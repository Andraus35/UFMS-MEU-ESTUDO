"""CDO-14 e FIQ-10: caderno pendente não gera prescrição duplicada sem resolução explícita."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from notebook_prescriber import prescribe_notebook  # noqa: E402
from test_notebook_prescriber import prescribe, snapshot  # noqa: E402


class PendentesTests(unittest.TestCase):
    def test_sem_pendencias_o_comportamento_nao_muda(self):
        self.assertEqual(prescribe(), prescribe(pending_recommendations=None))
        self.assertIsNone(prescribe()["supersedes"])
        self.assertEqual(prescribe(pending_recommendations=[])["status"], "recommended")

    def test_cdo14_pendente_identico_exige_reutilizacao_ou_substituicao(self):
        pend = prescribe()
        with self.assertRaisesRegex(ValueError, "duplicado"):
            prescribe(pending_recommendations=[pend])
        reuso = prescribe(pending_recommendations=[pend], pending_resolution={
            "action": "reuse", "recommendation_id": pend["recommendation_id"], "reason": "ainda não resolvido"})
        self.assertEqual(reuso["status"], "reused_pending")
        self.assertEqual(reuso["recommendation_id"], pend["recommendation_id"])
        self.assertFalse(reuso["side_effects_performed"])
        nova = prescribe(pending_recommendations=[pend], pending_resolution={
            "action": "replace", "recommendation_id": pend["recommendation_id"], "reason": "filtros mudaram"})
        self.assertEqual(nova["status"], "recommended")
        self.assertEqual(nova["supersedes"], pend["recommendation_id"])
        self.assertEqual(nova["supersede_reason"], "filtros mudaram")

    def test_fiq10_mesmo_candidato_com_outro_objetivo_continua_duplicado(self):
        pend = prescribe(objective="Linha de base sem consulta.")
        self.assertNotEqual(pend["recommendation_id"], prescribe()["recommendation_id"])
        with self.assertRaisesRegex(ValueError, "duplicado"):
            prescribe(objective="Outro objetivo.", pending_recommendations=[pend])

    def test_intervencao_ou_plataforma_diferente_nao_e_duplicada(self):
        pend = prescribe()
        self.assertEqual(prescribe(intervention="fixation", pending_recommendations=[pend])["status"], "recommended")
        self.assertEqual(prescribe(platform="TEC", pending_recommendations=[pend])["status"], "recommended")

    def test_resolucao_invalida_e_rejeitada(self):
        pend = prescribe()
        rid = pend["recommendation_id"]
        casos = {
            "ação inválida": {"action": "ignorar", "recommendation_id": rid, "reason": "x"},
            "id de outra pendência": {"action": "replace", "recommendation_id": "rec-outra", "reason": "x"},
            "sem justificativa": {"action": "replace", "recommendation_id": rid, "reason": "  "},
            "sem justificativa (ausente)": {"action": "reuse", "recommendation_id": rid},
            "não é objeto": "replace",
        }
        for nome, res in casos.items():
            with self.subTest(nome), self.assertRaises(ValueError):
                prescribe(pending_recommendations=[pend], pending_resolution=res)

    def test_resolucao_sem_pendencia_correspondente_e_rejeitada(self):
        with self.assertRaisesRegex(ValueError, "sem pendência"):
            prescribe(pending_resolution={"action": "replace", "recommendation_id": "rec-x", "reason": "x"})
        outra = prescribe(intervention="fixation")
        with self.assertRaisesRegex(ValueError, "sem pendência"):
            prescribe(pending_recommendations=[outra], pending_resolution={
                "action": "replace", "recommendation_id": outra["recommendation_id"], "reason": "x"})

    def test_pendencias_invalidas_sao_rejeitadas(self):
        for bad in ("x", {"a": 1}, [None], [{"candidate_id": "candidate-1"}], [{"recommendation_id": ""}]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                prescribe(pending_recommendations=bad)


if __name__ == "__main__":
    unittest.main()
