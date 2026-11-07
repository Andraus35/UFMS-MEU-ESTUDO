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

    def test_checkpoint_preparado_coerente(self):
        result = verify(self.root)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["state"], "prepared")

    def test_baseline_rm08_e_estado_preparado_com_rm08_formal_bloqueada(self):
        result = verify(self.root)
        self.assertEqual(result["active_task"], "RM-08-BASELINE")
        self.assertEqual(result["state"], "prepared")
        self.assertEqual(result["next_task"], "RM-08")

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
        p.write_text(p.read_text().replace("Último merge comprovado: PR #54", "Último merge comprovado: PR #52", 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "último merge|diverge do WORKFLOW"):
            verify(self.root)

    def test_rejeita_proxima_tarefa_divergente(self):
        p = self.root / "ROADMAP.md"
        p.write_text(p.read_text().replace("**Próxima tarefa: RM-08**",
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
