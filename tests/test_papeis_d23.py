"""A D-23 e os documentos que a aplicam precisam concordar (papéis dos três modelos)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ler(caminho):
    return (ROOT / caminho).read_text(encoding="utf-8")


class PapeisD23Tests(unittest.TestCase):
    def test_d23_define_os_quatro_papeis_e_a_regra_de_entrega(self):
        d23 = next(l for l in ler("PRODUCT.md").splitlines() if l.startswith("- **D-23"))
        for trecho in ("Tutor", "autor editorial", "Gemini Notebook", "rascunho", "Zapia", "comando assinado",
                       "Claude de engenharia", "`verificado`", "rascunho"):
            self.assertIn(trecho, d23)

    def test_documentos_aplicam_a_d23(self):
        self.assertIn("S2-R10", ler("docs/especificacoes/S2_TUTOR.md"))
        self.assertIn("D-23", ler("docs/especificacoes/S5_ZAPIA.md"))
        self.assertIn("D-23", ler("agents/ZAPIA.md"))
        self.assertIn("review_provenance", ler("PRODUCT.md"))
        self.assertIn("review_provenance", ler("docs/especificacoes/S2_TUTOR.md"))
        self.assertIn("D-23", ler("memory/HANDOFF.md"))

    def test_zapia_nao_redige_conteudo_nem_a_pedido_direto(self):
        zapia = ler("agents/ZAPIA.md")
        self.assertIn("não o redige", zapia)
        self.assertIn("rascunho fora do harness", zapia)
        self.assertIn("não escreve prompt de revisão", zapia)


if __name__ == "__main__":
    unittest.main()
