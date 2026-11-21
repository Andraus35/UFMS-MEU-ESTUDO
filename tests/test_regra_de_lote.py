"""Regra de merge por lote (decisão do proprietário, 21/11/2026): o AGENTS.md precisa carregá-la inteira e sem relaxar o resto."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
BLOCO = AGENTS[AGENTS.index("**Lote de entrega e merge"):AGENTS.index("**Regra de transição pós-merge:**")]


class RegraDeLoteNoAgents(unittest.TestCase):
    def test_bloco_unico_e_antes_da_transicao_pos_merge(self):
        self.assertEqual(AGENTS.count("**Lote de entrega e merge"), 1)

    def test_cinco_itens_numerados(self):
        for n in range(1, 6):
            self.assertIn(f"({n})", BLOCO, n)

    def test_merge_apos_lote_micro_tarefas_uma_por_vez_no_mesmo_pr(self):
        for trecho in ("a unidade de merge é o **lote**", "O merge ocorre **após um lote de entrega**", "continuam **uma por vez**", "mesmo PR draft", "mesma branch"):
            self.assertIn(trecho, BLOCO)

    def test_coesao_obrigatoria_e_vizinhanca_nao_forma_lote(self):
        for trecho in ("interdependentes e coesas", "mesma frente ou bloco de trabalho", "insumo, verificação ou correção", "**não** forma lote"):
            self.assertIn(trecho, BLOCO)

    def test_outra_frente_exige_mesclar_antes_e_proibe_paralelismo(self):
        for trecho in ("outra frente ou bloco", "**mesclado antes** de iniciar o próximo", "**proibido** abrir PR ou branch paralelos", "misturar frentes no mesmo PR"):
            self.assertIn(trecho, BLOCO)

    def test_merge_segue_so_por_pedido_expresso_e_nao_relaxa_gates(self):
        for trecho in ("só por pedido expresso do proprietário", "citando PR e head", "não** vale para a janela do piloto", "CI verde no head exato",
                       "**não** relaxa os gates", "aprovação expressa para arquivos de contrato"):
            self.assertIn(trecho, BLOCO)

    def test_regra_antiga_de_um_pr_draft_por_vez_segue_no_documento_e_no_workflow(self):
        self.assertIn("**Não abrir PRs/branches paralelos, empilhados ou exclusivos para auditoria/correção**", AGENTS)
        rules = json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["rules"]
        self.assertEqual((rules["max_open_pull_requests"], rules["max_active_work_branches"], rules["allow_parallel_work"], rules["allow_concurrent_prs"]),
                         (1, 1, False, False))

    def test_handoff_registra_a_decisao_e_a_data(self):
        handoff = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("REGRA PERMANENTE DE MERGE POR LOTE", handoff)
        self.assertIn("21/11/2026", handoff)


if __name__ == "__main__":
    unittest.main()
