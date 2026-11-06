"""Adversarial tests for the offline synthetic Tutor-Coach cycle."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from decision_queue import FACTOR_NAMES
from tutor_coach_offline_cycle import run_offline_cycle

SOURCE_COMMIT = "9525a2dd5a6e3646eaffee4da4b1dd1fca3e1fe7"
TOPICS = [{"topic_id": "523-06"}, {"topic_id": "324-01"}]


def candidate(candidate_id, topic_id="523-06", cargo_id="523", learning_need=1):
    factors = {name: 1 for name in FACTOR_NAMES}
    factors["elimination_risk"] = 2
    factors["learning_need"] = learning_need
    return {
        "candidate_id": candidate_id,
        "eligibility": "needs_evidence",
        "topic_ids": [topic_id],
        "cargo_ids": [cargo_id],
        "priority_factors": factors,
        "justification": "Fixture sintética para verificar o encadeamento offline.",
    }


def scenario():
    return {
        "candidates": [candidate("SYNTH-CANDIDATE-01")],
        "next_candidates": [candidate("SYNTH-CANDIDATE-02", learning_need=2)],
        "topics": TOPICS,
        "as_of": "2026-11-06T09:00:00-04:00",
        "reevaluation_as_of": "2026-11-06T10:00:00-04:00",
        "source_commit": SOURCE_COMMIT,
        "edital_version": "fixture-edital-2026",
        "execution_simulation": {
            "data_origin": "synthetic_fixture",
            "status": "simulated",
            "execution_ref": "synthetic-fixture://execution/01",
            "candidate_id": "SYNTH-CANDIDATE-01",
        },
        "result_report": {
            "data_origin": "synthetic_fixture",
            "platform": "manual_search",
            "event_id": "SYNTH-EVENT-01",
            "attempt_id": "SYNTH-ATTEMPT-01",
            "recorded_at": "2026-11-06T09:30:00-04:00",
            "attempt_at": None,
            "source_ref": "synthetic-fixture://report/01",
            "execution_ref": "synthetic-fixture://execution/01",
            "answered_convention": "answered_excludes_unanswered",
            "reported_answered": 8,
            "reported_unanswered": 2,
            "correct": 6,
            "incorrect": 2,
            "source_kind": "manual_report",
            "independence": "unknown",
            "familiarity": "unknown",
            "diversity": "unknown",
            "confidence": "unknown",
            "topic_results": [
                {"topic_id": "523-06", "attempted": 8, "correct": 6}
            ],
        },
        "objective": "Fixture: observar evidência agregada e por tópico sem inferir domínio.",
        "question_target": 10,
    }


class OfflineTutorCoachCycleTests(unittest.TestCase):
    def run_scenario(self, **updates):
        values = scenario()
        values.update(updates)
        return run_offline_cycle(**values)

    def test_ciclo_completo_permanece_sintetico_e_sem_efeitos(self):
        result = self.run_scenario()
        self.assertEqual(result["data_origin"], "synthetic_fixture")
        self.assertEqual(result["recommendation"]["platform"], "manual_search")
        self.assertEqual(result["recommendation"]["availability_status"], "unavailable_or_unverified")
        self.assertIsNone(result["recommendation"]["questions_suggested"])
        self.assertEqual(result["execution_simulation"]["status"], "simulated")
        self.assertEqual(result["result"]["event"]["execution_ref"],
                         result["execution_simulation"]["execution_ref"])
        self.assertTrue(result["validation"]["schema_valid"])
        self.assertTrue(result["validation"]["in_memory_only"])
        self.assertFalse(result["validation"]["persistence_authorized"])
        self.assertEqual(result["reconstruction"]["attempts_count"], 1)
        self.assertEqual(result["evidence"]["level"], "E2")
        self.assertIsNotNone(result["reevaluation"]["next_queue_snapshot"]["selected_candidate_id"])
        self.assertFalse(result["reevaluation"]["automatic_factor_updates"])
        self.assertFalse(result["side_effects_performed"])
        self.assertFalse(result["external_integrations_used"])
        self.assertFalse(result["persisted"])

    def test_ciclo_e_reprodutivel_para_os_mesmos_inputs(self):
        first = self.run_scenario()
        second = self.run_scenario()
        self.assertEqual(first["recommendation"]["recommendation_id"],
                         second["recommendation"]["recommendation_id"])
        self.assertEqual(first["reevaluation"]["next_queue_snapshot"]["snapshot_id"],
                         second["reevaluation"]["next_queue_snapshot"]["snapshot_id"])

    def test_resultado_agregado_sem_topicos_permanece_e1(self):
        report = scenario()["result_report"]
        report["topic_results"] = []
        result = self.run_scenario(result_report=report)
        self.assertEqual(result["evidence"]["level"], "E1")
        self.assertEqual(result["reconstruction"]["progress"]["523-06"]["attempted"], 0)

    def test_relatorio_com_contagens_incoerentes_e_rejeitado(self):
        report = scenario()["result_report"]
        report["correct"] = 7
        with self.assertRaisesRegex(ValueError, "não correspondem"):
            self.run_scenario(result_report=report)

    def test_relatorio_nao_sintetico_e_rejeitado(self):
        report = scenario()["result_report"]
        report["data_origin"] = "manual_report"
        with self.assertRaisesRegex(ValueError, "synthetic_fixture"):
            self.run_scenario(result_report=report)

    def test_referencia_externa_e_rejeitada(self):
        report = scenario()["result_report"]
        report["source_ref"] = "https://example.invalid/report"
        with self.assertRaisesRegex(ValueError, "fixture sintética"):
            self.run_scenario(result_report=report)

    def test_id_de_tentativa_nao_sintetico_e_rejeitado(self):
        report = scenario()["result_report"]
        report["attempt_id"] = "ATTEMPT-REAL-1"
        with self.assertRaisesRegex(ValueError, "SYNTH-"):
            self.run_scenario(result_report=report)

    def test_recommendation_id_divergente_e_rejeitado(self):
        report = scenario()["result_report"]
        report["recommendation_id"] = "rec-outro"
        with self.assertRaisesRegex(ValueError, "recommendation_id diferente"):
            self.run_scenario(result_report=report)

    def test_id_de_caderno_de_plataforma_e_rejeitado(self):
        report = scenario()["result_report"]
        report["platform_notebook_id"] = "TEC-12345"
        with self.assertRaisesRegex(ValueError, "ID de caderno externo"):
            self.run_scenario(result_report=report)

    def test_topico_fora_da_recomendacao_e_rejeitado(self):
        report = scenario()["result_report"]
        report["topic_results"] = [
            {"topic_id": "324-01", "attempted": 8, "correct": 6}
        ]
        with self.assertRaisesRegex(ValueError, "Tópico fora da recomendação"):
            self.run_scenario(result_report=report)

    def test_execucao_real_ou_integracao_externa_e_rejeitada(self):
        execution = scenario()["execution_simulation"]
        execution["status"] = "completed"
        with self.assertRaisesRegex(ValueError, "somente execução simulada"):
            self.run_scenario(execution_simulation=execution)

    def test_resultado_de_outra_execucao_e_rejeitado(self):
        report = scenario()["result_report"]
        report["execution_ref"] = "synthetic-fixture://execution/other"
        with self.assertRaisesRegex(ValueError, "não corresponde à execução simulada"):
            self.run_scenario(result_report=report)

    def test_execucao_de_outro_candidato_e_rejeitada(self):
        execution = scenario()["execution_simulation"]
        execution["candidate_id"] = "SYNTH-CANDIDATE-OTHER"
        with self.assertRaisesRegex(ValueError, "não corresponde ao candidato recomendado"):
            self.run_scenario(execution_simulation=execution)

    def test_plataforma_real_nao_e_permitida(self):
        report = scenario()["result_report"]
        report["platform"] = "TEC"
        with self.assertRaisesRegex(ValueError, "Plataforma externa"):
            self.run_scenario(result_report=report)

    def test_sem_candidato_elegivel_nao_cria_recomendacao(self):
        blocked = candidate("SYNTH-BLOCKED")
        blocked["eligibility"] = "blocked"
        with self.assertRaisesRegex(ValueError, "Não há candidato elegível"):
            self.run_scenario(candidates=[blocked])

    def test_topico_inexistente_na_fila_inicial_e_rejeitado(self):
        invalid = candidate("SYNTH-INVALID-FIRST", topic_id="999-99")
        with self.assertRaisesRegex(ValueError, "candidates contém tópico ausente"):
            self.run_scenario(candidates=[invalid])

    def test_topico_inexistente_em_candidato_alternativo_e_rejeitado(self):
        valid = candidate("SYNTH-VALID-FIRST", learning_need=3)
        invalid_alternative = candidate("SYNTH-INVALID-ALT", topic_id="999-99", learning_need=1)
        with self.assertRaisesRegex(ValueError, "candidates contém tópico ausente"):
            self.run_scenario(candidates=[valid, invalid_alternative])

    def test_topico_inexistente_na_fila_de_reevaluacao_e_rejeitado(self):
        invalid_next = candidate("SYNTH-INVALID-NEXT", topic_id="999-99")
        with self.assertRaisesRegex(ValueError, "next_candidates contém tópico ausente"):
            self.run_scenario(next_candidates=[invalid_next])


if __name__ == "__main__":
    unittest.main()
