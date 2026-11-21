"""A E3 é só proposta de texto: não altera agents/, o esquema de comandos nem o gate; distingue comando de evento."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "E3_OPERACAO_PEDIR_RELATORIO_20261118.md").read_text(encoding="utf-8")
T = DOC.replace("**", "").replace("`", "").lower()


class E3PropostaTests(unittest.TestCase):
    def test_e_proposta_e_nao_aplica_nada(self):
        for trecho in ("proposta de texto", "nada aqui está aplicado", "não altera agents/", "duas aprovações expressas",
                       "lote seguinte", "não aplica nenhuma mudança"):
            self.assertIn(trecho, T, trecho)

    def test_distingue_comando_de_evento(self):
        for trecho in ("agente → zapia", "proprietário → zapia → agentes", "a zapia só executa", "fila entrada",
                       "estudo_iniciado", "estudo_finalizado", "estudo de hoje finalizado."):
            self.assertIn(trecho, T, trecho)

    def test_operacao_compartilhada_com_parametros_e_limite_fechados(self):
        for trecho in ("pedir_relatorio_desempenho", "compartilhada", "shared", "zapia_relatorio", "modalidade", "cargo", "recorte",
                       "até 2 pedidos por dia", "um por plataforma", "gemini_notebook", "só com atividade concluída", "nunca grava"):
            self.assertIn(trecho, T, trecho)

    def test_decisoes_pedidas(self):
        for trecho in ("decisão a1", "b1 (decidida", "iniciar estudos", "b1b (pendente)", "finalizar estudos", "b2 (decidida", "emenda à s7",
                       "flag de escrita", "e3-c (pendente)", "compartilha com o coach"):
            self.assertIn(trecho, T, trecho)

    def test_o_esquema_e_o_gate_continuam_sem_a_operacao(self):
        schema = json.loads((ROOT / "config" / "agent_command_schema.json").read_text(encoding="utf-8"))
        self.assertNotIn("pedir_relatorio_desempenho", schema["destinations"])
        self.assertNotIn("zapia_relatorio", schema["destinations"].values())
        for caminho in ("scripts/agents_gate.py", "agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md", "AGENTS.md"):
            self.assertNotIn("pedir_relatorio_desempenho", (ROOT / caminho).read_text(encoding="utf-8"), caminho)

    def test_mantem_a_liberacao_a_flag_e_nao_tem_dado_pessoal(self):
        self.assertIn("d-27", T)
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"ghp_|github_pat_|Bearer\s")

    def test_fila_aponta_para_a_proposta(self):
        item = next(i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"] if i["id"] == "E3")
        self.assertEqual(item["deliverable"], "docs/governanca/E3_OPERACAO_PEDIR_RELATORIO_20261118.md")
        self.assertTrue((ROOT / item["deliverable"]).exists())


if __name__ == "__main__":
    unittest.main()
