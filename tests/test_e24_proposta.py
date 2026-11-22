"""E24: a proposta da operação `agendar_rotina` existe, traz os pontos para aprovação e NÃO foi aplicada ao contrato (esquema, perfis, gate)."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "governanca" / "E24_PROPOSTA_OPERACAO_AGENDAR_ROTINA.md"


class PropostaTeste(unittest.TestCase):
    def test_a_proposta_traz_os_pontos_para_aprovacao(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("proposta de texto", "nada aqui está aplicado", "`agendar_rotina`", "zapia_rotina", "Só o Coach", "F1_ENTREGA_UNICA",
                       "AUTORIZO", "por turno", "modelo versionado", "15 min e 24 h", "1 pedido por dia", "Autoescalonamento",
                       "Não está provado", "duas aprovações expressas", "recibo de volta"):
            self.assertIn(trecho, t, trecho)

    def test_a_instrucao_nao_vem_do_comando(self):
        t = DOC.read_text(encoding="utf-8")
        self.assertIn("A instrução que a Zapia segue NÃO vem do comando", t)
        self.assertIn("nada de texto livre", t)

    def test_nao_foi_aplicada_ao_contrato(self):
        esquema = json.loads((ROOT / "config" / "agent_command_schema.json").read_text(encoding="utf-8"))
        self.assertNotIn("agendar_rotina", esquema["destinations"])
        self.assertNotIn("zapia_rotina", esquema["destinations"].values())
        for rel in ("agents/COACH.md", "agents/ZAPIA.md", "scripts/command_params_schema.py", "scripts/agents_gate.py", "scripts/command_box.py"):
            self.assertNotIn("agendar_rotina", (ROOT / rel).read_text(encoding="utf-8"), rel)


if __name__ == "__main__":
    unittest.main()
