#!/data/data/com.termux/files/usr/bin/bash
# gera_chaves.sh: gera as chaves Ed25519 do Tutor e do Coach (D-18), confere a guarda e imprime SÓ as públicas.
# Uso (no aparelho do proprietário, dentro do clone do repositório):  bash scripts/termux/gera_chaves.sh
# Opcional: KEYDIR=/caminho/fora/do/repo (padrão ~/.ufms). Requer: python (pkg install python).
# Garantias: a privada fica em KEYDIR (modo 0700 no diretório, 0600 no arquivo), nunca é impressa, nunca é
# sobrescrita (rodar de novo reaproveita a chave existente) e é recusada se estiver dentro do repositório.
# Limites: guarda do sistema de arquivos local; não prova onde o agente roda (OPEN-09). Registrar a pública em
# config/agent_public_keys.json é outro passo, por PR.
set -eu
umask 077

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
KEYS_PY="$REPO/scripts/agent_keys.py"
KEYDIR="${KEYDIR:-$HOME/.ufms}"

command -v python >/dev/null 2>&1 || { echo "Instale o python: pkg install python" >&2; exit 1; }
[ -f "$KEYS_PY" ] || { echo "Não achei scripts/agent_keys.py; rode dentro do clone do repositório." >&2; exit 1; }

case "$(cd "$(dirname "$KEYDIR")" 2>/dev/null && pwd)/$(basename "$KEYDIR")" in
  "$REPO"|"$REPO"/*) echo "KEYDIR não pode ficar dentro do repositório." >&2; exit 1;;
esac

mkdir -p "$KEYDIR"
chmod 700 "$KEYDIR"

# pub_de SAIDA_JSON: extrai public_key do JSON impresso por agent_keys.py (nunca há segredo nessa saída).
pub_de() { python -c 'import json,sys; print(json.loads(sys.stdin.read())["public_key"])'; }

PUB_TUTOR=""
PUB_COACH=""
for ROLE in tutor coach; do
  KEY="$KEYDIR/$ROLE.key"
  if [ -e "$KEY" ] || [ -L "$KEY" ]; then
    echo "[$ROLE] chave já existe; mantida (não sobrescrevo)."
  else
    python "$KEYS_PY" generate --private-out "$KEY" >/dev/null
    echo "[$ROLE] chave gerada em $KEY"
  fi
  SAIDA="$(python "$KEYS_PY" verify-key --key "$KEY")" || { echo "[$ROLE] guarda FALHOU; corrija e rode de novo." >&2; exit 1; }
  PUB="$(printf '%s' "$SAIDA" | pub_de)"
  [ "$ROLE" = tutor ] && PUB_TUTOR="$PUB" || PUB_COACH="$PUB"
  echo "[$ROLE] guarda OK"
done

if [ "$PUB_TUTOR" = "$PUB_COACH" ]; then
  echo "As duas chaves públicas são iguais; isso não deve acontecer." >&2
  exit 1
fi

echo
echo "Chaves PÚBLICAS (podem ser enviadas ao agente construtor; as privadas ficam em $KEYDIR):"
echo "  tutor $PUB_TUTOR"
echo "  coach $PUB_COACH"
echo
echo "Próximo passo: envie só essas duas linhas; o registro em config/agent_public_keys.json é por PR."
echo "Nunca envie o conteúdo de $KEYDIR/*.key."
