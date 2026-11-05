"""Contraprovas para impedir regressao ao broker legado das branches #11/#15."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Sim05ReconciliationTests(unittest.TestCase):
    def test_current_broker_is_role_scoped_read_only_broker(self):
        source = (ROOT / "scripts/agent_entrypoint.py").read_text(encoding="utf-8")
        self.assertIn("class ReadOnlyAgentBroker:", source)
        self.assertIn('"tutor": "study"', source)
        self.assertIn('"engineer": "engineering"', source)
        self.assertIn('"external_effects_enabled": False', source)
        self.assertNotIn("class AgentBroker:", source)

    def test_current_broker_uses_current_bootstrap_not_legacy_ten_file_list(self):
        source = (ROOT / "scripts/agent_entrypoint.py").read_text(encoding="utf-8")
        self.assertIn("bootstrap_run(root, mode=mode)", source)
        self.assertIn("state/WORKFLOW.json", source)
        self.assertNotIn("MANDATORY = (", source)

    def test_legacy_composition_api_is_not_reintroduced(self):
        source = (ROOT / "scripts/agent_entrypoint.py").read_text(encoding="utf-8")
        for legacy_api in ("def document_manifest(", "def read_verified_document(",
                           "def prompt_context(self)"):
            with self.subTest(api=legacy_api):
                self.assertNotIn(legacy_api, source)
        self.assertIn("def model_context(self):", source)

    def test_workflow_has_one_current_sim05_task(self):
        state = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
        self.assertEqual(state["active"]["task_id"], "SIM-05")
        self.assertEqual(state["active"]["pr_number"], 22)
        self.assertEqual(state["active"]["phase"], "review")
        self.assertEqual(state["next_task_after_merge"], "SIM-06")
        self.assertEqual(state["last_merged"]["pr_number"], 21)

    def test_handoff_and_adr_record_non_reintegration_decision(self):
        handoff = (ROOT / "memory/HANDOFF.md").read_text(encoding="utf-8")
        decisions = (ROOT / "memory/DECISIONS.md").read_text(encoding="utf-8")
        self.assertIn("branches #11/#12/#14/#15", handoff)
        self.assertIn("ADR-010", decisions)
        self.assertIn("não reintegrar", decisions.lower())


if __name__ == "__main__":
    unittest.main()
