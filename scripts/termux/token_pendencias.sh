#!/data/data/com.termux/files/usr/bin/bash
# token_pendencias.sh: resolve, em ordem, as pendências do token zapia_dados (PR-010, S7-R4). Termux, SEM segredo.
# Este script NUNCA lê nem imprime o token: quem o pede (em modo oculto) é o verificador do projeto.
# O que ele automatiza: atualizar o clone; conferir o repositório privado (privado, forks, colaboradores);
# abrir a página do token; rodar o verificador; ler o resultado e dizer o que fazer. O que NÃO dá para
# automatizar: mudar a permissão Contents do token (o GitHub só permite na página dele).
set -u
PRIV="Andraus35/ufms-meu-estudo-dados"
CLONE="${UFMS_DIR:-$HOME/UFMS-MEU-ESTUDO}"
PAGINA="https://github.com/settings/personal-access-tokens"
LOG="$(mktemp 2>/dev/null || echo "$HOME/.tok_pend_$$")"; chmod 600 "$LOG" 2>/dev/null
cleanup() { rm -f "$LOG"; unset TOKEN; }
trap cleanup EXIT
ok()  { echo "  [OK] $*"; }
bad() { echo "  [ATENÇÃO] $*"; PEND=$((PEND+1)); }
PEND=0

echo "== Passo 1: atualizar o clone (traz o verificador corrigido) =="
UFMS=""
for c in "$CLONE/scripts/termux/ufms.sh" "$HOME/ufms.sh"; do [ -f "$c" ] && { UFMS="$c"; break; }; done
if [ -z "$UFMS" ]; then echo "Não achei o ufms.sh. Rode antes o 'preparar' do projeto e tente de novo."; exit 1; fi
bash "$UFMS" atualizar || { echo "Falha ao atualizar. Resolva a mensagem acima e rode de novo."; exit 1; }
[ -f "$CLONE/scripts/termux/ufms.sh" ] && UFMS="$CLONE/scripts/termux/ufms.sh"
ok "clone atualizado ($(git -C "$CLONE" rev-parse --short HEAD 2>/dev/null))"

echo
echo "== Passo 2: repositório privado de dados =="
if ! command -v gh >/dev/null 2>&1 || ! gh auth status >/dev/null 2>&1; then
  echo "  gh ausente ou sem login: pulo esta conferência (rode 'gh auth login' para fazê-la)."
else
  INFO="$(gh api "repos/$PRIV" --jq '[.private,.fork,((.allow_forking // "desconhecido")|tostring),.forks_count]|@tsv' 2>/dev/null)"
  if [ -z "$INFO" ]; then bad "não consegui ler $PRIV (erro de rede ou permissão)"
  else
    set -- $INFO
    [ "${1:-}" = "true" ] && ok "repositório PRIVADO (private=true)" || bad "private NÃO é true (valor: ${1:-?}). NÃO grave nada nele."
    [ "${2:-}" = "false" ] && ok "não é um fork" || bad "o repositório é um fork (valor: ${2:-?})"
    case "${3:-}" in
      false) ok "forks DESABILITADOS (allow_forking=false)";;
      true)  bad "forks permitidos: desabilite em Settings > General > Features (desmarque 'Allow forking'), pela S7-R8";;
      *)     echo "  [aviso] allow_forking: ${3:-?}; confira em Settings > General do repositório";;
    esac
    [ "${4:-0}" = "0" ] && ok "nenhum fork existente" || bad "existem ${4:-?} fork(s): apague-os antes de gravar"
  fi
  COLAB="$(gh api "repos/$PRIV/collaborators" --jq 'length' 2>/dev/null)"
  if [ -z "$COLAB" ]; then echo "  [aviso] não consegui listar colaboradores"
  elif [ "$COLAB" = "1" ]; then ok "só 1 colaborador (você)"
  else bad "colaboradores: $COLAB (o esperado é 1, você)"; fi
fi

echo
echo "== Passo 3: ajustar o token zapia_dados no GitHub (só você consegue) =="
cat <<'TXT'
  Na página do token:
   1. Abra o token zapia_dados e toque em Edit (ou no Edit de 'Access on').
   2. Em Repository permissions, mude CONTENTS para "Read and write".
      Metadata continua só leitura. NENHUMA outra permissão (sem Issues, Pull requests,
      Actions, Workflows nem Administration).
   3. Repository access: só 'Andraus35/ufms-meu-estudo-dados'.
   4. Expiração: 30 dias (hoje a do token é 16/12/2026; renove antes de vencer).
   5. Salve com Update. NÃO precisa de Regenerate token.
TXT
command -v termux-open-url >/dev/null 2>&1 && termux-open-url "$PAGINA" >/dev/null 2>&1 && echo "  (abri a página do token no navegador)" || echo "  Página: $PAGINA"
printf '  Quando tiver salvo, aperte ENTER para conferir... '; read -r _ || true

echo
echo "== Passo 4: conferir o token com o verificador do projeto =="
echo "  O verificador vai pedir o token em modo OCULTO (nada aparece ao colar). Cole e dê ENTER."
echo "  Se o token só aparece uma vez no GitHub (regeneração), copie-o agora."
bash "$UFMS" token privado 2>&1 | tee "$LOG"
RES="$(grep -E '^RESULTADO:' "$LOG" | tail -1)"

echo
echo "== Passo 5: o que fazer agora =="
case "$RES" in
  *CONFERE*)
    ok "$RES"
    echo "  Pendência do token RESOLVIDA. Próximos passos:"
    echo "   - Guarde o token SÓ no gerenciador de senhas ou no formulário seguro da Zapia; nunca no chat, em arquivo ou commit."
    echo "   - O cadastro na Zapia só é necessário na prova real de escrita (W5), depois que a rotina de escrita existir."
    VAL="$(grep -i 'Validade' "$LOG" | head -1 | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}')"
    echo "   - Renove o token antes de ${VAL:-o vencimento}."
    ;;
  *DIVERGE*)
    bad "$RES"
    echo "  O que corrigir, pelo que o verificador disse:"
    grep -q "SEM expira" "$LOG"          && echo "   - Token sem validade: crie/edite com expiração (30 dias)."
    grep -q "não é fine-grained" "$LOG"  && echo "   - Use um token FINE-GRAINED (github_pat_), não o clássico."
    grep -q "alcança o repositório PRIVADO" "$LOG" && echo "   - O token alcança outro repositório PRIVADO: reduza 'Repository access' só ao ufms-meu-estudo-dados."
    grep -qE "Gravar arquivo.*(DIVERGE|NÃO)" "$LOG" && echo "   - Gravar arquivo no repositório de dados deve ser PODE: Contents precisa ser Read and write."
    grep -qE "DIVERGE \(esperado NAO\)" "$LOG" && echo "   - O token CONSEGUE escrever onde não deve: reduza o acesso do token e confira de novo."
    echo "   Depois de corrigir na página do token, rode este script de novo."
    ;;
  *) bad "não encontrei a linha RESULTADO (o verificador não terminou). Rode de novo."; ;;
esac
echo
echo "Resumo: $PEND ponto(s) de atenção. Nada foi gravado em lugar nenhum; o token não foi lido por este script."
[ "$PEND" -eq 0 ] && [ "${RES#*CONFERE}" != "$RES" ]
