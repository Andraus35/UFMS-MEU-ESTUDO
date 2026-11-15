"""O registro da rodada 5c não pode vazar e-mail nem link do notebook, nem tratar o rascunho como fonte."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "RESPOSTA_RODADA5C_ZAPIA_20261115.md").read_text(encoding="utf-8")


class Rodada5cTests(unittest.TestCase):
    def test_sem_email_nem_link_de_notebook(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotIn("notebook.google.com", DOC)
        self.assertNotRegex(DOC, r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        self.assertNotRegex(DOC, r"https?://")

    def test_declara_autorrelato_rascunho_e_nao_promove_requisito(self):
        texto = DOC.replace("*", "").lower()
        for trecho in ("autorrelato", "rascunho não verificado", "nunca como fonte", "não promove nenhum requisito",
                       "parcial", "abertura de uma citação"):
            self.assertIn(trecho, texto, trecho)

    def test_v9_continua_bloqueado_e_privacidade_nao_informada(self):
        texto = DOC.replace("*", "").lower()
        self.assertIn("continua sem condições de rodar", texto)
        self.assertIn("lei 8.112", texto)
        self.assertIn("não se sabe se o notebook está privado", texto)

    def test_documentos_apontam_para_o_registro(self):
        for caminho in ("docs/especificacoes/S5_ZAPIA.md", "memory/HANDOFF.md"):
            self.assertIn("RESPOSTA_RODADA5C_ZAPIA_20261115.md", (ROOT / caminho).read_text(encoding="utf-8"), caminho)


if __name__ == "__main__":
    unittest.main()
