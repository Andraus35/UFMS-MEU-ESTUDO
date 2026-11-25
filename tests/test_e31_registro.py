"""E31: o registro do teste ponta a ponta diz o que mede, o que refuta e o que NÃO prova."""
import unittest
from pathlib import Path

DOC = Path(__file__).resolve().parents[1] / "docs" / "governanca" / "E31_TESTE_PONTA_A_PONTA_HOOK_ENTREGA.md"


class RegistroTeste(unittest.TestCase):
    def test_diz_o_que_mede_refuta_e_nao_prova(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("prova_f4_hook_entrega.sh", "HOOK_ENTREGA", "senders", "subject_contains", "nunca o corpo", "SINTETICO_MANUAL", "não anterior à criação da issue", "900 s",
                       "Refuta", "S20-R9", "O emissor é ele", "não o fluxo", "emenda do D-28", "não rodou com o `gh` real", "24 h", "autorrelato", "Nada aqui está provado",
                       "Não altera contrato"):
            self.assertIn(trecho, t, trecho)


if __name__ == "__main__":
    unittest.main()
