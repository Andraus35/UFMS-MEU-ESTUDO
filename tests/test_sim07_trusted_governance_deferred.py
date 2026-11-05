"""Protege a decisão de não instalar a proposta externa ainda não homologada."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Sim07TrustedGovernanceTests(unittest.TestCase):
    def test_no_unhomologated_external_app_oracle_runtime(self):
        self.assertFalse((ROOT / "scripts/trusted_governance.py").exists())
        self.assertFalse((ROOT / "scripts/trusted_app_check.py").exists())
        self.assertFalse((ROOT / ".github/workflows/trusted-governance.yml").exists())

    def test_decision_documents_the_stale_check_limitation(self):
        decision = (ROOT / "docs/governanca/DECISAO_TRUSTED_GOVERNANCE.md").read_text(encoding="utf-8")
        adr = (ROOT / "docs/ADR_P0_APP_OUTAGE.md")
        self.assertTrue(adr.exists() is False)
        self.assertIn("não é lease aplicada pelo GitHub", decision)
        self.assertIn("Não integrar", decision)

    def test_no_credentials_or_personal_results_enabled(self):
        settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertFalse(settings.get("personal_results_writes_enabled", False))
        decision = (ROOT / "docs/governanca/DECISAO_TRUSTED_GOVERNANCE.md").read_text(encoding="utf-8")
        self.assertIn("Nenhuma chave privada", decision)


if __name__ == "__main__":
    unittest.main()
