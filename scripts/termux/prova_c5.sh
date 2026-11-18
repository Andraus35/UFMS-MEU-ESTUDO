#!/data/data/com.termux/files/usr/bin/bash
# prova_c5.sh (tarefa C5 da S6): o PROPRIETÁRIO prova, no GitHub real e com a flag de escrita DESLIGADA, a primeira metade do desenho:
# o token "zapia token" grava UM arquivo sintético na fila de `entrada`, o fluxo roda (SHA do validador e hashes conferidos), o runner
# responde FLAG_DESLIGADA e o histórico `dados` NÃO muda. A segunda metade (promoção até `dados`) só existe com a flag ligada (C6).
# Roda no aparelho dele. O token entra por entrada OCULTA e vai por stdin ao curl (nunca em argumento, nunca na tela, nunca em arquivo).
# Pré-requisitos: C3 concluída; token "zapia token" já editado para só `entrada` (`bash ~/verifica_zapia_token.sh` sem DIVERGE).
# Uso: bash scripts/termux/prova_c5.sh        (precisa de gh logado, curl, python)
# Códigos de saída: 0 tudo conferido; 1 bloqueado; 2 há divergências listadas no fim.
# Limites: NÃO habilita a escrita de resultados; NÃO prova a promoção até `dados`; o arquivo é sintético (sem dado pessoal).
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1
ENTRADA="Andraus35/ufms-meu-estudo-entrada"
DADOS="Andraus35/ufms-meu-estudo-dados"
WF="promover.yml"
API="https://api.github.com"
DIV=0
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
div() { echo "  DIVERGE   $1"; DIV=$((DIV+1)); }
ok() { echo "  OK        $1"; }
for cmd in gh curl python base64; do command -v "$cmd" >/dev/null 2>&1 || falha "falta o comando $cmd."; done
gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes."
TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"; unset TOKEN' EXIT
pergunta() { local r; printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"; read -r r || r=""; [ "$r" = "$1" ]; }

echo "== 1. Pré-condições (leitura com a sua credencial) =="
[ "$(gh api "repos/$ENTRADA" --jq '.private' 2>/dev/null)" = "true" ] || falha "$ENTRADA não é privado ou não existe."
gh api "repos/$ENTRADA/contents/.github/workflows/$WF" --jq '.name' >/dev/null 2>&1 || falha "o fluxo $WF não está instalado em $ENTRADA (rode a C3)."
gh variable get FLUXO_SHA256 --repo "$ENTRADA" >/dev/null 2>&1 || falha "falta a variável FLUXO_SHA256 em $ENTRADA (rode a C3)."
gh api "repos/$ENTRADA/actions/secrets" --jq '.secrets[].name' 2>/dev/null | grep -qx 'DADOS_TOKEN' || falha "falta o segredo DADOS_TOKEN em $ENTRADA (rode a C3)."
echo "[ok] entrada privado, fluxo instalado, FLUXO_SHA256 e DADOS_TOKEN presentes."
DADOS_ANTES="$(gh api "repos/$DADOS/commits?per_page=1" --jq '.[0].sha' 2>&1 | head -c 120 || true)"
echo "[dados] ponto de partida: ${DADOS_ANTES:0:12}..."

echo "== 2. A Zapia (token \"zapia token\") grava UM arquivo sintético na fila =="
pergunta PROVAR "Gravar 1 arquivo sintético em fila/entradas de $ENTRADA com o token \"zapia token\"?" || { echo "Nada foi feito."; exit 1; }
printf 'Cole o token "zapia token" (nome no GitHub; só `entrada`; NÃO o zapia_dados) e tecle Enter (não aparece): '
read -rs TOKEN || TOKEN=""; echo
[ -n "$TOKEN" ] || falha "token vazio."
case "$TOKEN" in github_pat_*) ;; *) falha "não parece fine-grained (github_pat_...).";; esac
printf '%s' "$TOKEN" | LC_ALL=C grep -qE '^[!-~]{8,1024}$' || falha "o token tem caractere fora do padrão (espaço, quebra de linha ou invisível)."
NOME="c5-sintetica-$(date -u +%Y%m%dT%H%M%SZ).json"
CAMINHO="fila/entradas/$NOME"
CONTEUDO="$(printf '{"sintetico":true,"proposito":"C5","sem_dado_pessoal":true}' | base64 | tr -d '\n')"
CORPO="$(python - "$CONTEUDO" <<'PY'
import json, sys
print(json.dumps({"message": "C5: arquivo sintetico (sem dado pessoal)", "content": sys.argv[1], "branch": "main"}))
PY
)"
CODE="$(printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | curl -sS -K - -X PUT -o "$TMP/resp.json" -w '%{http_code}' \
  -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2022-11-28' -H 'Content-Type: application/json' \
  --data "$CORPO" "$API/repos/$ENTRADA/contents/$CAMINHO" 2>/dev/null || printf '000')"
unset TOKEN
[ "$CODE" = "201" ] || falha "a gravação sintética falhou (código $CODE); o token não grava em entrada. Nada mais foi feito."
SHA_COMMIT="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["commit"]["sha"])' "$TMP/resp.json" 2>/dev/null || true)"
[ -n "$SHA_COMMIT" ] || falha "gravou, mas não li o SHA do commit."
ok "arquivo $NOME gravado pelo token da Zapia (commit ${SHA_COMMIT:0:12})."

echo "== 3. O fluxo roda sobre esse commit (até 5 minutos) =="
RUN=""; STATUS=""; CONC=""
for _ in $(seq 1 "${C5_TENTATIVAS:-30}"); do
  LINHA="$(gh run list --repo "$ENTRADA" --workflow "$WF" --limit 10 --json databaseId,headSha,status,conclusion 2>/dev/null | \
    python -c 'import json,sys; sha=sys.argv[1]; r=[x for x in json.load(sys.stdin) if x["headSha"]==sha]; print((str(r[0]["databaseId"])+" "+str(r[0]["status"])+" "+str(r[0]["conclusion"])) if r else "")' "$SHA_COMMIT" 2>/dev/null || true)"
  if [ -n "$LINHA" ]; then set -- $LINHA; RUN="${1:-}"; STATUS="${2:-}"; CONC="${3:-}"; [ "$STATUS" = "completed" ] && break; fi
  sleep "${C5_INTERVALO:-10}"
done
[ -n "$RUN" ] || div "nenhuma execução do fluxo apareceu para o commit (o gatilho não disparou)"
if [ -n "$RUN" ]; then
  if [ "$STATUS" = "completed" ] && [ "$CONC" = "success" ]; then ok "fluxo concluído com sucesso (execução $RUN): SHA e hashes do validador conferidos."
  else div "fluxo não terminou em sucesso (status $STATUS, conclusão $CONC, execução $RUN)"; fi
  if gh run view "$RUN" --repo "$ENTRADA" --log 2>/dev/null | grep -q 'FLAG_DESLIGADA'; then ok "o runner respondeu FLAG_DESLIGADA (nada promovido)."
  else div "o log não mostra FLAG_DESLIGADA (não consegui provar que o runner parou na flag)"; fi
fi

echo "== 4. O histórico \`dados\` não mudou =="
DADOS_DEPOIS="$(gh api "repos/$DADOS/commits?per_page=1" --jq '.[0].sha' 2>&1 | head -c 120 || true)"
if [ "$DADOS_ANTES" = "$DADOS_DEPOIS" ]; then ok "dados idêntico antes e depois."; else div "dados mudou (antes ${DADOS_ANTES:0:12}, depois ${DADOS_DEPOIS:0:12})"; fi

echo "== 5. Limpeza do arquivo sintético =="
if pergunta LIMPAR "Apagar $CAMINHO de $ENTRADA (um novo push, que dispara o fluxo de novo)?"; then
  SHA_ARQ="$(gh api "repos/$ENTRADA/contents/$CAMINHO" --jq '.sha' 2>/dev/null || true)"
  if [ -n "$SHA_ARQ" ] && gh api -X DELETE "repos/$ENTRADA/contents/$CAMINHO" -f message="C5: remove arquivo sintetico" -f sha="$SHA_ARQ" -f branch=main >/dev/null 2>&1; then ok "arquivo sintético removido."
  else div "não consegui remover $CAMINHO (apague pela página do GitHub)"; fi
else echo "  (mantido na fila: com a flag desligada nada o consome)"; fi

echo "== Resumo =="
echo "A escrita de resultados continua DESABILITADA (personal_results_writes_enabled=false); esta prova NÃO cobre a promoção até dados (C6)."
if [ "$DIV" -eq 0 ]; then echo "RESULTADO: primeira metade da C5 conferida."; exit 0; fi
echo "RESULTADO: $DIV divergência(s); não avance para a C6." >&2; exit 2
