"""Independent audit assertions for PR5 NCs and 27 functional checks."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = json.loads((ROOT / "docs/governanca/RM07_MATRIZ_REAUDITORIA_9NC_27CHECKS_20261105.json").read_text(encoding="utf-8"))
R2_RECEIPT = json.loads((ROOT / ".specs/features/ufms-cognitive-gates/revisions/v0.3/approved-r2/approval-receipt.json").read_text(encoding="utf-8"))
R2_CHECKS = (ROOT / ".specs/features/ufms-cognitive-gates/revisions/v0.3/approved-r2/checks.md").read_text(encoding="utf-8")


class RM07AuditTests(unittest.TestCase):
    def test_nove_ncs_unicas_e_nenhuma_encerrada(self):
        rows = MATRIX["nonconformities"]
        self.assertEqual(len(rows), 9)
        self.assertEqual(len({row["nc_id"] for row in rows}), 9)
        self.assertTrue(all(row["closed"] is False for row in rows))
        self.assertEqual(MATRIX["summary"]["closed"], 0)

    def test_aprovacao_r2_na_main_e_documental_nao_gqd(self):
        approval = MATRIX["approval_r2_in_main"]
        self.assertEqual(approval["status"], "APPROVED_FOR_DOCUMENTARY_DERIVATION_NOT_GQ_D")
        self.assertEqual(approval["literal_user_message"], "APROVO")
        self.assertEqual(approval["functional_checks_pass"], 0)
        self.assertEqual(approval["functional_checks_not_run"], 27)
        self.assertEqual(R2_RECEIPT["independent_GQD"], "REPROVADA_PENDING_REAUDIT")
        self.assertEqual(R2_RECEIPT["VERIFY_C"], "NOT_RUN")
        self.assertEqual(R2_RECEIPT["VERIFY_O"], "BLOCKED")

    def test_27_checks_end_to_end_permanecem_nao_executados(self):
        checks = MATRIX["functional_checks"]
        self.assertEqual(len(checks), 27)
        self.assertEqual([row["check_id"] for row in checks], ["C" + str(i) for i in range(1, 28)])
        self.assertTrue(all(row["status"] == "NOT_RUN_END_TO_END" for row in checks))
        self.assertTrue(all(row["main_integration"] is False for row in checks))
        self.assertIn("0 PASS / 27 NOT_RUN", R2_CHECKS)

    def test_seletores_de_prova_tem_referencias(self):
        self.assertGreater(sum(len(row["proof_selectors"]) for row in MATRIX["functional_checks"]), 0)
        for row in MATRIX["functional_checks"]:
            self.assertTrue(row["acceptance_criterion"])

    def test_pr5_nao_e_mesclavel_em_lote(self):
        legacy = MATRIX["legacy_pr"]
        comparison = MATRIX["legacy_branch_comparison"]
        self.assertFalse(legacy["merged"])
        self.assertEqual(legacy["state"], "closed")
        self.assertEqual(comparison["ahead_by"], 22)
        self.assertEqual(comparison["behind_by"], 587)
        self.assertEqual(comparison["merge_strategy"], "NO_BULK_MERGE")

    def test_gateway_renderer_e_verificador_nao_estao_na_main_atual(self):
        self.assertFalse((ROOT / "scripts/tool_gateway.py").exists())
        self.assertFalse((ROOT / "scripts/safe_renderer.py").exists())
        self.assertFalse((ROOT / "tools/verify_spec.py").exists())
        self.assertFalse((ROOT / ".specs/features/ufms-cognitive-gates/revisions/v0.3/functional-tests").exists())
        self.assertTrue((ROOT / ".specs/features/ufms-cognitive-gates/revisions/v0.3/approved-r2/verify_approval_snapshot.py").exists())


if __name__ == "__main__":
    unittest.main()
