#!/data/data/com.termux/files/usr/bin/bash
# sonda_zapia_do_zero.sh: do ZERO no Termux. (1) instala o que faltar (gh, python), (2) faz login no GitHub se preciso, (3) roda a SONDA que
# prova, no GitHub real, que a Zapia LÊ e ESCREVE no repositório privado `entrada` com o token dela.
# Prova que ela não consegue inventar: o script cria `sondas/nonce.json` com um valor aleatório; a Zapia (ferramenta HTTP + credencial
# "zapia token") lê o valor e grava `sondas/resposta.json`; o script confere se o valor lido é IGUAL e se a resposta é POSTERIOR ao nonce.
# Usa só a SUA sessão do gh (não pede nem mostra o token da Zapia; nenhum token passa por aqui). Não cria rotina, hook nem lembrete.
# Códigos de saída: 0 provado; 1 bloqueado/abortado; 2 divergência (a sonda NÃO provou).
# Limites: prova leitura e escrita pelo token em `entrada`; NÃO prova rotina agendada, notificação no celular nem pontualidade.
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1
ENTRADA="${SONDA_REPO:-Andraus35/ufms-meu-estudo-entrada}"
NONCE_PATH="sondas/nonce.json"
RESP_PATH="sondas/resposta.json"
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
ok() { echo "  OK        $1"; }
div() { echo "  DIVERGE   $1"; DIV=1; }
DIV=0
# o gh imprime o corpo do erro (ex.: {"message":"Not Found"}) na saída normal e sai com código != 0: só vale a saída se o código for 0
gget() { local o; o="$(gh api "$@" 2>/dev/null)" || return 1; printf '%s' "$o"; }
echo "== 0. Preparar o Termux =="
if command -v pkg >/dev/null 2>&1; then
  FALTA=""
  command -v gh >/dev/null 2>&1 || FALTA="$FALTA gh"
  command -v python >/dev/null 2>&1 || FALTA="$FALTA python"
  command -v base64 >/dev/null 2>&1 || FALTA="$FALTA coreutils"
  if [ -n "$FALTA" ]; then
    echo "Instalando:$FALTA (pode demorar)"
    pkg update -y >/dev/null 2>&1 || true
    # shellcheck disable=SC2086
    pkg install -y $FALTA || { echo "BLOQUEADO: não consegui instalar:$FALTA" >&2; exit 1; }
  fi
fi
for cmd in gh python base64; do command -v "$cmd" >/dev/null 2>&1 || { echo "BLOQUEADO: falta o comando $cmd." >&2; exit 1; }; done
if ! gh auth status >/dev/null 2>&1; then
  echo "Login no GitHub: siga as instruções (abra github.com/login/device no navegador e digite o código)."
  gh auth login -h github.com -p https -s repo -w || { echo "BLOQUEADO: login no GitHub não concluído." >&2; exit 1; }
fi
echo "[ok] gh, python e base64 prontos; GitHub logado."
[ "$(gget "repos/$ENTRADA" --jq '.private' || true)" = "true" ] || falha "$ENTRADA não é privado ou não existe."
TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT
pergunta() { local r; printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"; read -r r || r=""; [ "$r" = "$1" ]; }
b64() { python -c 'import base64,sys;print(base64.b64encode(sys.stdin.buffer.read()).decode())'; }
sha_de() { gget "repos/$ENTRADA/contents/$1" --jq '.sha' || true; }
apagar() {
  local s; s="$(sha_de "$1")"; [ -n "$s" ] || return 0
  gh api -X DELETE "repos/$ENTRADA/contents/$1" -f message="sonda de leitura: limpeza" -f sha="$s" -f branch=main >/dev/null 2>&1 \
    && ok "apagado $1" || echo "  AVISO     não consegui apagar $1 (apague no GitHub)"
}

echo "== 1. Pré-condições =="
[ -z "$(sha_de "$NONCE_PATH")" ] || falha "já existe $NONCE_PATH em $ENTRADA (resto de outra sonda). Apague $NONCE_PATH e $RESP_PATH e rode de novo."
[ -z "$(sha_de "$RESP_PATH")" ] || falha "já existe $RESP_PATH em $ENTRADA. Apague e rode de novo."
ok "entrada privado e sem resto de sonda anterior."

echo "== 2. Criar o valor aleatório (nonce) em $NONCE_PATH =="
pergunta SONDAR "Criar $NONCE_PATH (só um valor aleatório, sem dado pessoal) em $ENTRADA?" || { echo "Nada foi feito."; exit 1; }
NONCE="$(python -c 'import secrets;print(secrets.token_hex(16))')"
CONTEUDO="$(printf '{"nonce":"%s"}' "$NONCE" | b64)"
gh api -X PUT "repos/$ENTRADA/contents/$NONCE_PATH" -f message="sonda de leitura: nonce" -f content="$CONTEUDO" -f branch=main >/dev/null 2>&1 \
  || falha "não consegui criar $NONCE_PATH (sua sessão do gh precisa de escrita em $ENTRADA)."
NONCE_QUANDO="$(gget "repos/$ENTRADA/commits?path=$NONCE_PATH&per_page=1" --jq '.[0].commit.committer.date' || true)"
ok "nonce criado (${NONCE:0:6}...)."

PROMPT="SONDA DE LEITURA, uma vez só, sem rotina, hook nem lembrete. Sua ferramenta HTTP aceita só comandos curl simples: faça UMA chamada por vez, sem \";\", \"&&\" nem pipes, e use SÓ as flags -X, -H e -d (nada de -s, -S, -f, -L, -i, -o nem --fail-with-body). Aplique a credencial \"zapia token\" do mesmo jeito que sua ferramenta já a aplicava (não mostre nem peça o valor). Chamada 1: GET https://api.github.com/repos/$ENTRADA/contents/$NONCE_PATH com -H \"Accept: application/vnd.github+json\"; decodifique o base64 do campo content. Chamada 2: PUT em https://api.github.com/repos/$ENTRADA/contents/$RESP_PATH com -X PUT e -d de um JSON com os campos message (\"sonda de leitura\"), branch (\"main\") e content, onde content é o base64 do JSON com os campos nonce_lido (o valor que você leu, exato) e lido_em (UTC). Chamada 3: releia $RESP_PATH. Se alguma chamada for bloqueada, pare e me diga: (a) o texto literal do erro, (b) a lista literal de flags aceitas, se a ferramenta informar, e (c) em uma frase, como você referencia a credencial (sem o valor). Só esses dois arquivos."
echo
echo "== 3. Envie este texto à Zapia (copiado para a área de transferência, se o Termux permitir) =="
echo
echo "$PROMPT"
echo
if command -v termux-clipboard-set >/dev/null 2>&1; then printf '%s' "$PROMPT" | termux-clipboard-set && echo "[copiado]"; fi
printf 'Quando a Zapia disser que terminou (ou der erro), tecle Enter: '
read -r _ || true

echo "== 4. Conferir a resposta =="
RESP_B64="$(gget "repos/$ENTRADA/contents/$RESP_PATH" --jq '.content' || true)"
if [ -z "$RESP_B64" ]; then
  div "a Zapia não gravou $RESP_PATH (leitura ou escrita não funcionou); cole aqui o erro literal que ela deu"
else
  LIDO="$(printf '%s' "$RESP_B64" | python -c 'import base64,json,sys
try:
    d=json.loads(base64.b64decode(sys.stdin.read()).decode())
    print(d["nonce_lido"] if set(d)=={"nonce_lido","lido_em"} and isinstance(d["nonce_lido"],str) else "")
except Exception:
    print("")' 2>/dev/null || true)"
  if [ -z "$LIDO" ]; then div "$RESP_PATH existe, mas fora do formato pedido (campos nonce_lido e lido_em)"
  elif [ "$LIDO" = "$NONCE" ]; then ok "o valor lido é IGUAL ao nonce: a Zapia leu o arquivo privado."
  else div "o valor lido NÃO é o nonce (ela não leu o arquivo; pode ter inventado)"; fi
  RESP_QUANDO="$(gget "repos/$ENTRADA/commits?path=$RESP_PATH&per_page=1" --jq '.[0].commit.committer.date' || true)"
  if [ -n "$NONCE_QUANDO" ] && [ -n "$RESP_QUANDO" ] && [ "$RESP_QUANDO" \> "$NONCE_QUANDO" ]; then ok "a resposta é POSTERIOR ao nonce (escrita depois da leitura)."
  else div "não consegui provar que a resposta é posterior ao nonce"; fi
fi

echo "== 5. Limpeza =="
if pergunta LIMPAR "Apagar $NONCE_PATH e $RESP_PATH de $ENTRADA?"; then apagar "$NONCE_PATH"; apagar "$RESP_PATH"; else echo "  Mantidos (apague depois, antes de outra sonda)."; fi

echo
if [ "$DIV" -eq 0 ]; then
  echo "RESULTADO: PROVADO. A Zapia leu e gravou no repositório privado com o token dela (sem rotina, sem hook)."
  echo "Próximo passo: a rotina da Zapia (exige a sua frase AUTORIZO). Anexe esta saída (sem token) ao chat."
  exit 0
fi
echo "RESULTADO: NÃO PROVADO. Veja as linhas DIVERGE e cole aqui o erro literal que a Zapia deu."
exit 2
