"""Contraprovas determinísticas da exigência de ROADMAP."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from roadmap_gate import REFERENCES, verify

class RoadmapGateTests(unittest.TestCase):
    def test_gate_integrado_confere_sha(self):
        self.assertEqual(len(verify(ROOT)), 64)

    def test_documentos_estrategicos_referenciam_roadmap(self):
        for path in REFERENCES:
            with self.subTest(path=path):
                self.assertIn("ROADMAP.md", (ROOT / path).read_text(encoding="utf-8"))

    def test_mutacao_referencia_removida_falha(self):
        reader = Path.read_text
        def mutant(path, *args, **kwargs):
            contents = reader(path, *args, **kwargs)
            if str(path).endswith("docs/OPERACAO.md"):
                return contents.replace("ROADMAP.md", "REMOVIDO")
            return contents
        with patch.object(Path, "read_text", mutant):
            with self.assertRaisesRegex(ValueError, "Referência ao roadmap ausente"):
                verify(ROOT)

    def test_nove_arquivos_reprova_contrato(self):
        read = Path.read_text
        def mutated(path, *args, **kwargs):
            text = read(path, *args, **kwargs)
            if str(path).endswith("docs/OPERACAO.md"):
                return text.replace("dez arquivos obrigatórios", "nove arquivos obrigatórios")
            return text
        with patch.object(Path, "read_text", mutated):
            with self.assertRaisesRegex(ValueError, "Contrato de leitura desatualizado"):
                verify(ROOT)

if __name__ == "__main__":
    unittest.main()
