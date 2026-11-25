"""Contrato da E4: D-28 emenda o D-21 sem autorizar leitura de e-mail e sem estourar o orçamento do PRODUCT.md."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")
REGISTRO = (ROOT / "docs" / "governanca" / "E4_EMENDA_D21_OUTLOOK_20261118.md").read_text(encoding="utf-8")


def bullet(ident):
    m = re.search(rf"^- \*\*{re.escape(ident)}\b.*$", PRODUCT, re.M)
    assert m, ident
    return m.group(0)


class EmendaD21Tests(unittest.TestCase):
    def test_d28_emenda_sem_autorizar_leitura(self):
        d = bullet("D-28").lower()
        for t in ("outlook conectado", "emenda a d-21", "não autoriza", "autorizo", "finalidade não declarada", "e-07"):
            self.assertIn(t, d, t)

    def test_d21_preservada_e_marcada(self):
        d21 = bullet("D-21")
        self.assertIn("emendada pela D-28", d21)
        for t in ("exclui o Outlook", "Mantenho drive e calendar apenas", "AUTORIZO"):
            self.assertIn(t, d21, t)

    def test_orcamento_e_registro(self):
        self.assertLessEqual(len(PRODUCT.encode("utf-8")), 40 * 1024)  # teto 40 KiB com a D-32
        self.assertIn("não autoriza", REGISTRO.lower().replace("**", ""))
        self.assertIn("pedido explícito", REGISTRO)

if __name__ == "__main__":
    unittest.main()
