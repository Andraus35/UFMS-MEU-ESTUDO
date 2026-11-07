"""PED-15: o estado é recuperado dos eventos versionados, não de memória do processo."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RetomadaTests(unittest.TestCase):
    def test_processo_novo_reconstroi_as_projecoes_versionadas(self):
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        r = subprocess.run([sys.executable, str(ROOT / "scripts/rebuild.py"), "--check"],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
