"""O registro de P1 e P3 não pode virar prova indevida, habilitar escrita nem carregar dado pessoal."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "RESULTADO_PERSISTENCIA_P1_P3_20261115.md").read_text(encoding="utf-8")
TEXTO = DOC.replace("*", "").lower()


class ResultadoP1P3Tests(unittest.TestCase):
    def test_declara_relato_e_ausencia_de_verificacao_independente(self):
        for trecho in ("relato do proprietário", "o agente construtor não verificou nada", "não habilita a escrita",
                       "relato"):
            self.assertIn(trecho, TEXTO)
        self.assertIn("sem prova independente", (ROOT / "docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md")
                      .read_text(encoding="utf-8"))

    def test_primeira_tentativa_nao_gravou_e_segunda_gravou(self):
        self.assertIn("consentimento não registrado", TEXTO)
        self.assertIn("nada gravado", TEXTO)
        self.assertIn("readback", TEXTO)
        self.assertRegex(DOC, r"1db27796a192171e1c8ac9b5912591472d3946f6")

    def test_controles_pendentes_continuam_pendentes(self):
        for trecho in ("p4", "p7", "p8", "pr-010", "open-01", "open-02", "não estão provados"):
            self.assertIn(trecho, TEXTO)
        self.assertIn("a flag `personal_results_writes_enabled` continua `false`", TEXTO)

    def test_sem_dado_pessoal_nem_credencial(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}")
        self.assertNotIn("notebook.google.com", DOC)

    def test_flag_de_escrita_pessoal_continua_falsa(self):
        configuracao = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIsNotNone(re.search(r'"personal_results_writes_enabled":\s*false', json.dumps(configuracao, indent=2)))

    def test_documentos_apontam_para_o_registro(self):
        for caminho in ("memory/HANDOFF.md", "docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md"):
            self.assertIn("RESULTADO_PERSISTENCIA_P1_P3_20261115.md", (ROOT / caminho).read_text(encoding="utf-8"), caminho)


if __name__ == "__main__":
    unittest.main()
