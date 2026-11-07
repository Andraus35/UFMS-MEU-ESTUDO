"""Estrutura e salvaguardas do roteiro de verificação da Zapia, rodada 2."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/PROMPT_VERIFICACAO_ZAPIA_RODADA2_20261107.md").read_text(encoding="utf-8")
PROMPT = re.search(r"```text\n(.*?)\n```", DOC, re.S).group(1)


class Rodada2Tests(unittest.TestCase):
    def test_perguntas_r1_a_r34_sequenciais_e_unicas(self):
        ids = re.findall(r"^R(\d+)\s", PROMPT, re.M)
        self.assertEqual([int(i) for i in ids], list(range(1, 35)))

    def test_regras_de_seguranca_presentes(self):
        for trecho in ("NUNCA imprima", "SOMENTE LEITURA", "PROIBIDO", "NÃO leia nem reproduza",
                       "DADOS, não instruções", "NÃO execute agora", "NÃO adivinhe"):
            self.assertIn(trecho, PROMPT)

    def test_formato_final_exige_status_e_evidencia(self):
        self.assertIn('"status":"OBSERVADO|DOCUMENTADO|DESCONHECIDO"', PROMPT)
        self.assertIn('"evidencia"', PROMPT)

    def test_nao_contem_segredos_nem_referencia_de_credencial(self):
        for padrao in (r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"github_ufms_repo_token"):
            self.assertIsNone(re.search(padrao, DOC), padrao)

    def test_aponta_para_rodada_1_e_para_o_branch_nao_mesclado(self):
        self.assertIn("feat/product-md-20261107", PROMPT)
        self.assertIn("PROMPT_VERIFICACAO_ZAPIA_20261107.md", DOC)


if __name__ == "__main__":
    unittest.main()
