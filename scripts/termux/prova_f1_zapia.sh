#!/data/data/com.termux/files/usr/bin/bash
# prova_f1_zapia.sh (S20 F1): o PROPRIETÁRIO prova que a Zapia LÊ um comando validado do repositório privado `entrada`, CONFERE o hash contra o recibo, ENTREGA
# o texto a ele (dentro da conversa) e grava o recibo de volta, que este script confere por código. O comando e o recibo são SINTÉTICOS e entram à mão em
# `comandos/validados/` e `comandos/recibos/` (o fluxo só promove com a flag ligada; o recibo vai marcado SINTETICO_MANUAL e NÃO prova a promoção).
# Pré-requisito: a sonda de leitura já deu PROVADO (a Zapia lê e escreve em `entrada` com o token dela). Roda DENTRO do clone do repositório público.
# Usa só a SUA sessão do gh; nenhum token da Zapia passa por aqui. Não cria rotina, hook nem lembrete. Sem dado pessoal.
# Códigos de saída: 0 provado; 1 bloqueado; 2 divergência. Limites: NÃO prova rotina agendada nem notificação espontânea (ela só responde na conversa).
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1
ENTRADA="${F1_REPO:-Andraus35/ufms-meu-estudo-entrada}"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
NOME="f1-teste.json"
VAL="comandos/validados/$NOME"; REC="comandos/recibos/$NOME"; ENT="comandos/entregas/$NOME"
DIV=0
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
ok() { echo "  OK        $1"; }
div() { echo "  DIVERGE   $1"; DIV=1; }
gget() { local o; o="$(gh api "$@" 2>/dev/null)" || return 1; printf '%s' "$o"; }
for cmd in gh python base64; do command -v "$cmd" >/dev/null 2>&1 || falha "falta o comando $cmd."; done
[ -f "$RAIZ/scripts/zapia_f1_prep.py" ] || falha "rode dentro do clone do repositório público (falta scripts/zapia_f1_prep.py)."
gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes."
[ "$(gget "repos/$ENTRADA" --jq '.private' || true)" = "true" ] || falha "$ENTRADA não é privado ou não existe."
TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT
pergunta() { local r; printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"; read -r r || r=""; [ "$r" = "$1" ]; }
b64() { python -c 'import base64,sys;print(base64.b64encode(sys.stdin.buffer.read()).decode())'; }
sha_de() { gget "repos/$ENTRADA/contents/$1" --jq '.sha' || true; }
subir() { local c; c="$(b64 < "$2")"; gh api -X PUT "repos/$ENTRADA/contents/$1" -f message="teste F1 (sintetico)" -f content="$c" -f branch=main >/dev/null 2>&1 || falha "não consegui gravar $1 (sua sessão do gh precisa de escrita em $ENTRADA)."; }
apagar() { local s; s="$(sha_de "$1")"; [ -n "$s" ] || return 0
  gh api -X DELETE "repos/$ENTRADA/contents/$1" -f message="teste F1: limpeza" -f sha="$s" -f branch=main >/dev/null 2>&1 && ok "apagado $1" || echo "  AVISO     não apaguei $1"; }

echo "== 1. Pré-condições =="
for p in "$VAL" "$REC" "$ENT"; do [ -z "$(sha_de "$p")" ] || falha "já existe $p em $ENTRADA (resto de outro teste). Apague e rode de novo."; done
ok "entrada privado e sem resto de teste anterior."

echo "== 2. Gerar o comando SINTÉTICO (passa pelo validador da caixa) e o recibo =="
pergunta TESTAR "Gravar o par sintético ($VAL e $REC) em $ENTRADA?" || { echo "Nada foi feito."; exit 1; }
python "$RAIZ/scripts/zapia_f1_prep.py" preparar --saida "$TMP" >/dev/null || falha "o comando de teste não passou no validador da caixa."
subir "$VAL" "$TMP/validados/$NOME"
subir "$REC" "$TMP/recibos/$NOME"
HASH="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["hash_corpo"])' "$TMP/meta.json")"
ok "par gravado (hash ${HASH:0:12}...)."

BASE="https://api.github.com/repos/$ENTRADA/contents"
PROMPT="TESTE F1 DE ENTREGA, uma vez só, sem rotina, hook nem lembrete. Sua ferramenta HTTP aceita só comandos curl simples: UMA chamada por vez, sem \";\", \"&&\" nem pipes, e SÓ as flags -X, -H e -d (nada de -s, -S, -f, -L, -i, -o nem --fail-with-body). Aplique a credencial \"zapia token\" como antes (não mostre nem peça o valor). 1) GET $BASE/$VAL e GET $BASE/$REC, com -H \"Accept: application/vnd.github+json\"; decodifique o base64 de content. 2) Em Python, calcule o SHA-256 (UTF-8) de json.dumps(<comando>, sort_keys=True, separators=(\",\",\":\"), ensure_ascii=False) e compare com hash_corpo do recibo. Se diferir, pare e diga. 3) Confira: operation é enviar_mensagem, origin é coach ou tutor e issued_at tem menos de 24 h. 4) Me mostre aqui no chat, como notificação, exatamente: \"Coach (origem declarada): \" seguido do texto de params.texto. 5) PUT em $BASE/$ENT com -X PUT e -d do JSON {\"message\":\"entrega F1\",\"branch\":\"main\",\"content\":\"<base64 de {\\\"entrada_id\\\":\\\"$NOME\\\",\\\"hash_corpo\\\":\\\"<hash>\\\",\\\"status\\\":\\\"ENTREGUE\\\",\\\"entregue_em\\\":\\\"<UTC AAAA-MM-DDTHH:MM:SSZ>\\\",\\\"origem_declarada\\\":\\\"coach\\\"}>\"} (sem o texto da mensagem). 6) Se qualquer chamada for bloqueada ou falhar, pare e me diga o texto literal do erro e a lista de flags aceitas, sem token. Só esses arquivos."
echo
echo "== 3. Envie este texto à Zapia (na conversa dela, NÃO aqui no terminal) =="
echo
echo "$PROMPT"
echo
if command -v termux-clipboard-set >/dev/null 2>&1; then printf '%s' "$PROMPT" | termux-clipboard-set && echo "[copiado]"; fi
echo "A Zapia deve te mostrar a notificação no chat. Depois que ela terminar (ou der erro), volte aqui."
printf 'Tecle Enter quando a Zapia terminar: '
read -r _ || true

echo "== 4. Conferir o recibo de volta =="
E_B64="$(gget "repos/$ENTRADA/contents/$ENT" --jq '.content' || true)"
if [ -z "$E_B64" ]; then
  div "a Zapia não gravou $ENT; cole AQUI no chat o erro literal que ela deu"
else
  printf '%s' "$E_B64" | python -c 'import base64,sys;sys.stdout.buffer.write(base64.b64decode(sys.stdin.read()))' > "$TMP/entrega.json"
  if python "$RAIZ/scripts/zapia_f1_prep.py" conferir --entrega "$TMP/entrega.json" --meta "$TMP/meta.json" >/dev/null; then ok "o recibo de volta confere com o hash do comando (mesmo hash, ENTREGUE, só campos fixos)."
  else div "o recibo de volta NÃO confere com o hash do comando"; fi
fi
printf 'Você viu a notificação "Coach (origem declarada): ..." no chat da Zapia? Digite SIM ou NAO: '
read -r VIU || VIU=""
[ "$VIU" = "SIM" ] && ok "você confirmou ter visto a notificação (relato seu)." || div "você não confirmou a notificação no chat da Zapia"

echo "== 5. Limpeza =="
if pergunta LIMPAR "Apagar $VAL, $REC e $ENT de $ENTRADA?"; then apagar "$VAL"; apagar "$REC"; apagar "$ENT"; else echo "  Mantidos (apague antes de repetir o teste)."; fi
echo
if [ "$DIV" -eq 0 ]; then
  echo "RESULTADO: PROVADO. A Zapia leu o comando validado, conferiu o hash, entregou a mensagem e gravou o recibo de volta (par sintético manual)."
  echo "NÃO provado: promoção pelo fluxo (flag/PJ), rotina agendada e notificação espontânea. Próximo: a rotina da Zapia (exige a sua frase AUTORIZO)."
  exit 0
fi
echo "RESULTADO: NÃO PROVADO. Veja as linhas DIVERGE e cole AQUI no chat (não no terminal) o texto literal da Zapia."
exit 2
