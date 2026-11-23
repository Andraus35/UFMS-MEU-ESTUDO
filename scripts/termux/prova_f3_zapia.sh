#!/data/data/com.termux/files/usr/bin/bash
# prova_f3_zapia.sh (ZAPIA-F3 e ZAPIA-CTX real, E29): o PROPRIETÁRIO prova, UMA vez e com par SINTÉTICO, (A) que o runner lê o `entrada` REAL como esperado (sonda
# somente leitura, ZAPIA-CTX) e (B) se uma rotina da Zapia consegue CRIAR outra (ZAPIA-F3): um poller de execução única lê um pedido `agendar_rotina`, cria a
# rotina FILHA e grava `comandos/criadas/`; a filha entrega o alvo. Subcomandos: preparar | conferir | limpar. Roda DENTRO do clone do repositório público,
# na revisão já enviada ao GitHub. Usa só a SUA sessão do gh; nenhum token da Zapia passa por aqui; nada de dado pessoal; não liga flag; não promove pelo fluxo.
# Códigos de saída: 0 provado/ok; 1 bloqueado; 2 divergência. Limites: autorrelato da Zapia (carimbo e id da rotina); só a captura da lista de rotinas do app
# separa rotina criada de entrega manual; não prova pontualidade em vários dias nem promoção pelo fluxo (PJ).
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1
ENTRADA="${F3_REPO:-Andraus35/ufms-meu-estudo-entrada}"
PUBLICO="${F3_PUBLICO:-Andraus35/UFMS-MEU-ESTUDO}"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
ESTADO="${F3_ESTADO:-$HOME/.ufms-f3-estado.json}"
ALVO="f3-alvo.json"; PEDIDO="f3-pedido.json"
ARQS="comandos/validados/$ALVO comandos/recibos/$ALVO comandos/validados/$PEDIDO comandos/recibos/$PEDIDO comandos/criadas/$PEDIDO comandos/entregas/$ALVO"
DIV=0
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
ok() { echo "  OK        $1"; }
div() { echo "  DIVERGE   $1"; DIV=1; }
gget() { local o; o="$(gh api "$@" 2>/dev/null)" || return 1; printf '%s' "$o"; }
pergunta() { local r; printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"; read -r r || r=""; [ "$r" = "$1" ]; }
b64() { python -c 'import base64,sys;print(base64.b64encode(sys.stdin.buffer.read()).decode())'; }
sha_de() { gget "repos/$ENTRADA/contents/$1" --jq '.sha' || true; }
subir() { local c; c="$(b64 < "$2")"; gh api -X PUT "repos/$ENTRADA/contents/$1" -f message="teste F3 (sintetico)" -f content="$c" -f branch=main >/dev/null 2>&1 || falha "não consegui gravar $1 (sua sessão do gh precisa de escrita em $ENTRADA)."; }
apagar() { local s; s="$(sha_de "$1")"; [ -n "$s" ] || return 0
  gh api -X DELETE "repos/$ENTRADA/contents/$1" -f message="teste F3: limpeza" -f sha="$s" -f branch=main >/dev/null 2>&1 && ok "apagado $1" || echo "  AVISO     não apaguei $1"; }
base() { for cmd in gh python base64; do command -v "$cmd" >/dev/null 2>&1 || falha "falta o comando $cmd."; done
  [ -f "$RAIZ/scripts/zapia_poller.py" ] || falha "rode dentro do clone do repositório público (falta scripts/zapia_poller.py)."
  gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes."
  [ "$(gget "repos/$ENTRADA" --jq '.private' || true)" = "true" ] || falha "$ENTRADA não é privado ou não existe."; }
sonda() { GH_TOKEN="$(gh auth token)" python "$RAIZ/scripts/ctx_leitura_real.py" "$ENTRADA" || true; }

usar="${1:-}"
case "$usar" in
preparar)
  base
  command -v git >/dev/null 2>&1 || falha "falta o comando git."
  echo "== 1. Pré-condições =="
  for p in $ARQS; do [ -z "$(sha_de "$p")" ] || falha "já existe $p em $ENTRADA (resto de outro teste). Rode: bash $0 limpar"; done
  ok "entrada privado e sem resto de teste anterior."
  REF="$(git -C "$RAIZ" rev-parse HEAD)"
  [ -z "$(git -C "$RAIZ" status --porcelain)" ] || falha "há alteração local não commitada; o poller lê o modelo no GitHub, num commit fixo."
  [ -n "$(gget "repos/$PUBLICO/commits/$REF" --jq '.sha' || true)" ] || falha "o commit $REF não está no GitHub ($PUBLICO). Envie o commit ao GitHub antes."
  ok "modelo filho fixado no commit $REF (enviado ao GitHub)."
  echo "== 2. Sonda real ANTES (somente leitura, ZAPIA-CTX) =="
  sonda
  POLLER="$(python -c 'from datetime import datetime,timedelta,timezone;print((datetime.now(timezone.utc)+timedelta(minutes=25)).strftime("%Y-%m-%dT%H:%M:00Z"))')"
  FILHA="$(python -c 'from datetime import datetime,timedelta,timezone;print((datetime.now(timezone.utc)+timedelta(minutes=105)).strftime("%Y-%m-%dT%H:%M:00Z"))')"
  echo "  Poller (execução única): $POLLER   Filha (criada pelo poller): $FILHA   (anote; o verificador usa estes valores)"
  pergunta TESTAR "Gravar o par sintético (alvo e pedido) em $ENTRADA?" || { echo "Nada foi feito."; exit 1; }
  TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT
  python "$RAIZ/scripts/zapia_poller.py" preparar --saida "$TMP" --agendado-filha "$FILHA" >/dev/null || falha "o pedido de teste não passou na caixa."
  for n in "$ALVO" "$PEDIDO"; do subir "comandos/validados/$n" "$TMP/validados/$n"; subir "comandos/recibos/$n" "$TMP/recibos/$n"; done
  ok "par sintético gravado (recibos SINTETICO_MANUAL; a promoção pelo fluxo NÃO é provada aqui)."
  echo "== 3. Sonda real DEPOIS (esperado: 2 validados, 2 recibos, 2 hashes promovidos, agendamentos_do_dia [coach]) =="
  sonda
  printf '{"poller":"%s","filha":"%s","ref":"%s"}\n' "$POLLER" "$FILHA" "$REF" > "$ESTADO"
  INSTR="$(python "$RAIZ/scripts/agendar_rotina.py" --poller --agendado "$POLLER" --ref "$REF" --repo "$ENTRADA")" || falha "não consegui montar a instrução do poller."
  PROMPT="TESTE F3, uma vez só: crie UMA rotina agendada NATIVA do app, de execução única, para $POLLER (UTC), com EXATAMENTE a instrução entre as marcas INICIO e FIM (não traduza, não resuma, não reescreva nenhum URL ou pasta; depois de salvar, leia a instrução salva de volta e me mostre). Não crie nenhuma outra rotina, hook ou lembrete agora. INICIO $INSTR FIM"
  echo; echo "== 4. Envie este texto à Zapia (na conversa dela, NÃO aqui no terminal) =="; echo; echo "$PROMPT"; echo
  if command -v termux-clipboard-set >/dev/null 2>&1; then printf '%s' "$PROMPT" | termux-clipboard-set && echo "[copiado]"; fi
  echo "Depois: (a) tire a captura da lista de rotinas do app com o poller e, DEPOIS do horário do poller, com a filha; (b) após a filha disparar ($FILHA), rode: bash $0 conferir"
  ;;
conferir)
  base
  [ -f "$ESTADO" ] || falha "não achei $ESTADO; rode 'preparar' antes."
  POLLER="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["poller"])' "$ESTADO")"
  FILHA="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["filha"])' "$ESTADO")"
  echo "== 1. Sonda real (somente leitura) =="; sonda
  echo "== 2. Baixar o estado de $ENTRADA e conferir (poller $POLLER, filha $FILHA) =="
  TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT
  for p in $ARQS; do
    c="$(gget "repos/$ENTRADA/contents/$p" --jq '.content' || true)"
    if [ -n "$c" ]; then mkdir -p "$TMP/$(dirname "$p")"; printf '%s' "$c" | python -c 'import base64,sys;sys.stdout.buffer.write(base64.b64decode(sys.stdin.read()))' > "$TMP/$p"; ok "lido $p"
    else echo "  ausente   $p"; fi
  done
  for d in validados recibos criadas entregas; do mkdir -p "$TMP/comandos/$d"; done
  python "$RAIZ/scripts/zapia_poller.py" conferir --raiz "$TMP" --poller-agendado "$POLLER" --repo "$ENTRADA" || DIV=1
  printf 'Você viu a rotina FILHA na lista de rotinas do app (captura tirada)? Digite SIM ou NAO: '; read -r VIU || VIU=""
  [ "$VIU" = "SIM" ] && ok "você confirmou a rotina filha na lista do app (relato seu)." || div "sem confirmação da rotina filha na lista do app"
  printf 'Você recebeu a notificação na hora da filha, sem estar na conversa? Digite SIM ou NAO: '; read -r VIU2 || VIU2=""
  [ "$VIU2" = "SIM" ] && ok "notificação recebida (relato seu)." || div "sem confirmação da notificação espontânea"
  echo
  if [ "$DIV" -eq 0 ]; then
    echo "RESULTADO: PROVADO (autorrelato conferido). Uma rotina da Zapia criou outra, que entregou o alvo. Anexe as capturas e o relato dela ao E29."
    echo "NÃO provado: promoção pelo fluxo (flag/PJ), vários dias e pontualidade (S15-R4). Depois rode: bash $0 limpar"
    exit 0
  fi
  echo "RESULTADO: NÃO PROVADO. Veja as linhas DIVERGE/ausente. Cole AQUI no chat (não no terminal) o texto literal da Zapia: o erro dela também é resultado (pode refutar a hipótese)."
  exit 2
  ;;
limpar)
  base
  pergunta LIMPAR "Apagar os seis arquivos do teste F3 de $ENTRADA?" || { echo "Nada foi apagado."; exit 1; }
  for p in $ARQS; do apagar "$p"; done
  rm -f "$ESTADO"
  echo "Lembre de remover/desativar no app da Zapia o poller e a rotina filha (são de execução única; confira que não ficaram recorrentes)."
  ;;
*)
  echo "uso: bash $0 {preparar|conferir|limpar}" >&2
  exit 1
  ;;
esac
