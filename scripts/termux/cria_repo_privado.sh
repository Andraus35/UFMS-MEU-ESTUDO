#!/data/data/com.termux/files/usr/bin/bash
# cria_repo_privado.sh: o PROPRIETÁRIO cria (se não existir) o repositório privado de dados de estudo, confere
# private=true (ADR-013, P1) e registra o consentimento v2 (P3), com readback. Roda no aparelho dele, com a
# credencial dele no `gh` (gh auth login). Nenhuma credencial passa por este script, pelo modelo nem pela Zapia.
# Uso:  bash scripts/termux/cria_repo_privado.sh   (dentro do clone; precisa de gh, python, base64 e sha256sum)
# Garantias: destino fixo (P2), nunca o repositório público; só segue se a leitura autenticada devolver
# private=true; só grava o consentimento depois de você digitar a frase; não sobrescreve consentimento existente.
# Limites: NÃO habilita a escrita de resultados (personal_results_writes_enabled continua false; isso é PR próprio
# com aprovação humana) e não resolve P4, OPEN-01 nem OPEN-02. O token da Zapia é outro passo (D-09).
set -eu
umask 077

REPO="Andraus35/ufms-meu-estudo-dados"
PUBLIC_REPO="Andraus35/UFMS-MEU-ESTUDO"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ADR="$ROOT/docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md"

for cmd in gh python base64 sha256sum; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Falta o comando $cmd (pkg install gh python coreutils)." >&2; exit 1; }
done
[ -f "$ADR" ] || { echo "Não achei o ADR-013; rode dentro do clone do repositório." >&2; exit 1; }
[ "$(printf '%s' "$REPO" | tr 'A-Z' 'a-z')" != "$(printf '%s' "$PUBLIC_REPO" | tr 'A-Z' 'a-z')" ] \
  || { echo "P2: o destino não pode ser o repositório público." >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Faça 'gh auth login' antes (a credencial fica só no seu aparelho)." >&2; exit 1; }

TMP="$(mktemp -d)"; chmod 700 "$TMP"
trap 'rm -rf "$TMP"' EXIT

# leitura: imprime o valor e devolve 0; 2 se não existe (404); 1 em qualquer outro erro.
ler() {
  local out
  if out="$(gh api "$@" 2>&1)"; then printf '%s' "$out"; return 0; fi
  case "$out" in *404*|*"Not Found"*) return 2;; *) return 1;; esac
}

set +e; VIS="$(ler "repos/$REPO" --jq '.private')"; RC=$?; set -e
if [ "$RC" -eq 0 ]; then
  [ "$VIS" = "true" ] || { echo "BLOQUEADO (P1): $REPO existe e NÃO é privado. Nada foi gravado." >&2; exit 1; }
  echo "[repositório] já existe e é privado."
elif [ "$RC" -eq 2 ]; then
  printf 'O repositório %s não existe. Digite CRIAR para criá-lo como PRIVADO: ' "$REPO"
  read -r RESP || RESP=""
  [ "$RESP" = "CRIAR" ] || { echo "Nada foi criado." >&2; exit 1; }
  gh repo create "$REPO" --private --description "Dados de estudo (privado)" >/dev/null
  echo "[repositório] criado."
else
  echo "Não consegui ler o repositório (erro que não é 'não existe'); nada foi feito." >&2; exit 1
fi

set +e; VIS="$(ler "repos/$REPO" --jq '.private')"; RC=$?; set -e
[ "$RC" -eq 0 ] && [ "$VIS" = "true" ] \
  || { echo "BLOQUEADO (P1): não confirmei private=true por leitura autenticada. Nada foi gravado." >&2; exit 1; }
echo "[P1] private=true confirmado por leitura autenticada."

set +e; ler "repos/$REPO/contents/consent.json" --jq '.sha' >/dev/null; RC=$?; set -e
if [ "$RC" -eq 0 ]; then
  echo "[P3] consent.json já existe; mantido (não sobrescrevo). Para revogar, veja o procedimento no ADR-013 (P8)."
  echo "A escrita de resultados continua DESABILITADA (personal_results_writes_enabled=false)."
  exit 0
elif [ "$RC" -ne 2 ]; then
  echo "Não consegui verificar o consentimento; nada foi gravado." >&2; exit 1
fi

NOW="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
python - "$ADR" "$NOW" "$TMP/consent.json" "$TMP/texto.txt" <<'PY'
import hashlib, json, sys
adr, now, out_json, out_text = sys.argv[1:5]
texto = open(adr, encoding="utf-8").read()
secao = texto.split("## Consentimento v2", 1)[1].split("\n## ", 1)[0]
citacoes = [l[2:].strip() for l in secao.splitlines() if l.startswith("> ")]
if len(citacoes) != 1 or not citacoes[0].endswith("Versão: v2."):
    sys.exit("O texto do consentimento v2 não foi encontrado de forma única no ADR-013.")
registro = {"version": "v2", "scope": "resultados_estudo", "granted_at": now, "revoked_at": None,
            "text": citacoes[0], "text_sha256": hashlib.sha256(citacoes[0].encode("utf-8")).hexdigest()}
open(out_json, "w", encoding="utf-8").write(json.dumps(registro, ensure_ascii=False, indent=2) + "\n")
open(out_text, "w", encoding="utf-8").write(citacoes[0] + "\n")
PY

echo
echo "Texto do consentimento v2 (ADR-013):"
cat "$TMP/texto.txt"
echo
printf 'Para REGISTRAR este consentimento agora, digite CONSINTO v2 (Enter para pular): '
read -r RESP || RESP=""
if [ "$RESP" != "CONSINTO v2" ]; then
  echo "[P3] consentimento NÃO registrado. Sem ele, nenhuma gravação de resultados é permitida."
  exit 0
fi

B64="$(base64 < "$TMP/consent.json" | tr -d '\n')"
gh api -X PUT "repos/$REPO/contents/consent.json" -f message="Consentimento v2 registrado pelo proprietario" \
  -f content="$B64" >/dev/null
LOCAL="$(sha256sum "$TMP/consent.json" | cut -d' ' -f1)"
set +e; REMOTO="$(ler "repos/$REPO/contents/consent.json" --jq '.content' | base64 -d 2>/dev/null | sha256sum | cut -d' ' -f1)"; set -e
if [ "$LOCAL" != "$REMOTO" ]; then
  echo "PENDENTE (P6): o readback do consentimento divergiu; não considere registrado. Confira no GitHub." >&2; exit 1
fi
echo "[P3] consentimento v2 registrado e confirmado por readback (sha256 ${LOCAL:0:12}...)."
echo "A escrita de resultados continua DESABILITADA (personal_results_writes_enabled=false); habilitar é PR próprio."
echo "Próximos passos: token fine-grained só deste repositório para a Zapia (D-09) e a validação P4/OPEN-01/OPEN-02."
