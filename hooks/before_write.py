"""Hook opcional: verificação pré-gravação. Integrar explicitamente ao agente."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    result = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")], cwd=ROOT, check=False)
    if result.returncode:
        print("Falha pré-escrita. Corrija a origem antes de publicar.", file=sys.stderr)
    sys.exit(result.returncode)
