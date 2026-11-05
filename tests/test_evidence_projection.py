"""Adversarial tests for deterministic E0-E4 evidence projection."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from core import topic_rows, rebuild
from evidence_projection import derive_evidence_level

TOPICS = topic_rows(ROOT)
TOPIC = "GER-LEG"


def legacy_result(topic=True):
    event = {
        "event_id": "legacy-result", "type": "resultado_recebido",
        "timestamp": "2026-11-04T10:00:00-04:00",
        "caderno_id": "LEGACY-1", "total": 10, "acertos": 7,
        "erros": 3, "nao_respondidas": 0,
    }
    if topic:
        event["topic_results"] = [{"topic_id": TOPIC, "attempted": 10, "correct": 7}]
    return event


def attempt(event_id, attempt_id, date, item_set, *, independence="without_consultation",
            familiarity="new", diversity="varied", source_kind="platform_export",
            confidence="secure"):
    return {
        "event_id": event_id, "type": "attempt_recorded", "attempt_id": attempt_id,
        "recorded_at": date + "T11:00:00-04:00",
        "attempt_at": date + "T10:00:00-04:00",
        "recommendation_id": "REC-" + attempt_id,
        "platform_notebook_id": "EXT-" + attempt_id,
        "source_ref": "synthetic://evidence/" + attempt_id,
        "independence": independence, "familiarity": familiarity,
        "diversity": diversity, "source_kind": source_kind,
        "confidence": confidence, "item_set_id": item_set,
        "topic_results": [{"topic_id": TOPIC, "attempted": 10, "correct": 7}],
    }


class EvidenceProjectionTests(unittest.TestCase):
    def test_e0_without_results(self):
        result = derive_evidence_level([])
        self.assertEqual(result["level"], "E0")
        self.assertEqual(result["knowledge_status"], "unknown_until_evidence")

    def test_e1_aggregate_only(self):
        result = derive_evidence_level([legacy_result(topic=False)])
        self.assertEqual(result["level"], "E1")
        self.assertEqual(result["dimensions"]["granularity"], "aggregate")
        self.assertIn("aggregate_only_no_topic_breakdown", result["uncertainties"])

    def test_e2_topic_breakdown_without_context(self):
        result = derive_evidence_level([legacy_result(topic=True)])
        self.assertEqual(result["level"], "E2")
        self.assertEqual(result["dimensions"]["granularity"], "topic")
        self.assertEqual(result["dimensions"]["independence"], "unknown")

    def test_e3_contextualized_single_attempt(self):
        result = derive_evidence_level([attempt("e1", "A1", "2026-11-01", "SET-A")])
        self.assertEqual(result["level"], "E3")
        self.assertEqual(result["dimensions"]["temporality"], "known")
        self.assertEqual(result["knowledge_status"], "unknown_until_evidence")

    def test_e4_requires_independent_recoveries_on_distinct_dates_and_sets(self):
        result = derive_evidence_level([
            attempt("e1", "A1", "2026-11-01", "SET-A"),
            attempt("e2", "A2", "2026-11-04", "SET-B"),
        ])
        self.assertEqual(result["level"], "E4")
        self.assertEqual(result["knowledge_status"], "unknown_until_evidence")

    def test_repeated_items_do_not_reach_e4(self):
        result = derive_evidence_level([
            attempt("e1", "A1", "2026-11-01", "SET-A"),
            attempt("e2", "A2", "2026-11-04", "SET-A"),
        ])
        self.assertEqual(result["level"], "E3")

    def test_same_date_does_not_reach_e4(self):
        result = derive_evidence_level([
            attempt("e1", "A1", "2026-11-01", "SET-A"),
            attempt("e2", "A2", "2026-11-01", "SET-B"),
        ])
        self.assertEqual(result["level"], "E3")

    def test_consultation_does_not_reach_e4(self):
        result = derive_evidence_level([
            attempt("e1", "A1", "2026-11-01", "SET-A", independence="with_consultation"),
            attempt("e2", "A2", "2026-11-04", "SET-B"),
        ])
        self.assertEqual(result["level"], "E3")

    def test_unknown_context_never_promoted_to_e3(self):
        result = derive_evidence_level([
            attempt("e1", "A1", "2026-11-01", "SET-A", familiarity="unknown")
        ])
        self.assertEqual(result["level"], "E2")
        self.assertIn("insufficient_independent_recoveries_on_distinct_dates_and_item_sets",
                      result["uncertainties"])

    def test_rebuild_exposes_reproducible_evidence_projection(self):
        state, _ = rebuild([], TOPICS)
        self.assertEqual(state["evidence_schema_version"], "1.0")
        self.assertEqual(state["evidence_level"], "E0")
        self.assertEqual(state["evidence_uncertainties"], ["no_assessment"])
        self.assertEqual(rebuild([], TOPICS), rebuild([], TOPICS))


if __name__ == "__main__":
    unittest.main()
