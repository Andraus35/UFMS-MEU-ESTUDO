#!/data/data/com.termux/files/usr/bin/bash
# prova_n1.sh (teste N1 da ponte Tutor -> Zapia -> Gemini Notebook, S10-R11, roteiro do E40): ATO DO PROPRIETÁRIO, no Termux, com a SUA sessão do gh.
# Três passos, um por vez:  preparar | colocar | conferir
#   preparar : gera os comandos e recibos SINTÉTICOS (scripts/zapia_n1_prep.py) em $N1_DIR (padrão ~/n1). Offline, não grava nada no GitHub.
#   colocar  : (frase COLOCAR N1) grava os comandos em comandos/validados/, os recibos em comandos/recibos/ e a fonte pública em comandos/fontes/n1.txt de `entrada`, e confere cada um por
#              leitura de volta (bytes iguais). Recusa sobrescrever arquivo que já exista. Os recibos são SINTETICO_MANUAL: NÃO provam promoção pelo fluxo.
#   conferir : lê comandos/respostas/<nome> de `entrada` e roda scripts/notebook_response_check.py. Só leitura. Não imprime o texto da resposta.
# Sem token em argumento ou tela (usa o gh logado). A flag de escrita de resultados NÃO é tocada. Limite: prova o transporte e a conferência; o
# Notebook e a Zapia só são provados se a resposta REAL chegar e passar; a sessão em nuvem não executa este roteiro.
# Códigos: 0 tudo conferido; 1 bloqueado; 2 divergência ou resposta pendente.
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1
ENTRADA="Andraus35/ufms-meu-estudo-entrada"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
N1_DIR="${N1_DIR:-$HOME/n1}"
N1_PREFIXO="${N1_PREFIXO:-n1}"  # n1 (1ª rodada), n1b, n1c, n1d (E48): prefixo dos nomes dos comandos; o hook não repete respostas já gravadas com o mesmo nome
PASSO="${1:-}"
DIV=0
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
div() { echo "  DIVERGE   $1"; DIV=$((DIV+1)); }
ok() { echo "  OK        $1"; }
pergunta() { local r; printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"; read -r r || r=""; [ "$r" = "$1" ]; }
case "$PASSO" in preparar|colocar|conferir) ;; *) echo "Uso: bash scripts/termux/prova_n1.sh {preparar|colocar|conferir}"; exit 2;; esac
for cmd in python; do command -v "$cmd" >/dev/null 2>&1 || falha "falta o comando $cmd."; done
TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT

if [ "$PASSO" = "preparar" ]; then
  python "$ROOT/scripts/zapia_n1_prep.py" --saida "$N1_DIR" --prefixo "$N1_PREFIXO" >/dev/null || falha "o preparo recusou (validador do prompt ou caixa)."
  ok "arquivos gerados em $N1_DIR (comandos, recibos, fonte-n1.txt, instrucao-zapia.txt)."
  echo "Próximo: bash scripts/termux/prova_n1.sh colocar"
  exit 0
fi

for cmd in gh base64; do command -v "$cmd" >/dev/null 2>&1 || falha "falta o comando $cmd."; done
gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes."
[ -f "$N1_DIR/meta.json" ] || falha "rode antes: bash scripts/termux/prova_n1.sh preparar"
[ "$(gh api "repos/$ENTRADA" --jq '.private' 2>/dev/null)" = "true" ] || falha "$ENTRADA não é privado ou não existe."
NOMES="$(python -c 'import json,sys;print(" ".join(sorted(json.load(open(sys.argv[1]))["itens"])))' "$N1_DIR/meta.json")"
[ -n "$NOMES" ] || falha "meta.json sem itens."

if [ "$PASSO" = "colocar" ]; then
  FONTE_EXISTE=0
  if gh api "repos/$ENTRADA/contents/comandos/fontes/n1.txt" >/dev/null 2>&1; then  # a fonte é pública e igual em todas as rodadas: se já existe com os MESMOS bytes, não regrava
    gh api "repos/$ENTRADA/contents/comandos/fontes/n1.txt" --jq .content 2>/dev/null | base64 -d > "$TMP/fonte-atual" 2>/dev/null || true
    cmp -s "$TMP/fonte-atual" "$N1_DIR/fonte-n1.txt" && FONTE_EXISTE=1 || falha "comandos/fontes/n1.txt já existe em entrada com conteúdo diferente; não sobrescrevo."
  fi
  for n in $NOMES; do
    gh api "repos/$ENTRADA/contents/comandos/validados/$n" >/dev/null 2>&1 && falha "comandos/validados/$n já existe em entrada; não sobrescrevo."
    gh api "repos/$ENTRADA/contents/comandos/recibos/$n" >/dev/null 2>&1 && falha "comandos/recibos/$n já existe em entrada; não sobrescrevo."
  done
  pergunta "COLOCAR N1" "Gravar os comandos, recibos e a fonte SINTÉTICOS (sem dado pessoal) em comandos/ de $ENTRADA com a sua sessão do gh?" || { echo "Nada foi feito."; exit 1; }
  grava() {  # $1 caminho no repositório; $2 arquivo local
    local conteudo; conteudo="$(base64 < "$2" | tr -d '\n')"
    gh api -X PUT "repos/$ENTRADA/contents/$1" -f message="N1: arquivo sintetico do teste da ponte (sem dado pessoal)" -f content="$conteudo" -f branch=main >/dev/null 2>&1 || { div "não consegui gravar $1"; return; }
    gh api "repos/$ENTRADA/contents/$1" --jq .content 2>/dev/null | base64 -d > "$TMP/volta" 2>/dev/null || true
    if cmp -s "$TMP/volta" "$2"; then ok "$1 gravado e conferido por leitura de volta."; else div "$1: a leitura de volta difere do que foi gravado"; fi
  }
  if [ "$FONTE_EXISTE" = 1 ]; then ok "comandos/fontes/n1.txt já existe com os mesmos bytes; mantido."; else grava "comandos/fontes/n1.txt" "$N1_DIR/fonte-n1.txt"; fi
  for n in $NOMES; do
    grava "comandos/validados/$n" "$N1_DIR/$n"
    grava "comandos/recibos/$n" "$N1_DIR/${n%.json}.recibo.json"
  done
  echo "Próximo: crie na Zapia o hook de Gmail de uso único com o texto de $N1_DIR/instrucao-hook-notebook.txt (ou, sem hook, cole $N1_DIR/instrucao-zapia.txt); depois: bash scripts/termux/prova_n1.sh conferir"
  [ "$DIV" -eq 0 ] || { echo "RESULTADO: $DIV divergência(s)." >&2; exit 2; }
  exit 0
fi

# conferir (só leitura)
PENDENTE=0
for n in $NOMES; do
  if gh api "repos/$ENTRADA/contents/comandos/respostas/$n" --jq .content 2>/dev/null | base64 -d > "$TMP/resp-$n" 2>/dev/null && [ -s "$TMP/resp-$n" ]; then
    CODIGO="$(python - "$N1_DIR" "$n" "$TMP/resp-$n" "$ROOT" <<'PY'
import json, sys
d, nome, resp, raiz = sys.argv[1:5]
sys.path.insert(0, raiz + "/scripts")
import notebook_response_check as chk
meta = json.load(open(d + "/meta.json", encoding="utf-8"))
item = meta["itens"][nome]
esperado = {"nome": nome, "hash_corpo": item["hash_corpo"], "fonte_nome": meta["fonte_nome"]}
fonte = open(d + "/fonte-n1.txt", encoding="utf-8").read()
codigo = chk.conferir(open(resp, "rb").read(), esperado, fonte, contraprova=bool(item["contraprova"]), ancora_gabarito=item.get("ancora_gabarito"))
if codigo is None and json.loads(open(resp, encoding="utf-8").read()).get("estado") == "PARADO":
    codigo = "PARADA_REGISTRADA"  # forma válida, mas o teste NÃO foi provado: a Zapia ou o Notebook pararam
print(codigo or "OK")
PY
)"
    if [ "$CODIGO" = "OK" ]; then ok "$n: resposta confere (pode seguir ao Tutor)."; else div "$n: resposta recusada ($CODIGO)"; fi
  else
    echo "  PENDENTE  $n: ainda não há comandos/respostas/$n"; PENDENTE=$((PENDENTE+1))
  fi
done
echo "== Resumo =="
echo "Isto confere só a forma, o vínculo por hash, a citação e a contraprova; a fidelidade do Notebook segue sem medida (S10, limites)."
[ "$DIV" -eq 0 ] && [ "$PENDENTE" -eq 0 ] && { echo "RESULTADO: N1 conferido."; exit 0; }
echo "RESULTADO: $DIV divergência(s), $PENDENTE pendente(s)." >&2; exit 2
