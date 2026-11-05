"""Protege a main contra ativacao acidental da ponte externa nao homologada."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Sim08ExternalBridgeTests(unittest.TestCase):
    def test_oracle_bridge_runtime_and_workflow_remain_absent(self):
        self.assertFalse((ROOT / "integrations/oracle_bridge").exists())
        self.assertFalse((ROOT / ".github/workflows/oracle-bridge-ci.yml").exists())

    def test_decision_keeps_all_external_effects_deferred(self):
        decision = (ROOT / "docs/governanca/DECISAO_ORACLE_TELEGRAM_CALENDAR.md").read_text(encoding="utf-8")
        self.assertIn("Não importar o código", decision)
        self.assertIn("Nenhum bot ou calendário foi criado", decision)
        self.assertIn("auditoria independente", decision)

    def test_personal_results_remain_disabled(self):
        settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertFalse(settings["storage"]["personal_results_writes_enabled"])


if __name__ == "__main__":
    unittest.main()
