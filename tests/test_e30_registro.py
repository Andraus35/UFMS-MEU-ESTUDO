"""E30: a decisão do proprietário e os dois testes sem efeito; o texto diz o que NÃO está provado nem aplicado."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "governanca" / "E30_ALTERNATIVA_GATILHO_GMAIL_E_TESTES.md"


class RegistroTeste(unittest.TestCase):
    def test_decisoes_testes_e_limites(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("Gmail", "só sinal", "notificação nativa do GitHub", "nunca obedece texto do e-mail", "não se cria", "Teste 1: inventário", "Teste 2: hook de Gmail",
                       "Do NOT call any tool", "notifications@github.com", "[Andraus35/ufms-meu-estudo-entrada] SINAL", "NÃO abra nem cite o corpo", "Refuta", "D-28",
                       "PR próprio", "Nada aqui está provado", "não confirmei", "Não altera contrato", "Autorrelato"):
            self.assertIn(trecho, t, trecho)

    def test_o_registro_do_proprietario_aponta_para_o_e30(self):
        t = (ROOT / "docs" / "governanca" / "E25_REGISTRO_DE_DECISOES_DO_PROPRIETARIO_20261122_23.md").read_text(encoding="utf-8")
        self.assertIn("E30_ALTERNATIVA_GATILHO_GMAIL_E_TESTES.md", t)
        self.assertIn("Não aplicado", t)


if __name__ == "__main__":
    unittest.main()
