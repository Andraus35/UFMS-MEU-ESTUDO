"""Tests for truthful notebook prescriptions without platform side effects."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from decision_queue import rank_candidates, FACTOR_NAMES
from notebook_prescriber import prescribe_notebook

SHA = "a" * 40
AS_OF = "2026-11-05T12:00:00-04:00"


def snapshot():
    factors = {name: 1 for name in FACTOR_NAMES}
    return rank_candidates([{
        "candidate_id": "candidate-1", "eligibility": "eligible",
        "topic_ids": ["GER-LEG"], "cargo_ids": ["523", "324"],
        "priority_factors": factors, "justification": "Diagnóstico de legislação compartilhada.",
        "deferred_alternative": "RLM diagnóstico",
    }], as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")


def prescribe(**kwargs):
    args = {
        "queue_snapshot": snapshot(),
        "candidate_id": "candidate-1",
        "intervention": "diagnostic",
        "objective": "Estabelecer linha de base sem consulta.",
        "platform": "student_choice",
    }
    args.update(kwargs)
    return prescribe_notebook(**args)


class NotebookPrescriberTests(unittest.TestCase):
    def test_recommendation_nao_cria_caderno_nem_id_externo(self):
        result = prescribe()
        self.assertEqual(result["status"], "recommended")
        self.assertEqual(result["creation_status"], "not_created")
        self.assertIsNone(result["platform_notebook_id"])
        self.assertEqual(result["platform_notebook_id_status"], "unknown")
        self.assertIs(result["side_effects_performed"], False)

    def test_disponibilidade_desconhecida_nao_inventa_quantidade(self):
        result = prescribe(question_target=20)
        self.assertEqual(result["availability_status"], "unavailable_or_unverified")
        self.assertIsNone(result["questions_suggested"])

    def test_disponibilidade_confirmada_limita_sugestao_ao_estoque(self):
        result = prescribe(
            question_target=20,
            availability={"status": "confirmed", "available_count": 7, "evidence_ref": "user-screen-1"},
        )
        self.assertEqual(result["availability_status"], "confirmed")
        self.assertEqual(result["questions_suggested"], 7)

    def test_objeto_de_disponibilidade_vazio_permanece_desconhecido(self):
        result = prescribe(availability={})
        self.assertEqual(result["availability_status"], "unavailable_or_unverified")
        self.assertIsNone(result["questions_suggested"])

    def test_confirmacao_sem_evidencia_rejeitada(self):
        with self.assertRaisesRegex(ValueError, "sem evidence_ref"):
            prescribe(availability={"status": "confirmed", "available_count": 10})

    def test_filtros_confirmados_exigem_evidencia(self):
        with self.assertRaisesRegex(ValueError, "sem evidence_ref"):
            prescribe(platform_capabilities={"topic_filter": {"status": "confirmed"}})

    def test_camadas_de_filtro_preservam_escopo(self):
        result = prescribe()
        self.assertEqual(result["filters"]["layer_0_scope"]["topic_ids"], ["GER-LEG"])
        self.assertEqual(result["filters"]["layer_0_scope"]["cargo_ids"], ["523", "324"])
        self.assertEqual(result["fallback"][0]["preserve"], ["cargo_ids", "topic_ids"])
        self.assertEqual(result["fallback"][3]["preserve"], ["cargo_ids", "topic_ids"])

    def test_alternativa_exige_motivo_de_override(self):
        value = snapshot()
        second = dict(value["ranked"][0])
        second["candidate_id"] = "alternative"
        value["ranked"].append(second)
        with self.assertRaisesRegex(ValueError, "justificativa explícita"):
            prescribe(queue_snapshot=value, candidate_id="alternative")
        result = prescribe(queue_snapshot=value, candidate_id="alternative",
                           selection_override_reason="Estudante preferiu este tópico.")
        self.assertEqual(result["candidate_id"], "alternative")

    def test_candidato_fora_do_snapshot_rejeitado(self):
        with self.assertRaisesRegex(ValueError, "não consta do snapshot"):
            prescribe(candidate_id="inventado")

    def test_recommendation_id_e_deterministico(self):
        first = prescribe()
        second = prescribe()
        self.assertEqual(first["recommendation_id"], second["recommendation_id"])

    def test_filtro_nao_confirmado_permanece_pendente(self):
        result = prescribe()
        self.assertEqual(result["filters"]["layer_0_scope"]["status"], "pending_confirmation")
        self.assertEqual(result["filters"]["layer_2_exam_similarity"]["status"], "unknown")

    def test_caderno_compartilhado_conta_uma_vez(self):
        result = prescribe()
        self.assertEqual(result["cargo_ids"], ["523", "324"])
        self.assertEqual(result["topic_ids"], ["GER-LEG"])


if __name__ == "__main__":
    unittest.main()
