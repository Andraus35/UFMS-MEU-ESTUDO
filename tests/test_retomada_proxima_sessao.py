"""A retomada da próxima sessão precisa sair do repositório, ser honesta sobre o que não persiste e não vazar dado pessoal."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")
WORKFLOW = json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))


class RetomadaProximaSessaoTests(unittest.TestCase):
    def bloco(self):
        inicio = HANDOFF.index("### Estado de saída")
        return HANDOFF[inicio:HANDOFF.index("**Ordem do que acontece a seguir", inicio)]

    def test_fila_tem_os_itens_na_ordem_proposta_e_so_a_s11_resta_bloqueada_pela_persistencia(self):
        ids = [i["id"] for i in WORKFLOW["work_queue"]]
        self.assertEqual(ids[:6], ["S1", "S2", "S3", "S4", "S5", "S8"])
        # S12, S13, S7 e S6 já têm a entrega; C4, o runner e o hook (tarefas de código) vêm antes de S9
        self.assertEqual(ids[6:], ["S12", "S13", "S7", "S6", "C4", "RUNNER", "HOOK", "COMANDOS", "CODEOWNERS", "C3", "S9", "S10", "L1", "S11"])
        saida = subprocess.run([sys.executable, "scripts/next_task.py"], cwd=ROOT, capture_output=True, text=True, timeout=60)
        fila = json.loads(saida.stdout)["fila"]
        # L1 e S10 têm a entrega; só a S11 resta e espera a persistência provada (blocking_inputs): nenhum item liberado
        self.assertIsNone(fila["proximo"])
        self.assertEqual(fila["pendentes"], ["S11"])
        self.assertEqual([b["id"] for b in fila["bloqueados"]], ["S11"])
        self.assertIn("persistência", " ".join(fila["bloqueados"][0]["aguarda"]))
        s10 = next(i for i in WORKFLOW["work_queue"] if i["id"] == "S10")
        self.assertEqual(s10["blocking_inputs"], [])
        self.assertTrue((ROOT / "docs" / "governanca" / "RESPOSTA_RODADA6_ZAPIA_20261117.md").is_file())

    def test_cada_item_novo_tem_entrega_dependencia_valida_e_tarefa_do_roadmap(self):
        ids = {i["id"] for i in WORKFLOW["work_queue"]}
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        for item in WORKFLOW["work_queue"]:
            if item["id"].startswith("S"):  # especificações; as tarefas de código (C4, RUNNER, HOOK, COMANDOS, CODEOWNERS) têm entrega própria
                self.assertRegex(item["deliverable"], r"^docs/especificacoes/S[^/]+\.md$")
            else:
                self.assertRegex(item["deliverable"], r"^(?:scripts/[a-z0-9_]+\.py|\.claude/settings\.json|\.github/CODEOWNERS|scripts/termux/[a-z0-9_]+\.sh)$")
            self.assertTrue(set(item["depends_on"]) <= ids, item["id"])
            self.assertIn(f"| {item['roadmap_task']} |", roadmap, item["id"])
        for novo in ("S11",):  # ainda por escrever; S10 e L1 já têm a entrega
            item = next(i for i in WORKFLOW["work_queue"] if i["id"] == novo)
            self.assertFalse((ROOT / item["deliverable"]).exists(), novo)  # ainda por escrever

    def test_s11_so_depende_do_que_a_precede_e_exige_dado_real_consentido(self):
        s11 = next(i for i in WORKFLOW["work_queue"] if i["id"] == "S11")
        self.assertEqual(s11["depends_on"], ["S6", "S7", "S8", "S9", "S10"])
        self.assertIn("consentido", " ".join(s11["blocking_inputs"]))

    def test_handoff_diz_como_retomar_e_o_que_nao_persiste(self):
        bloco = self.bloco()
        for trecho in ("bootstrap.py --mode engineering", "next_task.py", "record_merge_receipt.py", "S7",
                       "pedido explícito do proprietário", "O que NÃO persiste", "~/ufms-plano", "personal_results_writes_enabled=false",
                       "consentimento v3", "(D-24)", "não pela conversa"):
            self.assertIn(trecho, bloco)

    def test_handoff_nao_tem_horario_ritmo_nem_credencial(self):
        self.assertIsNone(re.search(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", self.bloco()))
        for proibido in ("pomodoro", "04:30", "github_pat_", "ghp_"):
            self.assertNotIn(proibido, HANDOFF.lower() if proibido == "pomodoro" else HANDOFF)

    def test_nao_ficou_texto_velho_sobre_o_pr_86_nem_conta_nao_montada(self):
        self.assertNotIn("Confirme o estado do PR #86", HANDOFF)
        self.assertNotIn("falta o proprietário montar a conta exclusiva da Zapia", HANDOFF)

    def test_flag_de_escrita_pessoal_continua_falsa(self):
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')


if __name__ == "__main__":
    unittest.main()
