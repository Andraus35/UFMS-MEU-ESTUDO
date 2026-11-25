"""E29: o registro diz o que o teste mede e, sobretudo, o que NÃO prova (autorrelato, fluxo, vários dias, gh real)."""
import unittest
from pathlib import Path

DOC = Path(__file__).resolve().parents[1] / "docs" / "governanca" / "E29_ROTINA_CRIA_ROTINA_TESTE_F3.md"


class RegistroTeste(unittest.TestCase):
    def test_diz_o_que_mede_e_o_que_nao_prova(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("ctx_leitura_real.py", "zapia_poller.py", "prova_f3_zapia.sh", "90 min", "não provado", "SINTETICO_MANUAL", "autorrelato",
                       "captura da lista de rotinas do app", "pin", "Se a Zapia NÃO conseguir criar rotina de dentro de rotina", "refuta a hipótese",
                       "não foi executado com o `gh` real", "Promoção pelo fluxo", "pontualidade em vários dias", "pedido expresso", "S20-R9", "REFUTADO", "I cannot create a routine from inside a routine"):
            self.assertIn(trecho, t, trecho)


if __name__ == "__main__":
    unittest.main()
