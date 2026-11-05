"""Regressão da proveniência documental do PLAN v0.3-r2 aprovado."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / ".specs/features/ufms-cognitive-gates/revisions/v0.3/approved-r2"
sys.path.insert(0, str(SNAPSHOT))
from verify_approval_snapshot import audit


class CognitiveSpecR2SnapshotTests(unittest.TestCase):
    def test_approved_snapshot_provenance_and_scope(self):
        result = audit(SNAPSHOT)
        self.assertEqual(result["result"], "PASS", result["errors"])
        self.assertEqual(result["ears_count"], 27)
        self.assertEqual(result["checks_count"], 27)
        self.assertEqual(result["functional_checks_pass"], 0)
        self.assertEqual(result["functional_checks_not_run"], 27)
        self.assertEqual(result["GQD"], "REPROVADA_PENDING_REAUDIT")


if __name__ == "__main__":
    unittest.main()
