"""Integrity tests for the 102-scenario traceability inventory."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = json.loads((ROOT / "docs/pedagogia/MATRIZ_RASTREABILIDADE_102_RM06_20261105.json").read_text(encoding="utf-8"))
CATALOG = (ROOT / "docs/pedagogia/CRITERIOS_DE_ACEITACAO.md").read_text(encoding="utf-8")


class ScenarioTraceabilityTests(unittest.TestCase):
    def test_catalog_has_exactly_102_unique_ids(self):
        ids = re.findall(r"^\|\s*((?:PED|COMP|SIM|EFA|FIQ|CDO|PRD)-\d{2})\s*\|", CATALOG, re.M)
        matrix_ids = [row["scenario_id"] for row in MATRIX["scenarios"]]
        self.assertEqual(len(ids), 102)
        self.assertEqual(len(set(ids)), 102)
        self.assertEqual(matrix_ids, ids)

    def test_every_scenario_has_honest_status_and_execution_state(self):
        self.assertEqual(MATRIX["catalog_count"], 102)
        self.assertEqual(len(MATRIX["scenarios"]), 102)
        for row in MATRIX["scenarios"]:
            self.assertIn(row["status"], {"PARTIAL", "NOT_IMPLEMENTED"})
            self.assertEqual(row["execution"], "NOT_RUN_AS_SCENARIO")
            self.assertTrue(row["note"])
        self.assertEqual(MATRIX["status_counts"]["PASS"], 0)
        self.assertEqual(MATRIX["status_counts"]["NOT_RUN"], 102)

    def test_every_test_reference_resolves_to_one_canonical_test(self):
        for row in MATRIX["scenarios"]:
            for ref in row["test_refs"]:
                path, test_name = ref.split("::", 1)
                source = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("def " + test_name + "(", source, row["scenario_id"] + ": " + ref)

    def test_no_scenario_is_silently_duplicated(self):
        ids = [row["scenario_id"] for row in MATRIX["scenarios"]]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
