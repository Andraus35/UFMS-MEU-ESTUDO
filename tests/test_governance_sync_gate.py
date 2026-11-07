"""Adversarial tests for governance state and document synchronization."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.governance_sync_gate import ROOT, verify


class GovernanceSyncGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for rel in ("state/WORKFLOW.json", "memory/HANDOFF.md", "ROADMAP.md",
                    "docs/governanca/STATUS_BRANCHES_RECONCILIADO_20261105.md"):
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)

    def tearDown(self):
        self.temp.cleanup()

    def test_checkpoint_ativo_coerente(self):
        result = verify(self.root)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["state"], "prepared" if result["active_pr"] is None else "active")

    def test_resultado_reflete_o_workflow_vigente(self):
        live = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
        result = verify(self.root)
        self.assertEqual(result["active_task"], live["active"]["task_id"])
        self.assertEqual(result["active_pr"], live["active"]["pr_number"])
        self.assertEqual(result["last_merged_pr"], live["last_merged"]["pr_number"])
        self.assertEqual(result["last_merge_sha"], live["last_merged"]["merge_commit_sha"])
        self.assertEqual(result["next_task"], live["next_task_after_merge"])

    def test_rejeita_marcador_de_proxima_tarefa_solto_fora_do_bloco(self):
        live = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
        p = self.root / "ROADMAP.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n**Próxima tarefa: RM-99**\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "marcador de próxima tarefa divergente"):
            verify(self.root)

    def test_aceita_marcador_historico_sem_negrito(self):
        p = self.root / "ROADMAP.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nPróxima tarefa então prevista: RM-08.\n", encoding="utf-8")
        self.assertEqual(verify(self.root)["result"], "PASS")

    def mutate_workflow(self, fn):
        p = self.root / "state/WORKFLOW.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        fn(data)
        p.write_text(json.dumps(data), encoding="utf-8")

    def test_rejeita_sha_de_merge_invalido(self):
        self.mutate_workflow(lambda d: d["last_merged"].update(merge_commit_sha="bad"))
        with self.assertRaisesRegex(ValueError, "SHA válido"):
            verify(self.root)

    def test_rejeita_pr_de_merge_ausente(self):
        self.mutate_workflow(lambda d: d["last_merged"].update(pr_number=None))
        with self.assertRaisesRegex(ValueError, "PR do último merge"):
            verify(self.root)

    def test_rejeita_documento_com_recibo_stale(self):
        p = self.root / "memory/HANDOFF.md"
        live = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
        old = f"Último merge comprovado: PR #{live['last_merged']['pr_number']}"
        p.write_text(p.read_text().replace(old, "Último merge comprovado: PR #1", 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "último merge|diverge do WORKFLOW"):
            verify(self.root)

    def test_rejeita_proxima_tarefa_divergente(self):
        p = self.root / "ROADMAP.md"
        p.write_text(p.read_text().replace(f"**Próxima tarefa: {json.loads((ROOT / 'state/WORKFLOW.json').read_text(encoding='utf-8'))['next_task_after_merge']}**",
                                           "**Próxima tarefa: RM-99**", 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Próxima tarefa|diverge do WORKFLOW"):
            verify(self.root)

    def test_rejeita_estado_idle_com_documento_ativo(self):
        self.mutate_workflow(lambda d: d.update(active=None))
        with self.assertRaisesRegex(ValueError, "WORKFLOW.active"):
            verify(self.root)

    def test_rejeita_branch_main_como_branch_de_trabalho(self):
        self.mutate_workflow(lambda d: d["active"].update(branch="main"))
        with self.assertRaisesRegex(ValueError, "branch de ciclo"):
            verify(self.root)

    def test_rejeita_pr_booleano(self):
        self.mutate_workflow(lambda d: d["active"].update(pr_number=True))
        with self.assertRaisesRegex(ValueError, "PR ativo inválido"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()
