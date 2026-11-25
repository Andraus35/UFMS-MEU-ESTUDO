#!/data/data/com.termux/files/usr/bin/bash
# aprova_n1.sh (limite 3 do N1, lote VOLTA-N1): ATO DO PROPRIETÁRIO, no Termux, com a SUA sessão do gh e a SUA chave. Dois passos:
#   chave   : gera a chave privada Ed25519 FORA do repositório (padrão ~/.ufms/chave_proprietario, modo 0600, pasta 0700) e imprime a PÚBLICA.
#   aprovar : lê de `entrada` os comandos de comandos/validados/, MOSTRA o prompt de cada um para você ler, e só com a frase APROVO N1 assina o hash_corpo
#             (aprovação destacada, scripts/aprovacao_comando.py) e grava comandos/aprovacoes/<nome>.aprovacao.json em `entrada`, com leitura de volta.
# A chave privada nunca vai ao modelo nem ao repositório. A aprovação prova que ESTA chave aprovou ESTE hash; não prova que o Tutor escreveu o texto.
# Códigos: 0 ok; 1 bloqueado; 2 divergência.
set -eu
umask 077
export PYTHONDONTWRITEBYTECODE=1
ENTRADA="Andraus35/ufms-meu-estudo-entrada"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
CHAVE="${UFMS_CHAVE:-$HOME/.ufms/chave_proprietario}"
PASSO="${1:-}"
DIV=0
falha() { echo "BLOQUEADO: $1" >&2; exit 1; }
div() { echo "  DIVERGE   $1"; DIV=$((DIV+1)); }
ok() { echo "  OK        $1"; }
pergunta() { local r; printf '%s Digite %s para continuar (Enter pula): ' "$2" "$1"; read -r r || r=""; [ "$r" = "$1" ]; }
case "$PASSO" in chave|aprovar) ;; *) echo "Uso: bash scripts/termux/aprova_n1.sh {chave|aprovar}"; exit 2;; esac
command -v python >/dev/null 2>&1 || falha "falta o comando python."
TMP="$(mktemp -d)"; chmod 700 "$TMP"; trap 'rm -rf "$TMP"' EXIT

if [ "$PASSO" = "chave" ]; then
  [ ! -e "$CHAVE" ] || falha "já existe uma chave em $CHAVE; não sobrescrevo (apague-a você mesmo se quiser outra)."
  mkdir -p "$(dirname "$CHAVE")"; chmod 700 "$(dirname "$CHAVE")"
  python "$ROOT/scripts/aprovacao_comando.py" gerar-chave --privada "$CHAVE" || falha "não consegui gerar a chave."
  echo "Guarde a chave pública acima (é pública). A privada ficou em $CHAVE e não deve sair do aparelho."
  exit 0
fi

command -v gh >/dev/null 2>&1 || falha "falta o comando gh."; command -v base64 >/dev/null 2>&1 || falha "falta o comando base64."
gh auth status >/dev/null 2>&1 || falha "faça 'gh auth login' antes."
[ -f "$CHAVE" ] || falha "sem chave em $CHAVE; rode antes: bash scripts/termux/aprova_n1.sh chave"
[ "$(gh api "repos/$ENTRADA" --jq '.private' 2>/dev/null)" = "true" ] || falha "$ENTRADA não é privado ou não existe."
NOMES="$(gh api "repos/$ENTRADA/contents/comandos/validados" --jq '.[].name' 2>/dev/null | grep '\.json$' | sort)" || true
[ -n "$NOMES" ] || falha "não há comandos em comandos/validados/ de $ENTRADA."
mkdir -p "$TMP/cmd"
for n in $NOMES; do
  gh api "repos/$ENTRADA/contents/comandos/validados/$n" --jq .content | base64 -d > "$TMP/cmd/$n" || falha "não consegui ler $n."
done
echo "== Prompts que você vai aprovar (leia antes) =="
python - "$TMP/cmd" "$ROOT" <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[2] + "/scripts")
import command_box
for f in sorted(Path(sys.argv[1]).glob("*.json")):
    c = json.loads(f.read_text(encoding="utf-8"))
    print("\n--- " + f.name + "  origem=" + str(c.get("origin")) + "  hash=" + command_box.command_hash(c)[:12] + "...")
    print(c.get("params", {}).get("prompt", "(sem campo prompt)"))
PY
echo
pergunta "APROVO N1" "Aprovar com a sua chave os hashes dos comandos acima e gravar as aprovações em comandos/aprovacoes/ de $ENTRADA?" || { echo "Nada foi feito."; exit 1; }
python - "$TMP/cmd" "$ROOT" "$CHAVE" "$TMP/aprov" <<'PY' || falha "não consegui assinar (a guarda da chave recusou ou o comando é inválido)."
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[2] + "/scripts")
import aprovacao_comando, command_box
saida = Path(sys.argv[4]); saida.mkdir()
for f in sorted(Path(sys.argv[1]).glob("*.json")):
    c = json.loads(f.read_text(encoding="utf-8"))
    ap = aprovacao_comando.aprovar(command_box.command_hash(c), sys.argv[3])
    (saida / (f.stem + ".aprovacao.json")).write_text(json.dumps(ap, indent=2), encoding="utf-8")
PY
for a in "$TMP"/aprov/*.aprovacao.json; do
  nome="$(basename "$a")"; caminho="comandos/aprovacoes/$nome"
  gh api "repos/$ENTRADA/contents/$caminho" >/dev/null 2>&1 && { div "$caminho já existe; não sobrescrevo"; continue; }
  conteudo="$(base64 < "$a" | tr -d '\n')"
  gh api -X PUT "repos/$ENTRADA/contents/$caminho" -f message="N1: aprovacao destacada do proprietario (hash do comando)" -f content="$conteudo" -f branch=main >/dev/null 2>&1 || { div "não consegui gravar $caminho"; continue; }
  gh api "repos/$ENTRADA/contents/$caminho" --jq .content 2>/dev/null | base64 -d > "$TMP/volta" 2>/dev/null || true
  if cmp -s "$TMP/volta" "$a"; then ok "$caminho gravado e conferido por leitura de volta."; else div "$caminho: a leitura de volta difere"; fi
done
[ "$DIV" -eq 0 ] && { echo "RESULTADO: aprovações gravadas. Avise a sessão: ela verifica com a chave pública."; exit 0; }
echo "RESULTADO: $DIV divergência(s)." >&2; exit 2
