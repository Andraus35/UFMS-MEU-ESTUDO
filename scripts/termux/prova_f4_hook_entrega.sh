#!/data/data/com.termux/files/usr/bin/bash
# prova_f4_hook_entrega.sh (ponta a ponta, E31): o PROPRIETÁRIO prova, UMA vez e com par SINTÉTICO, que um HOOK de Gmail da Zapia, ao acordar pelo e-mail de uma issue
# do `entrada` privado, LÊ o comando validado e o recibo, CONFERE o hash, NOTIFICA e GRAVA o recibo de entrega, que este script confere por código (hash, carimbo
# não anterior à criação da issue e até 900 s depois, uma única entrega). Subcomandos: preparar | sinal | conferir | limpar. Roda DENTRO do clone do repositório
# público, na revisão enviada ao GitHub. Usa só a SUA sessão do gh; nenhum token da Zapia passa por aqui; sem dado pessoal; não liga flag; não promove pelo fluxo.
# Códigos de saída: 0 provado/ok; 1 bloqueado; 2 divergência. Limites: autorrelato da Zapia (carimbo e notificação); o par é colocado à mão (SINTETICO_MANUAL);
# um disparo; o emissor é você (issue aberta à mão), não o fluxo; não prova vários dias nem hook recorrente.
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1
ENTRADA="${F4_REPO:-Andraus35/ufms-meu-estudo-entrada}"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
ESTADO="${F4_ESTADO:-$HOME/.ufms-f4-estado.json}"
NOME="f4-hook.json"
ARQS="comandos/validados/$NOME comandos/recibos/$NOME comandos/entregas/$NOME"
DIV=0
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
ok() { echo "  OK        $1"; }
div() { echo "  DIVERGE   $1"; DIV=1; }
gget() { local o; o="$(gh api "$@" 2>/dev/null)" || return 1; printf '%s' "$o"; }
pergunta() { local r; printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"; read -r r || r=""; [ "$r" = "$1" ]; }
b64() { python -c 'import base64,sys;print(base64.b64encode(sys.stdin.buffer.read()).decode())'; }
sha_de() { gget "repos/$ENTRADA/contents/$1" --jq '.sha' || true; }
subir() { local c; c="$(b64 < "$2")"; gh api -X PUT "repos/$ENTRADA/contents/$1" -f message="teste ponta a ponta (sintetico)" -f content="$c" -f branch=main >/dev/null 2>&1 || falha "não consegui gravar $1 (sua sessão do gh precisa de escrita em $ENTRADA)."; }
apagar() { local s; s="$(sha_de "$1")"; [ -n "$s" ] || return 0
  gh api -X DELETE "repos/$ENTRADA/contents/$1" -f message="teste ponta a ponta: limpeza" -f sha="$s" -f branch=main >/dev/null 2>&1 && ok "apagado $1" || echo "  AVISO     não apaguei $1"; }
base() { for cmd in gh python base64; do command -v "$cmd" >/dev/null 2>&1 || falha "falta o comando $cmd."; done
  [ -f "$RAIZ/scripts/zapia_f1_prep.py" ] && [ -f "$RAIZ/scripts/zapia_disparo.py" ] || falha "rode dentro do clone do repositório público (faltam scripts/zapia_f1_prep.py e scripts/zapia_disparo.py)."
  gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes."
  [ "$(gget "repos/$ENTRADA" --jq '.private' || true)" = "true" ] || falha "$ENTRADA não é privado ou não existe."; }
estado_campo() { python -c 'import json,sys;print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$ESTADO" "$1"; }

usar="${1:-}"
case "$usar" in
preparar)
  base
  [ -f "$RAIZ/scripts/agendar_rotina.py" ] || falha "falta scripts/agendar_rotina.py."
  echo "== 1. Pré-condições =="
  for p in $ARQS; do [ -z "$(sha_de "$p")" ] || falha "já existe $p em $ENTRADA (resto de outro teste). Rode: bash $0 limpar"; done
  ok "entrada privado e sem resto de teste anterior."
  [ "$(gget "repos/$ENTRADA" --jq '.has_issues' || true)" = "true" ] || falha "as issues estão desligadas em $ENTRADA; não vou mudar a configuração."
  ok "issues ligadas (o sinal será uma issue)."
  pergunta TESTAR "Gravar o par sintético ($NOME) em $ENTRADA?" || { echo "Nada foi feito."; exit 1; }
  TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT
  python "$RAIZ/scripts/zapia_f1_prep.py" preparar --saida "$TMP" --nome "$NOME" >/dev/null || falha "o comando de teste não passou no validador da caixa."
  HASH="$(python -c 'import json,sys;print(json.load(open(sys.argv[1]))["hash_corpo"])' "$TMP/meta.json")"
  subir "comandos/validados/$NOME" "$TMP/validados/$NOME"
  subir "comandos/recibos/$NOME" "$TMP/recibos/$NOME"
  ok "par gravado (hash ${HASH:0:12}...; recibo SINTETICO_MANUAL; o comando vale 24 h)."
  printf '{"hash":"%s"}\n' "$HASH" > "$ESTADO"
  INSTR="$(python "$RAIZ/scripts/agendar_rotina.py" --hook-entrega --hash "$HASH" --repo "$ENTRADA")" || falha "não consegui montar a instrução do hook."
  PROMPT="TESTE PONTA A PONTA, uma vez só, hook de e-mail. Crie UM hook de Gmail na conta Gmail conectada em Conectores, caixa de entrada, com EXATAMENTE estes filtros e nenhum outro: senders = notifications@github.com e subject_contains = \"[$ENTRADA] SINAL\". NÃO use labels nem text_contains. Se a ferramenta não salvar exatamente esses dois filtros, NÃO crie o hook e diga o motivo literal. A tarefa do hook é EXATAMENTE o texto entre as marcas INICIO e FIM (não traduza, não resuma, não reescreva nenhum URL ou pasta). Depois de salvar, mostre lidos de volta: a conta, os filtros e o texto salvo. Não crie nenhuma rotina, lembrete ou outro hook. INICIO $INSTR FIM"
  echo; echo "== 2. Envie este texto à Zapia (na conversa dela, NÃO aqui no terminal) =="; echo; echo "$PROMPT"; echo
  if command -v termux-clipboard-set >/dev/null 2>&1; then printf '%s' "$PROMPT" | termux-clipboard-set && echo "[copiado]"; fi
  echo "Quando a Zapia mostrar a conta, os filtros e o texto lidos de volta, rode: bash $0 sinal"
  ;;
sinal)
  base
  [ -f "$ESTADO" ] || falha "não achei $ESTADO; rode 'preparar' antes."
  pergunta SIM "A Zapia mostrou a conta, SÓ os dois filtros e o texto do hook lidos de volta, e o hook está ativo?" || { echo "Nada foi feito."; exit 1; }
  URL="$(gh issue create -R "$ENTRADA" -t "SINAL teste E2E" -b "teste sem dado pessoal")" || falha "não consegui criar a issue."
  N="${URL##*/}"
  CRIADA="$(gh issue view -R "$ENTRADA" "$N" --json createdAt --jq '.createdAt')"
  python -c 'import json,sys;d=json.load(open(sys.argv[1]));d["issue"]=sys.argv[2];d["criada"]=sys.argv[3];json.dump(d,open(sys.argv[1],"w"))' "$ESTADO" "$N" "$CRIADA"
  echo; echo "Issue criada: #$N"; echo "Criada em (UTC): $CRIADA"; echo "Assunto esperado: [$ENTRADA] SINAL teste E2E (Issue #$N)"
  echo
  echo "NÃO FECHE a issue ainda: o aviso de fechamento é outro e-mail ('Re: ...')."
  echo "Aguarde a Zapia notificar e relatar no chat (tolerância: 15 min). Tire a captura com o relógio visível."
  printf 'Tecle ENTER SOMENTE depois que a Zapia relatar (ou depois de 15 min sem resposta): '; read -r _ || true
  gh issue close -R "$ENTRADA" "$N" --reason "not planned" >/dev/null && echo "Issue #$N fechada."
  echo "Agora rode: bash $0 conferir"
  ;;
conferir)
  base
  [ -f "$ESTADO" ] || falha "não achei $ESTADO; rode 'preparar' e 'sinal' antes."
  CRIADA="$(estado_campo criada)" || falha "o estado não tem a hora de criação da issue; rode 'sinal' antes."
  TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT
  for d in validados recibos entregas; do mkdir -p "$TMP/comandos/$d"; done
  for p in $ARQS; do
    c="$(gget "repos/$ENTRADA/contents/$p" --jq '.content' || true)"
    if [ -n "$c" ]; then printf '%s' "$c" | python -c 'import base64,sys;sys.stdout.buffer.write(base64.b64decode(sys.stdin.read()))' > "$TMP/$p"; ok "lido $p"
    else echo "  ausente   $p"; fi
  done
  echo "== Conferência por código (hash, carimbo não anterior a $CRIADA e até 900 s depois, entrega única) =="
  python "$RAIZ/scripts/zapia_disparo.py" --raiz "$TMP" --nome "$NOME" --agendado "$CRIADA" || DIV=1
  printf 'Você viu no chat da Zapia a notificação "Coach (origem declarada): ..."? Digite SIM ou NAO: '; read -r V1 || V1=""
  [ "$V1" = "SIM" ] && ok "notificação vista (relato seu)." || div "sem confirmação da notificação"
  printf 'A Zapia confirmou que o hook foi desativado ou apagado? Digite SIM ou NAO: '; read -r V2 || V2=""
  [ "$V2" = "SIM" ] && ok "hook desativado (relato dela, por você)." || div "hook sem confirmação de desativação"
  echo
  if [ "$DIV" -eq 0 ]; then
    echo "RESULTADO: PROVADO (autorrelato conferido). O hook acordou pelo e-mail, leu o comando e o recibo, conferiu o hash, notificou e gravou o recibo de entrega."
    echo "NÃO provado: o fluxo como emissor, hook recorrente, vários dias e pontualidade em relação a agendado_utc. Depois rode: bash $0 limpar"
    exit 0
  fi
  echo "RESULTADO: NÃO PROVADO. Veja as linhas DIVERGE/ausente e cole AQUI no chat (não no terminal) o texto literal da Zapia: o erro dela também é resultado."
  exit 2
  ;;
limpar)
  base
  pergunta LIMPAR "Apagar os três arquivos do teste ponta a ponta de $ENTRADA?" || { echo "Nada foi apagado."; exit 1; }
  for p in $ARQS; do apagar "$p"; done
  rm -f "$ESTADO"
  echo "Lembre de apagar o hook no app da Zapia (ele deve estar desativado, mas pode continuar salvo na lista)."
  ;;
*)
  echo "uso: bash $0 {preparar|sinal|conferir|limpar}" >&2
  exit 1
  ;;
esac
