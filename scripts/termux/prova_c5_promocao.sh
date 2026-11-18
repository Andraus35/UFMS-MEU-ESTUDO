#!/data/data/com.termux/files/usr/bin/bash
# prova_c5_promocao.sh (tarefa C5, segunda metade): o PROPRIETÁRIO prova, no GitHub real e COM A FLAG DO FLUXO LIGADA, que um evento
# SINTÉTICO entregue pela Zapia na fila de `entrada` é promovido pelo fluxo até o histórico `dados`, com a marca de teste no envelope.
# A primeira metade (prova_c5.sh) provou o gatilho, o pino do validador e o escopo do token com a flag desligada.
# Pré-condições (conferidas aqui, por leitura, e BLOQUEIAM se faltarem): a C6 ligou `storage.private_flow_promotion_enabled` no SHA que
# o fluxo fixa; o fluxo foi reinstalado com esse SHA (prepara_entrada.sh, etapa 4); o consentimento v4 existe em `dados`; token "zapia
# token" editado para só `entrada`. Janela curta (decisão do proprietário): ligar, provar e desligar a flag de novo por PR da C6.
# Roda no aparelho dele, dentro do clone, com `gh` logado, curl e python. O token entra por entrada OCULTA e vai por stdin ao curl.
# O evento promovido FICA no histórico (só de acréscimo; nunca se apaga `dados`): leva `sintetico: true` e as projeções o descartam.
# Códigos de saída: 0 tudo conferido; 1 bloqueado; 2 há divergências listadas no fim.
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1
PUBLIC="Andraus35/UFMS-MEU-ESTUDO"
ENTRADA="Andraus35/ufms-meu-estudo-entrada"
DADOS="Andraus35/ufms-meu-estudo-dados"
WF=".github/workflows/promover.yml"
API="https://api.github.com"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
DIV=0
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
div() { echo "  DIVERGE   $1"; DIV=$((DIV+1)); }
ok() { echo "  OK        $1"; }
for cmd in gh curl python base64; do command -v "$cmd" >/dev/null 2>&1 || falha "falta o comando $cmd."; done
[ -f "$ROOT/scripts/c5_entrada_sintetica.py" ] || falha "rode dentro do clone atualizado (falta scripts/c5_entrada_sintetica.py)."
gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes."
TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"; unset TOKEN' EXIT
pergunta() { local r; printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"; read -r r || r=""; [ "$r" = "$1" ]; }
b64d() { base64 -d 2>/dev/null; }

echo "== 1. Pré-condições (leitura com a sua credencial) =="
[ "$(gh api "repos/$ENTRADA" --jq '.private' 2>/dev/null)" = "true" ] || falha "$ENTRADA não é privado ou não existe."
[ "$(gh api "repos/$DADOS" --jq '.private' 2>/dev/null)" = "true" ] || falha "$DADOS não é privado ou não existe."
gh variable get FLUXO_SHA256 --repo "$ENTRADA" >/dev/null 2>&1 || falha "falta a variável FLUXO_SHA256 em $ENTRADA (rode a C3)."
gh api "repos/$ENTRADA/actions/secrets" --jq '.secrets[].name' 2>/dev/null | grep -qx 'DADOS_TOKEN' || falha "falta o segredo DADOS_TOKEN em $ENTRADA."
gh api "repos/$DADOS/contents/consent-v4.json" --jq '.sha' >/dev/null 2>&1 || falha "falta o consent-v4.json em $DADOS (rode: bash scripts/termux/ufms.sh consentir-v4)."
FLUXO="$(gh api "repos/$ENTRADA/contents/$WF" --jq '.content' 2>/dev/null | b64d || true)"
[ -n "$FLUXO" ] || falha "o fluxo $WF não está instalado em $ENTRADA (rode a C3)."
SHA_FIXADO="$(printf '%s\n' "$FLUXO" | sed -n 's/^  VALIDADOR_SHA: *//p' | head -1 | tr -d '[:space:]')"
case "$SHA_FIXADO" in [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) [ "${#SHA_FIXADO}" -eq 40 ] || falha "o SHA fixado no fluxo não tem 40 caracteres.";; *) falha "o fluxo não tem um SHA de validador fixado (marcador não trocado).";; esac
SETTINGS="$(gh api "repos/$PUBLIC/contents/settings.json?ref=$SHA_FIXADO" --jq '.content' 2>/dev/null | b64d || true)"
[ -n "$SETTINGS" ] || falha "não consegui ler o settings.json do SHA fixado (${SHA_FIXADO:0:12})."
printf '%s' "$SETTINGS" | python -c 'import json,sys; s=json.load(sys.stdin)["storage"]; sys.exit(0 if s.get("private_flow_promotion_enabled") is True else 1)' 2>/dev/null \
  || falha "a flag private_flow_promotion_enabled NÃO está ligada no SHA fixado pelo fluxo (${SHA_FIXADO:0:12}): falta a C6 e a reinstalação do fluxo com esse SHA."
printf '%s' "$SETTINGS" | python -c 'import json,sys; s=json.load(sys.stdin)["storage"]; sys.exit(0 if s.get("personal_results_writes_enabled") is False else 1)' 2>/dev/null \
  || falha "a flag personal_results_writes_enabled do público deveria seguir falsa neste SHA."
echo "[ok] fluxo instalado com o SHA ${SHA_FIXADO:0:12}; flag do fluxo ligada nele; v4 presente; segredo e variável presentes."

# a fila precisa estar VAZIA: entradas paradas de uma tentativa anterior seriam promovidas junto e quebrariam a contagem (+1)
FILA_PREVIA="$(gh api "repos/$ENTRADA/contents/fila/entradas" --jq 'length' 2>/dev/null || echo 0)"
case "$FILA_PREVIA" in ''|*[!0-9]*) FILA_PREVIA=0;; esac
[ "$FILA_PREVIA" -eq 0 ] || falha "há $FILA_PREVIA arquivo(s) parado(s) em fila/entradas de $ENTRADA (tentativa anterior). Apague-os pela página do GitHub antes de repetir a prova."
contar() { gh api "repos/$DADOS/git/trees/HEAD?recursive=1" --jq '[.tree[] | select(.type=="blob") | select(.path|startswith("eventos/"))] | length' 2>/dev/null || echo 0; }
cabeca() { gh api "repos/$DADOS/commits?per_page=1" --jq '.[0].sha' 2>/dev/null | head -c 64 || true; }
ANTES_N="$(contar)"; ANTES_H="$(cabeca)"
echo "[dados] antes: ${ANTES_N} evento(s); cabeça ${ANTES_H:0:12}..."

echo "== 2. A entrada sintética (marca sintetico=true; passa antes pelo mesmo esquema do portão) =="
python "$ROOT/scripts/c5_entrada_sintetica.py" --saida "$TMP/entrada.json" > "$TMP/saida.txt" || falha "não consegui montar a entrada sintética (veja a mensagem acima)."
NOME="$(sed -n 's/^NOME=//p' "$TMP/saida.txt")"; EVENTO="$(sed -n 's/^EVENTO=//p' "$TMP/saida.txt")"
[ -n "$NOME" ] && [ -n "$EVENTO" ] || falha "a montagem não devolveu nome e caminho do evento."
ok "entrada $NOME (evento previsto em $EVENTO)."

echo "== 3. A Zapia (token \"zapia token\") grava a entrada na fila =="
pergunta PROMOVER "Gravar 1 entrada SINTÉTICA em fila/entradas de $ENTRADA e deixar o fluxo promovê-la a $DADOS (fica no histórico, marcada como teste)?" || { echo "Nada foi feito."; exit 1; }
printf 'Cole o token "zapia token" (nome no GitHub; só `entrada`; NÃO o zapia_dados) e tecle Enter (não aparece): '
read -rs TOKEN || TOKEN=""; echo
[ -n "$TOKEN" ] || falha "token vazio."
case "$TOKEN" in github_pat_*) ;; *) falha "não parece fine-grained (github_pat_...).";; esac
printf '%s' "$TOKEN" | LC_ALL=C grep -qE '^[!-~]{8,255}$' || falha "o token tem caractere fora do padrão (espaço, quebra de linha ou invisível)."
CORPO="$(python - "$TMP/entrada.json" <<'PY'
import base64, json, sys
print(json.dumps({"message": "C5: entrada sintetica (teste, sem dado pessoal)", "branch": "main",
                  "content": base64.b64encode(open(sys.argv[1], "rb").read()).decode()}))
PY
)"
CODE="$(printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | curl -sS -K - -X PUT -o "$TMP/resp.json" -w '%{http_code}' \
  -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2022-11-28' -H 'Content-Type: application/json' \
  --data "$CORPO" "$API/repos/$ENTRADA/contents/fila/entradas/$NOME" 2>/dev/null || printf '000')"
unset TOKEN
[ "$CODE" = "201" ] || falha "a gravação da entrada falhou (código $CODE); o token não grava em entrada. Nada mais foi feito."
SHA_COMMIT="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["commit"]["sha"])' "$TMP/resp.json" 2>/dev/null || true)"
[ -n "$SHA_COMMIT" ] || falha "gravou, mas não li o SHA do commit."
ok "entrada gravada pelo token da Zapia (commit ${SHA_COMMIT:0:12})."

echo "== 4. O fluxo roda sobre esse commit (até 5 minutos) =="
RUN=""; STATUS=""; CONC=""
for _ in $(seq 1 "${C5_TENTATIVAS:-30}"); do
  LINHA="$(gh run list --repo "$ENTRADA" --workflow promover.yml --limit 10 --json databaseId,headSha,status,conclusion 2>/dev/null | \
    python -c 'import json,sys; sha=sys.argv[1]; r=[x for x in json.load(sys.stdin) if x["headSha"]==sha]; print((str(r[0]["databaseId"])+" "+str(r[0]["status"])+" "+str(r[0]["conclusion"])) if r else "")' "$SHA_COMMIT" 2>/dev/null || true)"
  if [ -n "$LINHA" ]; then set -- $LINHA; RUN="${1:-}"; STATUS="${2:-}"; CONC="${3:-}"; [ "$STATUS" = "completed" ] && break; fi
  sleep "${C5_INTERVALO:-10}"
done
[ -n "$RUN" ] || div "nenhuma execução do fluxo apareceu para o commit (o gatilho não disparou)"
if [ -n "$RUN" ]; then
  if [ "$STATUS" = "completed" ] && [ "$CONC" = "success" ]; then ok "fluxo concluído com sucesso (execução $RUN)."
  else div "fluxo não terminou em sucesso (status $STATUS, conclusão $CONC, execução $RUN)"; fi
  if gh run view "$RUN" --repo "$ENTRADA" --log 2>/dev/null | grep -q 'FLAG_DESLIGADA'; then div "o runner respondeu FLAG_DESLIGADA: a flag NÃO estava ligada no SHA que o fluxo usou"
  else ok "o runner NÃO parou na flag."; fi
fi

echo "== 5. O evento chegou ao histórico, marcado como teste =="
DEPOIS_N="$(contar)"
if [ "$DEPOIS_N" -eq $((ANTES_N + 1)) ] 2>/dev/null; then ok "dados ganhou exatamente 1 evento ($ANTES_N -> $DEPOIS_N)."; else div "contagem de eventos em dados inesperada (antes $ANTES_N, depois $DEPOIS_N; esperado +1)"; fi
ARQ="$(gh api "repos/$DADOS/contents/$EVENTO" --jq '.content' 2>/dev/null | b64d || true)"
if [ -z "$ARQ" ]; then div "o arquivo do evento $EVENTO não existe em dados"
else
  printf '%s' "$ARQ" | python -c '
import json, sys
d = json.load(sys.stdin); e = d["envelope"]
assert e.get("sintetico") is True, "sem a marca de teste"
assert e.get("escritor") == "fluxo", "escritor não é o fluxo"
assert e.get("entregue_por") == "zapia", "entregue_por não é a zapia"
assert d["evento"]["type"] == "caderno_recomendado", "tipo inesperado"
' 2>/dev/null && ok "evento em $EVENTO com envelope: sintetico=true, escritor=fluxo, entregue_por=zapia." || div "o evento existe, mas o envelope não tem a marca de teste, o escritor fluxo ou a entrega da zapia"
fi
DEPOIS_H="$(cabeca)"
[ -n "$DEPOIS_H" ] && [ "$DEPOIS_H" != "$ANTES_H" ] && ok "a cabeça de dados avançou (${DEPOIS_H:0:12}...)." || div "a cabeça de dados não avançou"

echo "== 6. A fila foi consumida e o recibo existe =="
if gh api "repos/$ENTRADA/contents/fila/entradas/$NOME" --jq '.sha' >/dev/null 2>&1; then div "a entrada ainda está na fila"; else ok "a entrada saiu da fila."; fi
if gh api "repos/$ENTRADA/contents/recibos/$NOME" --jq '.sha' >/dev/null 2>&1; then ok "recibo em recibos/$NOME."; else div "não achei o recibo em recibos/$NOME"; fi

echo "== Resumo =="
echo "O evento sintético permanece em $DADOS (histórico só de acréscimo), marcado como teste: as projeções o descartam."
echo "AGORA a flag do fluxo deve voltar a falsa (janela curta): PR próprio da C6, com a sua aprovação."
if [ "$DIV" -eq 0 ]; then echo "RESULTADO: segunda metade da C5 conferida."; exit 0; fi
echo "RESULTADO: $DIV divergência(s); desligue a flag do fluxo e não use o fluxo para resultado real." >&2; exit 2
