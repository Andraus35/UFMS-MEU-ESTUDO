"""O recorte GP-3-MVP8 permanece rastreável: 8 referências resolvem para testes reais."""
import importlib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DOC = (ROOT / "docs/pedagogia/GP3_MVP_PESSOAL_8_20261105.md").read_text(encoding="utf-8")
MATRIX = json.loads((ROOT / "docs/pedagogia/MATRIZ_RASTREABILIDADE_102_RM06_20261105.json").read_text(encoding="utf-8"))
ROWS = re.findall(r"^\|\s*\d+\s*\|\s*([A-Z]+-\d{2})\s*—.*?`(tests/[\w./]+\.py)::(\w+)\.(\w+)`", DOC, re.M)


class Mvp8TraceabilityTests(unittest.TestCase):
    def test_exatamente_oito_cenarios_distintos(self):
        self.assertEqual(len(ROWS), 8)
        self.assertEqual(len({r[0] for r in ROWS}), 8)

    def test_cada_referencia_resolve_para_um_metodo_de_teste_real(self):
        for sid, path, cls, method in ROWS:
            with self.subTest(sid):
                module = importlib.import_module(path[:-3].replace("/", "."))
                self.assertTrue(callable(getattr(getattr(module, cls), method)), f"{sid}: {path}::{cls}.{method}")

    def test_cenarios_do_mvp8_constam_na_matriz_como_parciais_nunca_pass(self):
        status = {row["scenario_id"]: row["status"] for row in MATRIX["scenarios"]}
        for sid, *_ in ROWS:
            self.assertEqual(status[sid], "PARTIAL", sid)
        self.assertEqual(MATRIX["status_counts"]["PASS"], 0)

    def test_documento_nao_promete_homologacao(self):
        self.assertIn("Não equivale à homologação integral de GP-3", DOC)


if __name__ == "__main__":
    unittest.main()
