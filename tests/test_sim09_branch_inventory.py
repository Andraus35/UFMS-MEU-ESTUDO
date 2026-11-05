"""Contraprovas do inventário final de branches preservadas."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Sim09BranchInventoryTests(unittest.TestCase):
    def test_inventory_has_eight_merged_and_twelve_preserved_legacy_refs(self):
        doc = (ROOT / "docs/governanca/STATUS_BRANCHES_20261105.md").read_text(encoding="utf-8")
        merged = doc.split("## Branches de integração concluída", 1)[1].split("## Branches históricas", 1)[0]
        legacy = doc.split("## Branches históricas preservadas, sem merge bruto", 1)[1].split("## Fechamento", 1)[0]
        merged_rows = [line for line in merged.splitlines() if line.startswith("| ") and len(line.split("|")) >= 5]
        legacy_rows = [line for line in legacy.splitlines() if line.startswith("| ") and len(line.split("|")) >= 5]
        self.assertEqual(len(merged_rows), 9)  # cabeçalho + 8 branches
        self.assertEqual(len(legacy_rows), 13)  # cabeçalho + 12 branches

    def test_all_deferred_refs_have_unique_branches_and_known_shas(self):
        state = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
        refs = state["deferred_pull_requests"]
        self.assertEqual(len(refs), 12)
        branches = [item["branch"] for item in refs]
        self.assertEqual(len(branches), len(set(branches)))
        for item in refs:
            self.assertRegex(item["sha"], r"^[0-9a-f]{40}$")
            self.assertTrue(item["archived_without_merge"])

    def test_inventory_does_not_claim_legacy_branches_were_deleted(self):
        doc = (ROOT / "docs/governanca/STATUS_BRANCHES_20261105.md").read_text(encoding="utf-8")
        self.assertIn("20 branches de trabalho preservadas", doc)
        self.assertIn("Não apagar branches neste ciclo", doc)


if __name__ == "__main__":
    unittest.main()
