"""Contraprovas determinísticas de integridade e reconstrução."""
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from core import topic_rows, validate_events, rebuild  # noqa: E402

T = "2026-11-04T10:00:00-04:00"
TOPICS = topic_rows(ROOT)


def recommendation(eid="rec-1", cid="UFMS-001"):
    return {"event_id": eid, "type": "caderno_recomendado", "timestamp": T,
            "caderno_id": cid, "topic_ids": ["GER-LEG"]}


def outcome(eid="res-1", cid="UFMS-001", **kwargs):
    return {"event_id": eid, "type": "resultado_recebido", "timestamp": T,
            "caderno_id": cid, "total": 12, "acertos": 8, "erros": 4,
            "topic_results": [{"topic_id": "GER-LEG", "attempted": 12, "correct": 8}], **kwargs}


class HarnessTests(unittest.TestCase):
    def test_zero_events_rebuild(self):
        state, progress = rebuild([], TOPICS)
        self.assertEqual(state["event_count"], 0)
        self.assertEqual(len(progress), 23)
        self.assertTrue(all(row["attempted"] == 0 for row in progress))

    def test_recommendation_is_not_result(self):
        events = [recommendation()]
        validate_events(events, TOPICS)
        state, progress = rebuild(events, TOPICS)
        self.assertEqual(state["pending_cadernos"], ["UFMS-001"])
        self.assertEqual(state["results_count"], 0)

    def test_aggregate_result_does_not_invent_topic_score(self):
        result = outcome()
        result.pop("topic_results")
        validate_events([recommendation(), result], TOPICS, allow_private=True)
        state, progress = rebuild([recommendation(), result], TOPICS)
        self.assertEqual(state["results_count"], 1)
        self.assertEqual(next(row for row in progress if row["topic_id"] == "GER-LEG")["attempted"], 0)

    def test_disaggregated_result_is_accounted_for(self):
        events = [recommendation(), outcome()]
        validate_events(events, TOPICS, allow_private=True)
        state, progress = rebuild(events, TOPICS)
        p = next(row for row in progress if row["topic_id"] == "GER-LEG")
        self.assertEqual((p["attempted"], p["correct"], p["accuracy"]), (12, 8, "0.6667"))
        self.assertEqual(state["pending_cadernos"], [])

    def test_private_result_block(self):
        with self.assertRaisesRegex(ValueError, "bloqueados"):
            validate_events([outcome()], TOPICS, allow_private=False)

    def test_bad_total_rejected(self):
        event = outcome()
        event["erros"] = 5
        with self.assertRaisesRegex(ValueError, "Totais inconsistentes"):
            validate_events([event], TOPICS, allow_private=True)

    def test_unknown_topic_rejected(self):
        event = recommendation()
        event["topic_ids"] = ["INVENTADO-99"]
        with self.assertRaisesRegex(ValueError, "Tópico não cadastrado"):
            validate_events([event], TOPICS)

    def test_duplicate_event_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicado"):
            validate_events([recommendation(), recommendation()], TOPICS)

    def test_duplicate_result_requires_correction(self):
        with self.assertRaisesRegex(ValueError, "Resultado duplicado"):
            validate_events([outcome(), outcome(eid="res-2")], TOPICS, allow_private=True)

    def test_result_correction_replaces_not_sums(self):
        new_result = {
            "event_id": "corr-1", "type": "resultado_corrigido", "timestamp": T,
            "caderno_id": "UFMS-001", "corrects_event_id": "res-1",
            "total": 12, "acertos": 9, "erros": 3,
            "topic_results": [{"topic_id": "GER-LEG", "attempted": 12, "correct": 9}]
        }
        events = [outcome(), new_result]
        validate_events(events, TOPICS, allow_private=True)
        state, progress = rebuild(events, TOPICS)
        p = next(row for row in progress if row["topic_id"] == "GER-LEG")
        self.assertEqual((p["attempted"], p["correct"]), (12, 9))
        self.assertEqual(state["results_count"], 1)

    def test_revision_lifecycle(self):
        events = [
            {"event_id":"due1","type":"revisao_agendada","timestamp":T,"topic_id":"GER-LEG","due_at":"2026-11-11T18:00:00-04:00"},
            {"event_id":"done1","type":"revisao_concluida","timestamp":T,"topic_id":"GER-LEG"}
        ]
        validate_events(events, TOPICS)
        state, _ = rebuild(events, TOPICS)
        self.assertEqual(state["pending_reviews"], {})

    def test_unzoned_time_rejected(self):
        event = recommendation()
        event["timestamp"] = "2026-11-04T10:00:00"
        with self.assertRaisesRegex(ValueError, "fuso horário"):
            validate_events([event], TOPICS)

    def test_rebuild_is_reproducible(self):
        events = [recommendation(), outcome()]
        self.assertEqual(rebuild(events, TOPICS), rebuild(events, TOPICS))


if __name__ == "__main__":
    unittest.main()
