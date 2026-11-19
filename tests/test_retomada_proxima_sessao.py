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
        self.assertEqual(ids[6:], ["S12", "S13", "S7", "S6", "C4", "RUNNER", "HOOK", "COMANDOS", "CODEOWNERS", "C3", "S9", "S10", "L1", "S11", "E1", "N2", "Z1", "E2", "HOOK2", "L2", "E3", "E4", "C5R", "V4", "V4F", "C6A", "C6B", "C6C", "C6D", "C5P", "C6", "C5F", "C5G", "E7", "PROJ"])
        saida = subprocess.run([sys.executable, "scripts/next_task.py"], cwd=ROOT, capture_output=True, text=True, timeout=60)
        fila = json.loads(saida.stdout)["fila"]
        # tudo até a L2 tem a entrega; sobram S11 e E3, ambas esperando insumo do proprietário: nenhum item liberado
        self.assertIsNone(fila["proximo"])
        self.assertEqual(fila["pendentes"], ["S11", "E3"])
        self.assertEqual([b["id"] for b in fila["bloqueados"]], ["S11", "E3"])
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
                self.assertRegex(item["deliverable"], r"^(?:scripts/[a-z0-9_]+\.py|\.claude/settings\.json|\.github/CODEOWNERS|scripts/termux/[a-z0-9_]+\.sh|docs/governanca/E[0-9]+_[A-Z0-9_]+\.md|docs/governanca/PROMPT_[A-Z0-9_]+\.md|\.claude/hooks/[a-z0-9_]+\.py)$")
            self.assertTrue(set(item["depends_on"]) <= ids, item["id"])
            self.assertIn(f"| {item['roadmap_task']} |", roadmap, item["id"])
        for novo in ("S11", "E3"):  # ainda por fazer; S10, L1, E1 e N2 já têm a entrega
            item = next(i for i in WORKFLOW["work_queue"] if i["id"] == novo)
            self.assertFalse((ROOT / item["deliverable"]).exists(), novo)  # ainda por escrever

    def test_e1_n2_l2_entram_em_serie_depois_da_s11_por_decisao_do_proprietario(self):
        fila = {i["id"]: i for i in WORKFLOW["work_queue"]}
        self.assertEqual([fila[k]["depends_on"] for k in ("E1", "N2", "Z1", "L2")], [["S10"], ["E1"], ["N2"], ["N2", "Z1"]])
        self.assertEqual(fila["E2"]["depends_on"], ["Z1"])  # decisão de 18/11/2026: a E2 não espera a L2
        self.assertEqual(fila["E1"]["deliverable"], "docs/governanca/E1_EMENDA_PRODUCT_20261118.md")
        self.assertEqual(fila["N2"]["deliverable"], "scripts/notebook_prompt_validator.py")
        self.assertEqual(fila["L2"]["deliverable"], "scripts/tec_export_converter.py")
        self.assertIn("pedido de merge explícito", fila["E1"]["title"])
        self.assertIn("sem convenção de contagem presumida", fila["L2"]["title"])
        for k in ("E1", "N2", "Z1", "E2", "L2"):
            self.assertEqual(fila[k]["blocking_inputs"], [], k)  # o relatório da Zapia chegou e o formato foi decidido (18/11/2026)
        # a E3 espera a decisão do risco diário (depois da Z1) e a aprovação em agents/ (decisão de 18/11/2026)
        self.assertEqual(len(fila["E3"]["blocking_inputs"]), 1)
        self.assertIn("pedidos diários", fila["E3"]["blocking_inputs"][0])
        self.assertIn("depois do resultado da Z1", fila["E3"]["blocking_inputs"][0])
        self.assertIn("agents/", fila["E3"]["blocking_inputs"][0])
        self.assertIn("tabela estruturada", fila["L2"]["title"])
        self.assertEqual(fila["E3"]["depends_on"], ["E2", "L2"])  # a L2 vem primeiro (decisão de 18/11/2026)
        self.assertEqual(fila["E3"]["deliverable"], "docs/governanca/E3_OPERACAO_PEDIR_RELATORIO_20261118.md")
        self.assertIn("aprovação explícita", fila["E3"]["title"])
        self.assertIn("compartilhada pelo Tutor e pelo Coach", fila["E3"]["title"])  # decisão de 18/11/2026: o Coach também pode solicitar
        self.assertIn("Tutor ou pelo Coach", fila["E2"]["title"])
        self.assertEqual(fila["HOOK2"]["depends_on"], ["E2"])  # pedido de 18/11/2026, prazo 20/11
        self.assertEqual(fila["HOOK2"]["deliverable"], ".claude/hooks/entrega_final.py")
        self.assertIn("até 20/11/2026", fila["HOOK2"]["title"])
        self.assertIn("no máximo 1 por dia e só com atividade concluída", fila["E3"]["title"])  # decisão de 18/11/2026
        self.assertIn("bloco `procedimento`", fila["L2"]["title"])
        self.assertIn("não interpreta o conteúdo", fila["E2"]["title"])
        for termo in ("S5", "S4-R2", "S9-R1", "S4"):
            self.assertIn(termo, fila["E2"]["title"])
        self.assertEqual(fila["Z1"]["deliverable"], "docs/governanca/PROMPT_TESTE_EXPORTACAO_TEC_ZAPIA_20261118.md")

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
