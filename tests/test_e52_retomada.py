"""E52: o ponto de retomada de 27 e 28/11/2026 existe, está visível no HANDOFF, traz o que a próxima sessão precisa e a fila tem os itens com o que os bloqueia."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/E52_RETOMADA_PROXIMA_SESSAO_20261128.md").read_text(encoding="utf-8")
HANDOFF = (ROOT / "memory/HANDOFF.md").read_text(encoding="utf-8")
WORKFLOW = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
sys.path.insert(0, str(ROOT / "scripts"))
import canal_engenharia as ce  # noqa: E402


class RetomadaE52Test(unittest.TestCase):
    def test_o_handoff_aponta_para_o_registro_no_inicio_e_arquiva_os_blocos_antigos(self):
        i = HANDOFF.index("E52_RETOMADA_PROXIMA_SESSAO_20261128.md")
        self.assertLess(i, 4500)  # visível no começo do arquivo lido no START
        self.assertIn("LEITURA OBRIGATÓRIA DA PRÓXIMA SESSÃO", HANDOFF[i - 100:i])
        self.assertLess(i, HANDOFF.index("E46_RETOMADA_PROXIMA_SESSAO_20261125_26.md"))
        arq = (ROOT / "docs/governanca/ARQUIVO_HANDOFF_SESSAO_20261125_26.md").read_text(encoding="utf-8")
        for trecho in ("LOTE PROMPT-NOTEBOOK-C1", "LOTE KIT-N1-C1", "DECISÃO C1"):
            self.assertIn(trecho, arq)
            self.assertNotIn("**" + trecho, HANDOFF)

    def test_o_registro_traz_estado_rodadas_decisoes_atos_e_ordem(self):
        for trecho in ("206306492cb6dbc7002bf7e2c26a81ffa86eee11", "#213", "9f622bbf", "v10", "--prompt-hook", "eng-0005", "operawao", "HTTP 403", "Issues: Read and write",
                       "config/rotina_despertar_prompt.txt", "666d66c7a200be9ca2ac75c42d10a5509b398ab1b02c573f0397b3901a90dda7", "Criar a tarefa S22", "NÃO fechar nem comentar",
                       "revogação é ato dele", "__pycache__", "git merge -s ours", "orquestrador único", "RM-08", "ENG-V10-HOOK", "ENG-DESPERTAR",
                       "RODADA-NO-START", "intercambiáveis", "Dê o prompt completo ao proprietário em toda resposta"):
            self.assertIn(trecho, DOC, trecho)

    def test_a_fila_tem_os_tres_itens_novos_com_bloqueio_e_dependencia(self):
        fila = {i["id"]: i for i in WORKFLOW["work_queue"]}
        self.assertEqual([i["id"] for i in WORKFLOW["work_queue"]][-3:], ["ENG-V10-HOOK", "ENG-DESPERTAR", "RODADA-NO-START"])
        self.assertTrue(fila["ENG-V10-HOOK"]["blocking_inputs"])
        self.assertEqual(fila["ENG-DESPERTAR"]["depends_on"], ["ENG-V10-HOOK"])
        self.assertEqual(fila["RODADA-NO-START"]["depends_on"], ["ENG-DESPERTAR"])
        for id_ in fila:
            if id_ in ("ENG-V10-HOOK", "ENG-DESPERTAR", "RODADA-NO-START"):
                self.assertFalse((ROOT / fila[id_]["deliverable"]).exists(), id_)  # a entrega só existe quando o trabalho for feito

    def test_o_proximo_item_liberado_e_o_do_n1_e_os_novos_ficam_bloqueados(self):
        saida = subprocess.run([sys.executable, "scripts/next_task.py"], cwd=ROOT, capture_output=True, text=True, timeout=60)
        fila = json.loads(saida.stdout)["fila"]
        self.assertEqual(fila["proximo"]["id"], "N1-RODADA-4")
        self.assertIn("ENG-V10-HOOK", [b["id"] for b in fila["bloqueados"]])

    def test_o_workflow_cabe_no_limite_do_start(self):
        tam = len((ROOT / "state/WORKFLOW.json").read_bytes())
        self.assertLess(tam, 64 * 1024, tam)  # o START recusa documento acima de 64 KiB: arquive antes de crescer

    def test_o_prompt_de_atualizacao_do_hook_sai_do_codigo(self):
        self.assertIn("INICIO " + ce.hook_engenharia(ce.REPO_ENTRADA) + " FIM", ce.prompt_atualizar_hook(ce.REPO_ENTRADA))


if __name__ == "__main__":
    unittest.main()
