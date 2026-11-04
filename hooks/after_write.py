"""Hook opcional: verificação pós-gravação. Não equivale a commit remoto."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    result = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")], cwd=ROOT, check=False)
    sys.exit(result.returncode)
