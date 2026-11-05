"""Adversarial tests for deterministic adaptive queue ranking."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from decision_queue import rank_candidates, FACTOR_WEIGHTS, FACTOR_NAMES

SHA = "a" * 40
AS_OF = "2026-11-05T12:00:00-04:00"


def candidate(cid, *, status="eligible", cargos=None, factors=None, reason="diagnóstico de cobertura"):
    values = {name: 1 for name in FACTOR_NAMES}
    if factors:
        values.update(factors)
    return {
        "candidate_id": cid,
        "eligibility": status,
        "topic_ids": ["GER-LEG"],
        "cargo_ids": cargos or ["523"],
        "priority_factors": values,
        "justification": reason,
        "deferred_alternative": "diagnóstico RLM",
    }


class DeterministicQueueTests(unittest.TestCase):
    def test_mesma_entrada_politica_e_as_of_reproduz_snapshot(self):
        items = [candidate("A"), candidate("B", factors={"learning_need": 3})]
        first = rank_candidates(items, as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        second = rank_candidates(list(reversed(items)), as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        self.assertEqual(first["snapshot_id"], second["snapshot_id"])
        self.assertEqual(first["ranked"], second["ranked"])
        self.assertEqual(first["selected_candidate_id"], second["selected_candidate_id"])

    def test_candidato_bloqueado_nao_e_ranqueado_e_motivo_permanece(self):
        result = rank_candidates(
            [candidate("A"), candidate("B", status="blocked", reason="fora do edital")],
            as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        self.assertEqual([x["candidate_id"] for x in result["ranked"]], ["A"])
        self.assertEqual(result["excluded"][0]["candidate_id"], "B")
        self.assertEqual(result["excluded"][0]["reason"], "blocked")

    def test_pending_confirmation_nao_e_apresentado_como_elegivel(self):
        result = rank_candidates([candidate("A", status="pending_confirmation")],
                                 as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        self.assertEqual(result["ranked"], [])
        self.assertIsNone(result["selected_candidate_id"])

    def test_viabilidade_zero_exclui_candidato(self):
        result = rank_candidates(
            [candidate("A", factors={"feasibility": 0})],
            as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        self.assertEqual(result["excluded"][0]["reason"], "feasibility_zero")

    def test_fatores_desconhecidos_nao_sao_inventados(self):
        result = rank_candidates(
            [candidate("A", factors={"learning_need": None, "coverage_gap": None})],
            as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        row = result["ranked"][0]
        self.assertIn("learning_need", row["unknown_factors"])
        self.assertIsNone(row["score_breakdown"]["learning_need"]["value"])
        self.assertEqual(row["score_breakdown"]["learning_need"]["contribution"], 0)

    def test_pesos_sao_versionados_e_explicitamente_aplicados(self):
        policy = {"version": "test-v2", "weights": dict(FACTOR_WEIGHTS)}
        policy["weights"]["learning_need"] = 4
        result = rank_candidates([candidate("A", factors={"learning_need": 3})],
                                 as_of=AS_OF, source_commit=SHA,
                                 edital_version="152/2026-original", policy=policy)
        row = result["ranked"][0]
        self.assertEqual(row["score_breakdown"]["learning_need"]["weight"], 4)
        self.assertEqual(row["score_breakdown"]["learning_need"]["contribution"], 12)
        self.assertEqual(result["policy"]["version"], "test-v2")

    def test_candidato_compartilhado_523_324_aparece_uma_vez(self):
        result = rank_candidates([candidate("SHARED", cargos=["523", "324"])],
                                 as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        self.assertEqual(len(result["ranked"]), 1)
        self.assertEqual(result["ranked"][0]["cargo_ids"], ["523", "324"])

    def test_desempate_usa_id_estavel(self):
        result = rank_candidates([candidate("B"), candidate("A")],
                                 as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        self.assertEqual([x["candidate_id"] for x in result["ranked"]], ["A", "B"])

    def test_as_of_explicito_e_obrigatorio(self):
        with self.assertRaisesRegex(ValueError, "as_of"):
            rank_candidates([], as_of="2026-11-05T12:00:00", source_commit=SHA,
                            edital_version="152/2026-original")

    def test_source_commit_deve_ser_sha_git(self):
        with self.assertRaisesRegex(ValueError, "SHA Git"):
            rank_candidates([], as_of=AS_OF, source_commit="main",
                            edital_version="152/2026-original")

    def test_ids_duplicados_rejeitados(self):
        with self.assertRaisesRegex(ValueError, "candidate_id duplicado"):
            rank_candidates([candidate("A"), candidate("A")],
                            as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")

    def test_policy_incompleta_rejeitada(self):
        with self.assertRaisesRegex(ValueError, "Pesos da política"):
            rank_candidates([], as_of=AS_OF, source_commit=SHA,
                            edital_version="152/2026-original",
                            policy={"version": "bad", "weights": {"learning_need": 1}})

    def test_snapshot_muda_quando_as_of_muda(self):
        items = [candidate("A")]
        first = rank_candidates(items, as_of=AS_OF, source_commit=SHA, edital_version="152/2026-original")
        second = rank_candidates(items, as_of="2026-11-06T12:00:00-04:00",
                                 source_commit=SHA, edital_version="152/2026-original")
        self.assertNotEqual(first["snapshot_id"], second["snapshot_id"])

    def test_nao_emite_probabilidade_de_aprendizagem_ou_aprovacao(self):
        result = rank_candidates([candidate("A")], as_of=AS_OF,
                                 source_commit=SHA, edital_version="152/2026-original")
        self.assertIs(result["probability_claims"], False)
        self.assertNotIn("probability", result["ranked"][0])


if __name__ == "__main__":
    unittest.main()
