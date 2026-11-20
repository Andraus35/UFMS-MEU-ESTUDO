"""Prioridade persistente dos atos do proprietário que mais destravam trabalho (state/WORKFLOW.json, decisão de 18/11/2026)."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import next_task  # noqa: E402

WF = json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))
PRI = WF["owner_priorities"]
FILA = {i["id"] for i in WF["work_queue"]}


class PrioridadesDoProprietarioTests(unittest.TestCase):
    def test_nove_itens_em_ordem_com_campos_obrigatorios(self):
        self.assertEqual([i["rank"] for i in PRI], [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual([i["id"] for i in PRI], ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"])
        for i in PRI:
            for campo in ("rank", "id", "ato", "destrava", "destrava_itens", "depende_de", "esforco", "estado"):
                self.assertIn(campo, i, (i["id"], campo))
            self.assertIn(i["estado"], {"pendente", "feito"})
            self.assertTrue(i["ato"].strip() and i["destrava"].strip())

    def test_a_ordem_e_a_que_o_proprietario_pediu(self):
        ordem = [i["ato"].lower() for i in PRI]
        for k, trecho in enumerate(("z1", "risco do tec", "c3", "consentimento v4", "reconfirmar o merge", "c6")):
            self.assertIn(trecho, ordem[k], (k, trecho))
        self.assertIn("autorizo tec-export-1", ordem[0])

    def test_dependencias_apontam_para_itens_anteriores_e_destravas_para_a_fila(self):
        ids = [i["id"] for i in PRI]
        for i in PRI:
            for d in i["depende_de"]:
                self.assertIn(d, ids[:ids.index(i["id"])], (i["id"], d))
            for item in i["destrava_itens"]:
                self.assertIn(item, FILA, (i["id"], item))
        self.assertEqual(next(i for i in PRI if i["id"] == "P2")["depende_de"], ["P1"])
        self.assertEqual(next(i for i in PRI if i["id"] == "P6")["depende_de"], ["P3", "P4"])

    def test_next_task_lista_so_os_pendentes_em_ordem(self):
        r = next_task.owner_priorities(WF)
        self.assertEqual([i["id"] for i in r], [i["id"] for i in sorted(PRI, key=lambda x: x["rank"]) if i["estado"] != "feito"])
        wf = copy.deepcopy(WF)
        for i in wf["owner_priorities"]:
            i["estado"] = "pendente"
        wf["owner_priorities"][0]["estado"] = "feito"
        wf["owner_priorities"] = list(reversed(wf["owner_priorities"]))
        r = next_task.owner_priorities(wf)
        self.assertEqual([i["id"] for i in r], ["P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"])  # feito sai; a ordem vem do rank, não da posição
        self.assertEqual(next_task.owner_priorities({}), [])

    def test_a_saida_do_script_traz_a_lista_e_nao_altera_a_fila(self):
        out = subprocess.run([sys.executable, "scripts/next_task.py"], cwd=ROOT, capture_output=True, text=True, timeout=60)
        d = json.loads(out.stdout)
        self.assertEqual(len(d["desbloqueios_do_proprietario"]), len([i for i in PRI if i["estado"] != "feito"]))
        self.assertIn("pendentes", d["fila"])
        wf = copy.deepcopy(WF)
        wf["owner_priorities"] = []
        self.assertEqual(next_task.queue_status(ROOT, WF)["pendentes"], next_task.queue_status(ROOT, wf)["pendentes"])

    def test_nao_e_fila_de_engenharia_nem_cria_pr(self):
        self.assertIn("não é fila de engenharia e não cria branch nem PR", WF["owner_priorities_note"])
        self.assertTrue({"P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"}.isdisjoint(FILA))
        self.assertEqual(WF["policy"], "single_branch_single_pr_single_merge")

    def test_handoff_cita_a_lista_persistente(self):
        h = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("owner_priorities", h)
        for ident in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"):
            self.assertIn(ident, h, ident)


if __name__ == "__main__":
    unittest.main()
