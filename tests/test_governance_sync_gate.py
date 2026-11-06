"""Adversarial tests for deterministic governance-document synchronization."""
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
        for rel in (
            "state/WORKFLOW.json",
            "memory/HANDOFF.md",
            "ROADMAP.md",
            "docs/governanca/STATUS_BRANCHES_RECONCILIADO_20261105.md",
        ):
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)

    def tearDown(self):
        self.temp.cleanup()

    def test_checkpoint_vigente_e_coerente(self):
        result = verify(self.root)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["last_merged_pr"], 52)
        self.assertEqual(result["active_pr"], 53)

    def test_rejeita_handoff_sem_sha_do_ultimo_merge(self):
        path = self.root / "memory/HANDOFF.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(
            "7df4b8fff8d8ed76096d33edb6474808fb2e34ca", "0" * 40, 1
        ), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "HANDOFF desatualizado"):
            verify(self.root)

    def test_rejeita_roadmap_com_pr_ativo_antigo(self):
        path = self.root / "ROADMAP.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("RM-08-PREP / PR #53", "RM-08-PREP / PR #52", 1),
                        encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "ROADMAP desatualizado"):
            verify(self.root)

    def test_rejeita_status_sem_recibo_do_merge(self):
        path = self.root / "docs/governanca/STATUS_BRANCHES_RECONCILIADO_20261105.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("Último merge comprovado: PR #52", "Merge pendente", 1),
                        encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "STATUS desatualizado"):
            verify(self.root)

    def test_rejeita_workflow_sem_sha_de_merge(self):
        path = self.root / "state/WORKFLOW.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["last_merged"]["merge_commit_sha"] = "invalid"
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA válido"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()
