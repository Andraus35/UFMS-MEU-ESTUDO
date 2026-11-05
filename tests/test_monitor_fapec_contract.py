"""Contraprovas do contrato read-only e do monitoramento agendado FAPEC."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/monitor-fapec.yml").read_text(encoding="utf-8")
REGISTRY = json.loads((ROOT / "edital/fontes_oficiais.json").read_text(encoding="utf-8"))


class FapecWorkflowContractTests(unittest.TestCase):
    def test_workflow_tem_agendamento_e_dispatch_manual(self):
        self.assertIn("  schedule:", WORKFLOW)
        self.assertIn("cron: '17 12 * * *'", WORKFLOW)
        self.assertIn("  workflow_dispatch", WORKFLOW)

    def test_workflow_e_read_only_e_sem_credencial_persistida(self):
        self.assertIn("  contents: read", WORKFLOW)
        self.assertNotIn("contents: write", WORKFLOW)
        self.assertIn("persist-credentials: false", WORKFLOW)
        self.assertNotIn("GITHUB_TOKEN", WORKFLOW)

    def test_resultado_inconclusivo_ou_candidato_falha_fechado(self):
        self.assertIn('elif [ "$result" -eq 2 ]', WORKFLOW)
        self.assertIn('elif [ "$result" -eq 3 ]', WORKFLOW)
        self.assertGreaterEqual(WORKFLOW.count("exit 1"), 2)

    def test_edital_original_e_imutavel_e_retificacoes_nao_sao_aplicadas(self):
        self.assertIs(REGISTRY["amendment_policy"]["auto_apply"], False)
        self.assertEqual(REGISTRY["canonical"]["status"], "original_user_provided_hash_verified")
        self.assertEqual(REGISTRY["canonical"]["scope"], "não incorpora retificações")

    def test_alerta_cronologico_permanece_aberto(self):
        alerts = [x for x in REGISTRY["open_alerts"] if x["id"] == "ALERTA-DOC-01"]
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["status"], "unresolved_source_inconsistency")
        self.assertEqual(alerts[0]["resolution_document_id"], None)

    def test_equivalencia_de_bytes_remotos_nao_e_inferida(self):
        observation = REGISTRY["publication_observations"][0]
        institutional = REGISTRY["institutional_pdf_observations"][0]
        self.assertIsNone(observation["download_bytes_sha256"])
        self.assertEqual(observation["remote_pdf_equivalence"], "unverified")
        self.assertIsNone(institutional["pdf_bytes_sha256"])
        self.assertEqual(institutional["remote_pdf_equivalence"], "unverified")


if __name__ == "__main__":
    unittest.main()
