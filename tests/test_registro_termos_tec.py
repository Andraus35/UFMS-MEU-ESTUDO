"""O registro dos termos do TEC guarda só a conclusão do proprietário: sem copiar o texto, sem parecer jurídico, com o alcance limitado."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "REGISTRO_TERMOS_TEC_20261118.md").read_text(encoding="utf-8")
T = DOC.replace("**", "").replace("`", "").lower()


class RegistroTermosTecTests(unittest.TestCase):
    def test_conclusao_e_alcance_do_risco(self):
        for trecho in ("leu o item 8.1", "conclusão dele: o item veda automação", "assume o risco para a exportação", "suspensa ou bloqueada",
                       "teste da z1 (uma exportação)", "mantém o aceite do d-27", "autorizo tec-export-1"):
            self.assertIn(trecho, T, trecho)

    def test_cumpre_so_a_s9_r8_b_e_nao_a_r9_nem_o_uso_diario(self):
        for trecho in ("cumpre:", "s9-r8", "alínea (b)", "não cumpre: a s9-r9 (aprovação expressa em pr da primeira leitura real", "nem autoriza pedidos recorrentes", "não foi confirmado",
                       "fechando por padrão", "termos_tec_registrados", "qconcursos: inalterado"):
            self.assertIn(trecho, T, trecho)

    def test_e_relato_nao_parecer_juridico_e_nao_copia_o_texto(self):
        for trecho in ("relato dele, não verificado", "não é parecer jurídico", "o texto dos termos não é copiado"):
            self.assertIn(trecho, T, trecho)
        self.assertNotRegex(DOC, r"[“\"]É expressamente proibida")  # sem trecho literal da cláusula
        self.assertNotIn("crawlers, spiders", DOC.lower())

    def test_declara_os_riscos_que_ficam(self):
        for trecho in ("suspensão ou bloqueio da conta", "perda do histórico de questões", "não trava técnica"):
            self.assertIn(trecho, T, trecho)

    def test_sem_dado_pessoal_credencial_nem_estado_do_ciclo(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"ghp_|github_pat_[A-Za-z0-9_]{10}|Bearer\s|https?://")
        self.assertNotRegex(DOC, r"\bPR\s*#\d+")
        self.assertNotRegex(DOC, r"\b[0-9a-f]{40}\b")

    def test_s9_e_e2_apontam_para_o_registro(self):
        for caminho in ("docs/especificacoes/S9_LEITURA_PLATAFORMAS.md", "docs/governanca/E2_EMENDA_S5_S4R2_20261118.md"):
            self.assertIn("REGISTRO_TERMOS_TEC_20261118.md", (ROOT / caminho).read_text(encoding="utf-8"), caminho)


if __name__ == "__main__":
    unittest.main()
