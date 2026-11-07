"""Preflight invocável explicitamente; não é hook nativo registrado."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (ROOT, ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def run(root=ROOT):
    from scripts.validate import validate
    validate(root)
    return True


if __name__ == "__main__":
    try:
        run()
        print("OK: preflight local completo; nenhuma escrita realizada")
    except (OSError, KeyError, ValueError) as exc:
        print("FALHA: preflight bloqueado: " + str(exc), file=sys.stderr)
        sys.exit(1)
