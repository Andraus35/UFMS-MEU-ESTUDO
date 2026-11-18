"""C6: a flag do fluxo é ligada só por este PR de janela; a do público nunca liga; o registro diz como fechar a janela."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/E6_C6_LIGA_FLAG_DO_FLUXO_20261118.md").read_text(encoding="utf-8")
CFG = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))["storage"]


class FlagDoFluxoTests(unittest.TestCase):
    def test_estado_da_janela(self):
        # a janela da C6 foi aberta pelo PR #132 e fechada pelo PR de fechamento (E7): em repouso a flag do fluxo é falsa
        self.assertIs(CFG["private_flow_promotion_enabled"], False)
        self.assertIs(CFG["personal_results_writes_enabled"], False)

    def test_registro_diz_como_fechar_a_janela_e_o_que_ligar_nao_faz(self):
        for t in ("aprovação expressa", "ATUALIZAR", "SHA que fixa", "Mesclar o PR sem reinstalar NÃO desliga o fluxo",
                  "volta `private_flow_promotion_enabled` a `false`", "PR único", "permanece", "sintético", "v4",
                  "Não habilita leitura por sessões", "não muda, nunca liga"):
            self.assertIn(t, DOC, t)

    def test_pre_condicoes_do_codigo_existem(self):
        for caminho in ("scripts/session_read_guard.py", "scripts/termux/prova_c5_promocao.sh", "scripts/c5_entrada_sintetica.py",
                        "scripts/termux/ufms.sh"):
            self.assertTrue((ROOT / caminho).is_file(), caminho)
        runner = (ROOT / "scripts/promotion_runner.py").read_text(encoding="utf-8")
        self.assertIn("consent-v4.json", runner)  # a promoção exige o v4


if __name__ == "__main__":
    unittest.main()
