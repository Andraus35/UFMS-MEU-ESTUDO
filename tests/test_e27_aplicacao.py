"""E27: o registro da aplicação diz o que foi aplicado e, sobretudo, o que NÃO está feito (contexto do runner real, Zapia não executa o código)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "governanca" / "E27_APLICACAO_AGENDAR_ROTINA.md"


class RegistroTeste(unittest.TestCase):
    def test_diz_o_que_foi_aplicado_e_o_que_nao_esta_feito(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("`agendar_rotina`", "compartilhada por Tutor e Coach", "zapia_rotina", "agendar_rotina_enabled", "ROTINA_PARADA", "90 min e 24 h",
                       "1 pedido por dia por origem", "ALVO_NAO_PROMOVIDO", "config/rotina_instrucoes.json", "URLs completos e literais", "nunca `commands`",
                       "O que NÃO está feito", "todo `agendar_rotina` é recusado", "ZAPIA-CTX", "A Zapia não executa este Python", "Origem não provada",
                       "pedido expresso", "proposta de 7 dias"):
            self.assertIn(trecho, t, trecho)

    def test_a_e24_aponta_para_a_aplicacao(self):
        self.assertIn("E27_APLICACAO_AGENDAR_ROTINA.md", (ROOT / "docs" / "governanca" / "E24_PROPOSTA_OPERACAO_AGENDAR_ROTINA.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
