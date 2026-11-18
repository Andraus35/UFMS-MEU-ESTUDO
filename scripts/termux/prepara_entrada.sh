#!/data/data/com.termux/files/usr/bin/bash
# prepara_entrada.sh (tarefa C3 da S6): o PROPRIETÁRIO prepara o repositório privado `ufms-meu-estudo-entrada` e o fluxo que
# promove a fila ao histórico `ufms-meu-estudo-dados`. Roda no aparelho dele, com a credencial dele no `gh` (gh auth login).
# Nenhuma credencial passa por este script, pelo modelo nem pela Zapia; o token do fluxo entra por entrada OCULTA e vai por
# stdin ao `gh secret set` (nunca em argumento, nunca na tela, nunca em arquivo).
#
# Uso:  bash scripts/termux/prepara_entrada.sh            (dentro do clone, atualizado e limpo; precisa de gh, python, base64, sha256sum)
#       bash scripts/termux/prepara_entrada.sh sondar     (só a sonda opcional do token da Zapia; precisa de curl)
# Etapas, cada ESCRITA pede uma frase e é conferida por leitura de volta:
#   1 CRIAR       cria `entrada` como PRIVADO, se não existir (P1: só segue com private=true por leitura autenticada)
#   2 CONFIGURAR  forks desabilitados (tenta), nenhum colaborador nem convite, ações limitadas e permissão padrão só de leitura
#   3 (token)     guarda o segredo DADOS_TOKEN (o token `zapia_dados`, que passa a ser a credencial do fluxo) em `entrada`
#   4 INSTALAR    instala o fluxo com o SHA do validador FIXADO (o HEAD do seu clone, igual ao da `main` pública) e grava a
#                 variável FLUXO_SHA256 (hash do fluxo instalado) que o próprio fluxo confere antes de promover
# Garantias: destinos fixos (P2), nunca o repositório público; não sobrescreve segredo nem fluxo sem a frase própria; o fluxo
# instalado passa antes pelo teste estático (`promotion_workflow_check.py --arquivo ... --instanciado`); falha de leitura BLOQUEIA.
# Limites: NÃO habilita a escrita de resultados (personal_results_writes_enabled continua false: PR próprio com aprovação) e
# NÃO prova o fluxo de ponta a ponta (isso é a C5). Trocar o SHA fixado é ato seu, depois de revisar o PR no público.
# Códigos de saída: 0 tudo conferido; 1 bloqueado (nada além do já dito foi feito); 2 há pendências listadas no fim.
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1  # o Python não deixa __pycache__ no clone (a árvore precisa continuar limpa)

PUBLIC_REPO="Andraus35/UFMS-MEU-ESTUDO"
ENTRADA="Andraus35/ufms-meu-estudo-entrada"
DADOS="Andraus35/ufms-meu-estudo-dados"
WF_PATH=".github/workflows/promover.yml"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
MODEL="$ROOT/config/modelos_fluxo/promover.yml"
CHECK="$ROOT/scripts/promotion_workflow_check.py"
GATE="$ROOT/scripts/promotion_gate.py"
API="https://api.github.com"
PEND=0
PEND_LISTA=""

minus() { printf '%s' "$1" | tr 'A-Z' 'a-z'; }
pend() { PEND=$((PEND+1)); PEND_LISTA="$PEND_LISTA
 - $1"; }
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }

for cmd in gh python base64 sha256sum git; do
  command -v "$cmd" >/dev/null 2>&1 || falha "falta o comando $cmd (pkg install gh python coreutils git)."
done
[ -f "$MODEL" ] && [ -f "$CHECK" ] && [ -f "$GATE" ] || falha "rode dentro do clone do repositório (faltam arquivos do fluxo)."
for r in "$ENTRADA" "$DADOS"; do
  [ "$(minus "$r")" != "$(minus "$PUBLIC_REPO")" ] || falha "P2: o destino não pode ser o repositório público."
done
[ "$(minus "$ENTRADA")" != "$(minus "$DADOS")" ] || falha "P2: entrada e dados devem ser repositórios diferentes."

# ---------------------------------------------------------------------------------------------------------------- sonda
sondar() {
  command -v curl >/dev/null 2>&1 || falha "falta o curl (pkg install curl)."
  printf 'Cole o token "zapia token" (nome no GitHub; editado para valer SÓ para `entrada`; NÃO o zapia_dados) e tecle Enter (não aparece na tela): '
  read -rs TOKEN || TOKEN=""
  echo
  [ -n "$TOKEN" ] || falha "token vazio."
  trap 'unset TOKEN' EXIT
  DIV=0
  # corpo vazio: a autorização é conferida ANTES da validação; 422 = tem permissão (nada é criado), 401/403/404 = não tem.
  sonda() {  # METODO CAMINHO ESPERADO(PODE|NAO) DESCRIÇÃO
    local code real
    code="$(printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | curl -sS -K - -X "$1" -o /dev/null -w '%{http_code}' \
      -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2022-11-28' -H 'Content-Type: application/json' \
      --data '{}' "$API$2" 2>/dev/null || printf '000')"
    case "$code" in 422) real=PODE;; 401|403|404) real=NAO;; *) real=OUTRO;; esac
    if [ "$real" = "$3" ]; then echo "  OK        $4 (código $code)"; else echo "  DIVERGE   $4 (esperado $3, código $code)"; DIV=$((DIV+1)); fi
  }
  echo "Sondas (corpo vazio; nada é criado):"
  sonda PUT "/repos/$ENTRADA/contents/zz-sonda.txt" PODE "gravar arquivo na fila (entrada)"
  sonda PUT "/repos/$DADOS/contents/zz-sonda.txt" NAO "gravar DIRETO no histórico (dados)"
  sonda PUT "/repos/$ENTRADA/contents/.github/workflows/zz-sonda.yml" NAO "mexer no fluxo (sem a permissão Workflows)"
  sonda PUT "/repos/$PUBLIC_REPO/contents/zz-sonda.txt" NAO "gravar no repositório público"
  if [ "$DIV" -eq 0 ]; then echo "RESULTADO: o token tem só o alcance esperado."; exit 0; fi
  echo "RESULTADO: $DIV divergência(s): troque o token por um de escopo menor antes da C5." >&2; exit 2
}
if [ "${1:-}" = "sondar" ]; then sondar; fi

gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes (a credencial fica só no seu aparelho)."
TMP="$(mktemp -d)"; chmod 700 "$TMP"
trap 'rm -rf "$TMP"; unset TOKEN' EXIT

# leitura: imprime o valor e devolve 0; 2 se não existe (404); 1 em qualquer outro erro.
ler() {
  local out
  if out="$(gh api "$@" 2>&1)"; then printf '%s' "$out"; return 0; fi
  case "$out" in *404*|*"Not Found"*) return 2;; *) return 1;; esac
}
privado() {  # REPO -> 0 se private=true confirmado por leitura autenticada; 2 se não existe; 1 se a leitura falhou; 3 se não é privado
  local v rc=0
  v="$(ler "repos/$1" --jq '.private')" || rc=$?  # sem alternar o `set -e` aqui dentro: o chamador decide o que fazer com o código
  [ "$rc" -eq 0 ] || return "$rc"
  [ "$v" = "true" ] || return 3
  return 0
}
pergunta() {  # FRASE TEXTO -> 0 se digitou a frase
  local resp
  printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"
  read -r resp || resp=""
  [ "$resp" = "$1" ]
}

echo "== 1. Repositórios (P1: leitura autenticada com private=true) =="
set +e; privado "$DADOS"; RC=$?; set -e
case "$RC" in
  0) echo "[dados] existe e é privado.";;
  2) falha "$DADOS não existe; ele foi criado antes (cria_repo_privado.sh). Nada foi feito.";;
  3) falha "P1: $DADOS NÃO é privado. Nada foi feito.";;
  *) falha "não consegui ler $DADOS. Nada foi feito.";;
esac
set +e; privado "$ENTRADA"; RC=$?; set -e
case "$RC" in
  0) echo "[entrada] já existe e é privado.";;
  2) if pergunta CRIAR "O repositório $ENTRADA não existe; criá-lo como PRIVADO?"; then
       gh repo create "$ENTRADA" --private --description "Fila de dados e comandos (privado)" >/dev/null
       echo "[entrada] criado."
     else falha "nada foi criado."; fi;;
  3) falha "P1: $ENTRADA existe e NÃO é privado. Nada foi gravado.";;
  *) falha "não consegui ler $ENTRADA (erro que não é 'não existe'). Nada foi feito.";;
esac
set +e; privado "$ENTRADA"; RC=$?; set -e
[ "$RC" -eq 0 ] || falha "P1: não confirmei private=true de $ENTRADA por leitura autenticada. Nada foi gravado."
echo "[P1] private=true confirmado nos dois repositórios."

echo "== 2. Configuração (forks, colaboradores, ações) =="
set +e; AA="$(ler "repos/$ENTRADA/actions/permissions" --jq '.allowed_actions')"
DW="$(ler "repos/$ENTRADA/actions/permissions/workflow" --jq '.default_workflow_permissions')"; set -e
if [ "$AA" = "local_only" ] && [ "$DW" = "read" ]; then
  echo "[ações] já limitadas às locais deste repositório (nenhuma de terceiros) e permissão padrão só de leitura; nada a configurar."
elif pergunta CONFIGURAR "Aplicar: forks desabilitados (se o GitHub aceitar) e ações limitadas em $ENTRADA?"; then
  for r in "$ENTRADA" "$DADOS"; do gh api -X PATCH "repos/$r" -F allow_forking=false >/dev/null 2>&1 \
    || echo "  (o GitHub não aceitou desabilitar forks em $r; conto com 'nenhum colaborador' e forks_count=0)"; done
  # `local_only` (só ações e fluxos do próprio repositório): o GitHub recusa `selected` com tudo desligado (409, rodada real de 18/11/2026)
  gh api -X PUT "repos/$ENTRADA/actions/permissions" -F enabled=true -f allowed_actions=local_only >/dev/null
  gh api -X PUT "repos/$ENTRADA/actions/permissions/workflow" -f default_workflow_permissions=read \
    -F can_approve_pull_request_reviews=false >/dev/null
else
  pend "configuração (forks e ações) NÃO aplicada"
fi
for r in "$ENTRADA" "$DADOS"; do
  set +e; FORK="$(ler "repos/$r" --jq '.fork')"; FC="$(ler "repos/$r" --jq '.forks_count')"
  COL="$(ler "repos/$r/collaborators" --jq 'length')"; CRC=$?
  INV="$(ler "repos/$r/invitations" --jq 'length')"; IRC=$?; set -e
  { [ "$FORK" = "false" ] && [ "$FC" = "0" ]; } || falha "$r: é um fork ou tem forks (fork=$FORK, forks_count=$FC)."
  [ "$CRC" -eq 0 ] && [ "$COL" = "1" ] || falha "$r: colaboradores=${COL:-?} (esperado só você, 1; leitura indisponível também bloqueia)."
  [ "$IRC" -eq 0 ] && [ "$INV" = "0" ] || falha "$r: há convites pendentes ou a leitura falhou (convites=${INV:-?})."
  echo "[$r] fork=false, forks_count=0, colaboradores=1, convites=0."
done
set +e; AA="$(ler "repos/$ENTRADA/actions/permissions" --jq '.allowed_actions')"
DW="$(ler "repos/$ENTRADA/actions/permissions/workflow" --jq '.default_workflow_permissions')"; set -e
if [ "$AA" = "local_only" ] && [ "$DW" = "read" ]; then
  echo "[ações] limitadas às locais deste repositório (nenhuma de terceiros) e permissão padrão só de leitura."
else
  pend "ações de $ENTRADA não conferem (allowed_actions=${AA:-?}, default_workflow_permissions=${DW:-?})"
fi

echo "== 3. Segredo do fluxo (DADOS_TOKEN em $ENTRADA) =="
set +e; NOMES="$(gh api "repos/$ENTRADA/actions/secrets" --jq '.secrets[].name' 2>"$TMP/err_segredos")"; SRC=$?; set -e
[ "$SRC" -eq 0 ] || falha "não consegui listar os segredos de $ENTRADA ($(head -c 200 "$TMP/err_segredos" | tr '\n' ' ')). Nada foi gravado."
TEM=0; printf '%s\n' "$NOMES" | grep -qx 'DADOS_TOKEN' && TEM=1
if [ "$TEM" -eq 1 ] && [ "${SUBSTITUIR_SEGREDO:-}" != "1" ]; then
  echo "[segredo] DADOS_TOKEN já existe; mantido (para trocar: SUBSTITUIR_SEGREDO=1 bash $0)."
else
  printf 'Cole o token "zapia_dados" (nome no GitHub; escopo só de `dados`; NÃO o zapia token) e tecle Enter (não aparece; vazio pula): '
  read -rs TOKEN || TOKEN=""
  echo
  if [ -z "$TOKEN" ]; then
    pend "segredo DADOS_TOKEN NÃO guardado (o fluxo não terá a credencial do histórico)"
  else
    case "$TOKEN" in
      github_pat_*) ;;
      *) unset TOKEN; falha "o token não parece fine-grained (github_pat_...). Nada foi gravado.";;
    esac
    printf '%s' "$TOKEN" | gh secret set DADOS_TOKEN --repo "$ENTRADA" >/dev/null
    unset TOKEN
    set +e; NOMES="$(gh api "repos/$ENTRADA/actions/secrets" --jq '.secrets[].name' 2>"$TMP/err_segredos")"; set -e
    printf '%s\n' "$NOMES" | grep -qx 'DADOS_TOKEN' || falha "o segredo não aparece na leitura de volta."
    echo "[segredo] DADOS_TOKEN guardado e visível na lista (o valor não é legível, por desenho)."
  fi
fi

echo "== 4. Fluxo com o SHA do validador fixado =="
[ -z "$(git -C "$ROOT" status --porcelain --untracked-files=no)" ] || falha "o clone tem arquivos rastreados alterados; o SHA fixado precisa ser de um commit revisado (arquivos novos não rastreados não contam). Limpe e tente de novo."
HEAD_SHA="$(git -C "$ROOT" rev-parse HEAD)"
set +e; MAIN_SHA="$(ler "repos/$PUBLIC_REPO/commits/main" --jq '.sha')"; MRC=$?; set -e
[ "$MRC" -eq 0 ] || falha "não consegui ler a main pública."
[ "$HEAD_SHA" = "$MAIN_SHA" ] || falha "o seu clone ($HEAD_SHA) não é a main pública ($MAIN_SHA): rode git pull. O SHA fixado é o da main revisada."
GATE_HASH="$(sha256sum "$GATE" | cut -d' ' -f1)"
python - "$MODEL" "$TMP/promover.yml" "$HEAD_SHA" "$GATE_HASH" <<'PY'
import sys
modelo, saida, sha, gate = sys.argv[1:5]
t = open(modelo, encoding="utf-8").read()
for marcador, valor in (("__VALIDADOR_SHA__", sha), ("__VALIDADOR_GATE_SHA256__", gate)):
    if t.count(marcador) != 1:
        sys.exit("o modelo não tem o marcador %s exatamente uma vez" % marcador)
    t = t.replace(marcador, valor)
open(saida, "w", encoding="utf-8", newline="\n").write(t)
PY
python "$CHECK" --check --instanciado --arquivo "$TMP/promover.yml" >/dev/null \
  || falha "o fluxo gerado não passou no teste estático (promotion_workflow_check). Nada foi instalado."
LOCAL_HASH="$(sha256sum "$TMP/promover.yml" | cut -d' ' -f1)"
echo "[fluxo] gerado para o SHA ${HEAD_SHA:0:12}, hash ${LOCAL_HASH:0:12}; passou no teste estático."

set +e; REMOTE_SHA="$(ler "repos/$ENTRADA/contents/$WF_PATH" --jq '.sha')"; RRC=$?; set -e
B64="$(base64 < "$TMP/promover.yml" | tr -d '\n')"
instalar=0
if [ "$RRC" -eq 2 ]; then
  pergunta INSTALAR "Instalar o fluxo em $ENTRADA com o SHA fixado ${HEAD_SHA:0:12}?" && instalar=1
elif [ "$RRC" -eq 0 ]; then
  REMOTE_HASH="$(ler "repos/$ENTRADA/contents/$WF_PATH" --jq '.content' | base64 -d 2>/dev/null | sha256sum | cut -d' ' -f1)"
  if [ "$REMOTE_HASH" = "$LOCAL_HASH" ]; then echo "[fluxo] já instalado e idêntico."
  else
    echo "[fluxo] já existe e é DIFERENTE (instalado ${REMOTE_HASH:0:12}, novo ${LOCAL_HASH:0:12})."
    pergunta ATUALIZAR "Trocar o SHA fixado/o fluxo? (ato seu, depois de revisar o PR no público)" && instalar=2
  fi
else
  falha "não consegui ler o fluxo de $ENTRADA. Nada foi gravado."
fi
if [ "$instalar" -eq 1 ]; then
  gh api -X PUT "repos/$ENTRADA/contents/$WF_PATH" -f message="Instala o fluxo de promoção (SHA ${HEAD_SHA:0:12})" -f content="$B64" >/dev/null
elif [ "$instalar" -eq 2 ]; then
  gh api -X PUT "repos/$ENTRADA/contents/$WF_PATH" -f message="Atualiza o fluxo de promoção (SHA ${HEAD_SHA:0:12})" -f content="$B64" \
    -f sha="$REMOTE_SHA" >/dev/null
elif [ "$RRC" -eq 2 ]; then
  pend "fluxo NÃO instalado"
fi
if [ "$instalar" -ne 0 ] || [ "$RRC" -eq 0 ]; then
  set +e; REMOTE_HASH="$(ler "repos/$ENTRADA/contents/$WF_PATH" --jq '.content' | base64 -d 2>/dev/null | sha256sum | cut -d' ' -f1)"; set -e
  if [ "$REMOTE_HASH" = "$LOCAL_HASH" ]; then
    VAR="$(gh variable get FLUXO_SHA256 --repo "$ENTRADA" 2>/dev/null)" || VAR=""
    [ "$VAR" = "$LOCAL_HASH" ] || gh variable set FLUXO_SHA256 --repo "$ENTRADA" --body "$LOCAL_HASH" >/dev/null  # só grava se mudou
    VAR="$(gh variable get FLUXO_SHA256 --repo "$ENTRADA" 2>/dev/null)" || VAR=""
    if [ "$VAR" = "$LOCAL_HASH" ]; then echo "[fluxo] instalado e conferido por leitura de volta; FLUXO_SHA256=${LOCAL_HASH:0:12}...";
    else pend "a variável FLUXO_SHA256 não confere na leitura de volta"; fi
  else
    pend "o fluxo instalado NÃO confere na leitura de volta"
  fi
fi

echo "== Resumo =="
echo "A escrita de resultados continua DESABILITADA (personal_results_writes_enabled=false); a prova real é a C5."
echo "Próximo: crie no GitHub o token da Zapia SÓ de $ENTRADA (Contents leitura e escrita, 30 dias, sem Workflows) e rode:"
echo "  bash scripts/termux/prepara_entrada.sh sondar"
if [ "$PEND" -gt 0 ]; then echo "PENDÊNCIAS ($PEND):$PEND_LISTA" >&2; exit 2; fi
echo "RESULTADO: tudo conferido por leitura de volta."
