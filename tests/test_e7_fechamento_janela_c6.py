"""E7: a janela da C6 foi fechada; o registro diz o que foi provado e como o fechamento passa a valer."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/E7_FECHAMENTO_JANELA_C6_20261118.md").read_text(encoding="utf-8")
CFG = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))["storage"]


class FechamentoTests(unittest.TestCase):
    def test_as_duas_flags_estao_falsas_em_repouso(self):
        self.assertIs(CFG["private_flow_promotion_enabled"], False)
        self.assertIs(CFG["personal_results_writes_enabled"], False)

    def test_registro_diz_o_que_foi_provado_e_o_que_nao(self):
        for t in ("44421234167", "0 para 1 evento", "`sintetico=true`, `escritor=fluxo` e `entregue_por=zapia`", "recibos/c5-sintetica-",
                  "Não provado", "projeções lidas por sessões", "relato do proprietário", "sem prova independente"):
            self.assertIn(t, DOC, t)

    def test_fechamento_exige_reinstalar_e_retirar_o_acesso_de_leitura(self):
        for t in ("ATUALIZAR", "Mesclar sem reinstalar NÃO desliga o fluxo", "Claude GitHub App", "nunca vale para `dados`",
                  "aprovação expressa", "descartar_sinteticos"):
            self.assertIn(t, DOC, t)


if __name__ == "__main__":
    unittest.main()
