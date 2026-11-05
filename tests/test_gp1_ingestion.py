"""Synthetic acceptance tests for GP-1 IGP-12/13/14 in the integrated harness."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from core import topic_rows, validate_events, rebuild
from gp1_ingestion import normalize_external_report

TOPICS = topic_rows(ROOT)
TOPIC = "GER-LEG"
RECORDED = "2026-11-04T10:05:00-04:00"
ATTEMPTED = "2026-11-04T09:30:00-04:00"


def recommendation():
    return {
        "event_id": "rec-1", "type": "caderno_recomendado",
        "timestamp": "2026-11-04T09:00:00-04:00",
        "caderno_id": "internal-rec-1", "recommendation_id": "REC-FICT-1",
        "topic_ids": [TOPIC],
    }


def attempt(event_id, attempt_id, correct=8, errors=4, recorded=RECORDED,
            attempt_at=ATTEMPTED, kind="attempt_recorded", corrects=None):
    event = {
        "event_id": event_id, "type": kind, "schema_version": "1.0", "attempt_id": attempt_id,
        "recommendation_id": "REC-FICT-1", "platform_notebook_id": "EXT-FICT-44",
        "recorded_at": recorded, "attempt_at": attempt_at,
        "total": correct + errors, "acertos": correct, "erros": errors,
        "nao_respondidas": 0,
        "topic_results": [{"topic_id": TOPIC, "attempted": correct + errors, "correct": correct}],
    }
    if corrects is not None:
        event["corrects_event_id"] = corrects
    return event


def report():
    return {
        "event_id": "attempt-normalized-1", "attempt_id": "TRY-FICT-1",
        "recommendation_id": "REC-FICT-1", "platform_notebook_id": "EXT-FICT-44",
        "recorded_at": RECORDED, "attempt_at": None, "source_ref": "synthetic-fixture://IGP-12",
        "reported_answered": 12, "reported_unanswered": 3,
        "correct": 8, "incorrect": 4, "topic_results": [],
    }


class GP1IngestionTests(unittest.TestCase):
    def test_igp12_unknown_convention_never_creates_event(self):
        result = normalize_external_report(report())
        self.assertEqual(result["decision"], "pending_clarification")
        self.assertIs(result["canonical_event_created"], False)
        self.assertNotIn("event", result)

    def test_igp12_explicit_excludes_convention_derives_total_15(self):
        result = normalize_external_report(report(), "answered_excludes_unanswered")
        self.assertEqual(result["decision"], "normalized")
        self.assertIs(result["canonical_event_ready"], True)
        self.assertIs(result["canonical_event_created"], False)
        self.assertEqual(result["event"]["total"], 15)
        self.assertEqual(result["event"]["acertos"], 8)
        self.assertEqual(result["event"]["erros"], 4)
        self.assertEqual(result["event"]["nao_respondidas"], 3)

    def test_igp12_includes_convention_derives_12_answered_and_3_blank(self):
        value = report()
        value["reported_answered"] = 15
        result = normalize_external_report(value, "answered_includes_unanswered")
        self.assertEqual(result["normalization"]["answered"], 12)
        self.assertEqual(result["event"]["total"], 15)

    def test_igp12_rejects_incoherent_count_instead_of_guessing(self):
        value = report()
        value["correct"] = 9
        with self.assertRaisesRegex(ValueError, "não correspondem"):
            normalize_external_report(value, "answered_excludes_unanswered")

    def test_igp13_two_attempts_share_external_notebook_without_overwrite(self):
        events = [recommendation(), attempt("a1", "TRY-A"), attempt("a2", "TRY-B", correct=6, errors=6)]
        self.assertTrue(validate_events(events, TOPICS, allow_private=True))
        state, rows = rebuild(events, TOPICS)
        topic = next(row for row in rows if row["topic_id"] == TOPIC)
        self.assertEqual(state["results_count"], 2)
        self.assertEqual((topic["attempted"], topic["correct"]), (24, 14))

    def test_igp13_correction_replaces_only_selected_attempt(self):
        events = [
            recommendation(), attempt("a1", "TRY-A"),
            attempt("b1", "TRY-B", correct=6, errors=6),
            attempt("b2", "TRY-B", correct=7, errors=5, kind="attempt_corrected", corrects="b1"),
        ]
        self.assertTrue(validate_events(events, TOPICS, allow_private=True))
        state, rows = rebuild(events, TOPICS)
        topic = next(row for row in rows if row["topic_id"] == TOPIC)
        self.assertEqual(state["results_count"], 2)
        self.assertEqual((topic["attempted"], topic["correct"]), (24, 15))

    def test_attempt_completes_only_its_recommendation(self):
        events = [recommendation(), attempt("a1", "TRY-A")]
        state, _ = rebuild(events, TOPICS)
        self.assertEqual(state["pending_cadernos"], [])

    def test_missing_attempt_schema_version_rejected(self):
        value = attempt("a1", "TRY-A")
        value.pop("schema_version")
        with self.assertRaisesRegex(ValueError, "Versão do esquema"):
            validate_events([recommendation(), value], TOPICS, allow_private=True)

    def test_igp13_duplicate_attempt_id_rejected(self):
        events = [recommendation(), attempt("a1", "TRY-A"), attempt("a2", "TRY-A")]
        with self.assertRaisesRegex(ValueError, "attempt_id duplicado"):
            validate_events(events, TOPICS, allow_private=True)

    def test_igp13_orphan_correction_rejected(self):
        events = [recommendation(), attempt("a2", "TRY-A", kind="attempt_corrected", corrects="missing")]
        with self.assertRaisesRegex(ValueError, "Correção sem vínculo"):
            validate_events(events, TOPICS, allow_private=True)

    def test_igp13_correction_cannot_change_identity(self):
        events = [recommendation(), attempt("a1", "TRY-A")]
        correction = attempt("a2", "TRY-A", kind="attempt_corrected", corrects="a1")
        correction["platform_notebook_id"] = "OTHER-FICTIVE"
        events.append(correction)
        with self.assertRaisesRegex(ValueError, "alterou a identidade"):
            validate_events(events, TOPICS, allow_private=True)

    def test_igp14_recorded_at_and_unknown_attempt_at_are_separate(self):
        value = attempt("a1", "TRY-A", attempt_at=None)
        self.assertTrue(validate_events([recommendation(), value], TOPICS, allow_private=True))
        self.assertIsNone(value["attempt_at"])
        self.assertEqual(value["recorded_at"], RECORDED)
        state, _ = rebuild([recommendation(), value], TOPICS)
        self.assertEqual(state["last_event_at"], RECORDED)
        self.assertEqual(state["last_attempt_id"], "TRY-A")

    def test_igp14_attempt_at_after_recorded_at_rejected(self):
        value = attempt("a1", "TRY-A", attempt_at="2026-11-04T11:00:00-04:00")
        with self.assertRaisesRegex(ValueError, "posterior a recorded_at"):
            validate_events([recommendation(), value], TOPICS, allow_private=True)

    def test_attempt_results_remain_blocked_for_personal_persistence(self):
        with self.assertRaisesRegex(ValueError, "Resultados individuais bloqueados"):
            validate_events([recommendation(), attempt("a1", "TRY-A")], TOPICS, allow_private=False)


if __name__ == "__main__":
    unittest.main()
