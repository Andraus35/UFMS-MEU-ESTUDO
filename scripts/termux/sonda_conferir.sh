#!/data/data/com.termux/files/usr/bin/bash
# sonda_conferir.sh: confere a sonda JÁ feita (nonce.json no repositório privado `entrada`, resposta.json gravado pela Zapia). SÓ LEITURA até o
# LIMPAR final. Use depois que a Zapia terminar a sonda. Não usa token da Zapia. Saída: 0 provado; 1 bloqueado; 2 divergência.
set -eu
umask 077
ENTRADA="${SONDA_REPO:-Andraus35/ufms-meu-estudo-entrada}"
NONCE_PATH="sondas/nonce.json"; RESP_PATH="sondas/resposta.json"; DIV=0
ok() { echo "  OK        $1"; }
div() { echo "  DIVERGE   $1"; DIV=1; }
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
gget() { local o; o="$(gh api "$@" 2>/dev/null)" || return 1; printf '%s' "$o"; }
command -v gh >/dev/null 2>&1 && command -v python >/dev/null 2>&1 || falha "faltam gh e/ou python (rode antes o sonda_zapia_do_zero.sh)."
gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes."
campo() { printf '%s' "$1" | python -c 'import base64,json,sys
try:
    d=json.loads(base64.b64decode(sys.stdin.read()).decode()); print(d.get(sys.argv[1],"") if isinstance(d,dict) else "")
except Exception:
    print("")' "$2" 2>/dev/null || true; }
quando() { gget "repos/$ENTRADA/commits?path=$1&per_page=1" --jq '.[0].commit.committer.date' || true; }
apagar() { local s; s="$(gget "repos/$ENTRADA/contents/$1" --jq '.sha' || true)"; [ -n "$s" ] || return 0
  gh api -X DELETE "repos/$ENTRADA/contents/$1" -f message="sonda de leitura: limpeza" -f sha="$s" -f branch=main >/dev/null 2>&1 && ok "apagado $1" || echo "  AVISO     não apaguei $1"; }

N_B64="$(gget "repos/$ENTRADA/contents/$NONCE_PATH" --jq '.content' || true)"
[ -n "$N_B64" ] || falha "não existe $NONCE_PATH em $ENTRADA (rode o sonda_zapia_do_zero.sh)."
NONCE="$(campo "$N_B64" nonce)"; [ -n "$NONCE" ] || falha "$NONCE_PATH fora do formato."
R_B64="$(gget "repos/$ENTRADA/contents/$RESP_PATH" --jq '.content' || true)"
if [ -z "$R_B64" ]; then
  div "a Zapia ainda não gravou $RESP_PATH (leitura ou escrita não funcionou); cole aqui o erro literal que ela deu"
else
  LIDO="$(campo "$R_B64" nonce_lido)"
  if [ -z "$LIDO" ]; then div "$RESP_PATH fora do formato (campos nonce_lido e lido_em)"
  elif [ "$LIDO" = "$NONCE" ]; then ok "o valor lido é IGUAL ao nonce: a Zapia leu o arquivo privado."
  else div "o valor lido NÃO é o nonce (ela não leu o arquivo; pode ter inventado)"; fi
  A="$(quando "$NONCE_PATH")"; B="$(quando "$RESP_PATH")"
  if [ -n "$A" ] && [ -n "$B" ] && [ "$B" \> "$A" ]; then ok "a resposta é POSTERIOR ao nonce."; else div "não consegui provar que a resposta é posterior ao nonce"; fi
fi
printf 'Apagar os arquivos da sonda? Digite LIMPAR (Enter pula): '; read -r r || r=""
if [ "$r" = "LIMPAR" ]; then apagar "$NONCE_PATH"; apagar "$RESP_PATH"; else echo "  Mantidos."; fi
echo
[ "$DIV" -eq 0 ] && { echo "RESULTADO: PROVADO. A Zapia leu e gravou no repositório privado com o token dela."; exit 0; }
echo "RESULTADO: NÃO PROVADO. Veja as linhas DIVERGE e cole AQUI no chat (não no terminal) o erro literal da Zapia."; exit 2
