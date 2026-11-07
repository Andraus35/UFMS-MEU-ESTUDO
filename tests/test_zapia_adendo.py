"""O adendo registra só o delta, não substitui a rodada 2 e é consistente com as POCs."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/ADENDO_AUDITORIA_ZAPIA_20261107.md").read_text(encoding="utf-8")
PRODUCT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")


class AdendoTests(unittest.TestCase):
    def test_declara_que_nao_responde_a_rodada_2(self):
        self.assertIn("**não é** a resposta da rodada 2", DOC)
        self.assertIn("R1 a R34 seguem sem resposta", DOC)

    def test_commits_citados_batem_com_os_registros_das_poc(self):
        poc5 = (ROOT / "poc/POC-UFMS-005.json").read_text(encoding="utf-8")
        poc7 = (ROOT / "poc/POC-UFMS-007.json").read_text(encoding="utf-8")
        self.assertIn("747f239c823e1bfc5eea87130406ff85b9bc6707", poc5)
        self.assertIn("9a2c46b3eb9fa7d0eac6040be6f08c1490b65874", poc7)
        for curto in ("747f239", "9a2c46b", "220ef55"):
            self.assertIn(curto, DOC)

    def test_nao_contem_segredos(self):
        for padrao in (r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"github_ufms_repo_token"):
            self.assertIsNone(re.search(padrao, DOC), padrao)

    def test_product_incorpora_as_licoes_da_poc_008(self):
        self.assertIn("E-07", PRODUCT)
        self.assertIn("OPEN-06", PRODUCT)
        self.assertIn("recusa de lembrete para atividade já concluída", PRODUCT)
        self.assertIn("nunca de forma ampla", PRODUCT)

    def test_testes_sinteticos_seguem_nao_executados(self):
        self.assertIn("não executados", DOC)


if __name__ == "__main__":
    unittest.main()
