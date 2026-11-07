"""PRD-01: contagem de arquivos do bootstrap declarada nos documentos confere com settings.json."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUMEROS = {"três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10}
CLAIMS = re.compile(r"(?:(\d+)|(três|quatro|cinco|seis|sete|oito|nove|dez))\s+arquivos\s+(?:por sessão|obrigat|do bootstrap)",
                    re.I)
DOCS = ("AGENTS.md", "README.md", "docs/OPERACAO.md")


def claimed_counts(text):
    return [int(a) if a else NUMEROS[b.lower()] for a, b in CLAIMS.findall(text)]


class BootstrapDocSyncTests(unittest.TestCase):
    def effective(self):
        settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        return len(settings["bootstrap"]["mandatory"])

    def test_documentos_declaram_a_contagem_efetiva_do_settings(self):
        efetivo = self.effective()
        achou = 0
        for doc in DOCS:
            for n in claimed_counts((ROOT / doc).read_text(encoding="utf-8")):
                achou += 1
                self.assertEqual(n, efetivo, f"{doc} declara {n} arquivos; settings.json lista {efetivo}")
        self.assertGreaterEqual(achou, 3)

    def test_divergencia_de_contagem_e_detectada(self):
        efetivo = self.effective()
        self.assertEqual(claimed_counts("Bootstrap obrigatório — 7 arquivos por sessão"), [7])
        self.assertNotEqual(claimed_counts("conferir os sete arquivos obrigatórios")[0], efetivo)
        self.assertEqual(claimed_counts("os quatro arquivos obrigatórios")[0], efetivo)
        self.assertEqual(claimed_counts("sem declaração de contagem"), [])


if __name__ == "__main__":
    unittest.main()
