"""Contraprovas do inventário autenticado de branches."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Sim09BranchInventoryTests(unittest.TestCase):
    def test_inventory_has_fifteen_contained_and_twelve_divergent_refs(self):
        doc = (ROOT / "docs/governanca/STATUS_BRANCHES_20261105.md").read_text(encoding="utf-8")
        contained = doc.split("## Branches cujo HEAD está contido em main", 1)[1].split("## Branches históricas divergentes", 1)[0]
        legacy = doc.split("## Branches históricas divergentes — preservar, não mesclar em lote", 1)[1].split("## Regras de limpeza", 1)[0]
        contained_rows = [line for line in contained.splitlines() if line.startswith("| ") and len(line.split("|")) >= 5]
        legacy_rows = [line for line in legacy.splitlines() if line.startswith("| ") and len(line.split("|")) >= 6]
        self.assertEqual(len(contained_rows), 16)  # cabeçalho + 15 refs contidas
        self.assertEqual(len(legacy_rows), 13)  # cabeçalho + 12 refs divergentes


    def test_inventory_matches_post_sim10_authenticated_snapshot(self):
        doc = (ROOT / "docs/governanca/STATUS_BRANCHES_20261105.md").read_text(encoding="utf-8")
        self.assertIn("28 refs", doc)
        self.assertIn("34**, todos fechados; **20 merged**, **14 closed without merge", doc)
        self.assertIn("8bd0fd3fe51ac2ea371f466f55b6edb883e4d589", doc)

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
        self.assertIn("12 refs preservam commits exclusivos", doc)
        self.assertIn("15 refs têm HEAD contido", doc)
        self.assertIn("Nenhuma branch foi apagada nesta entrega", doc)
        self.assertIn("Exclusão requer autorização específica", doc)



if __name__ == "__main__":
    unittest.main()
