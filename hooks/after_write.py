"""Postflight invocável explicitamente; não comprova commit remoto."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(root=ROOT):
    from scripts.validate import validate
    validate(root)
    return True


if __name__ == "__main__":
    try:
        run()
        print("OK: postflight local completo; commit remoto nao verificado")
    except (OSError, KeyError, ValueError) as exc:
        print("FALHA: postflight bloqueado: " + str(exc), file=sys.stderr)
        sys.exit(1)
