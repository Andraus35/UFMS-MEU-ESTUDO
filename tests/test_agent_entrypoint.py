"""Adversarial offline tests: no START, no operation."""
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from agent_entrypoint import AgentBroker, GateClosed, MANDATORY, verify_start

HEAD = "e" * 40


def fake_roadmap():
    lines = ["# ROADMAP — UFMS MEU ESTUDO", "## Governança e leitura obrigatória",
             "## Fila de execução", "| ID | P | Frente | Estado | Definition of Done |",
             "| --- | --- | --- | --- | --- |"]
    for i in range(11):
        lines.append(f"| RM-{i:02d} | P0 | Ação de referência {i} | planejado |"
                     " Exigir comprovação por testes e evidência do HEAD exato |")
    lines.append("## Critérios de promoção")
    return "\n".join(lines) + "\n" + ("Referências auditáveis. " * 150)


class EntryGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in MANDATORY:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Documento válido de teste.", encoding="utf-8")
        (self.root / "AGENTS.md").write_text(
            "# Contrato\n1. `AGENTS.md`\n2. `ROADMAP.md`\n", encoding="utf-8"
        )
        (self.root / "ROADMAP.md").write_text(fake_roadmap(), encoding="utf-8")
        (self.root / "settings.json").write_text(
            json.dumps({"bootstrap": {"mandatory": list(MANDATORY)}}), encoding="utf-8"
        )
        # Test doubles are ONLY test-level patches; no production bypass flags.
        self.head_patch = mock.patch("agent_entrypoint._git_head", return_value=HEAD)
        self.clean_patch = mock.patch("agent_entrypoint._git_clean")
        self.head_mock = self.head_patch.start()
        self.clean_mock = self.clean_patch.start()
        self.addCleanup(self.head_patch.stop)
        self.addCleanup(self.clean_patch.stop)

    def verify(self):
        return verify_start(self.root, HEAD)

    def broker(self):
        return AgentBroker(self.root, HEAD)

    def test_pass_valid_snapshot(self):
        result = self.verify()
        self.assertEqual(len(result["hashes"]), 10)
        self.assertIn("RM-10", result["roadmap"])

    def test_fail_missing_roadmap(self):
        (self.root / "ROADMAP.md").unlink()
        with self.assertRaisesRegex(GateClosed, "missing"):
            self.verify()

    def test_fail_invalid_or_incomplete_roadmap(self):
        path = self.root / "ROADMAP.md"
        for text in ("placeholder", fake_roadmap().replace("RM-09", "RM-08"),
                     fake_roadmap().replace("| planejado |", "| homologacao_falsa |", 1)):
            with self.subTest(length=len(text)):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(GateClosed):
                    self.verify()

    def test_fail_wrong_order(self):
        config = self.root / "settings.json"
        bad = list(MANDATORY)
        bad[1], bad[2] = bad[2], bad[1]
        config.write_text(json.dumps({"bootstrap": {"mandatory": bad}}))
        with self.assertRaisesRegex(GateClosed, "order"):
            self.verify()

    def test_fail_other_head_and_dirty_checkout(self):
        self.head_mock.return_value = "f" * 40
        with self.assertRaisesRegex(GateClosed, "HEAD"):
            self.verify()
        self.head_mock.return_value = HEAD
        self.clean_mock.side_effect = GateClosed("Dirty checkout")
        with self.assertRaisesRegex(GateClosed, "Dirty"):
            self.verify()
        self.clean_mock.side_effect = None
        with self.assertRaisesRegex(GateClosed, "Trusted SHA"):
            verify_start(self.root, "")

    def test_fail_symlinked_mandatory(self):
        linked = self.root / "rules/CORE.md"
        linked.unlink()
        linked.symlink_to(self.root / "AGENTS.md")
        with self.assertRaisesRegex(GateClosed, "escaped"):
            self.verify()

    def test_no_powers_after_start(self):
        broker = self.broker()
        for role in ("tutor", "coach", "engineer", "auditor"):
            self.assertEqual(broker.request(role, "start")["status"], "bootstrap_verified")
        for action in ("telegram.send", "calendar.create", "github.write",
                       "execute", "merge", "delete", "post_result"):
            with self.subTest(action=action), self.assertRaisesRegex(GateClosed, "No protected writes"):
                broker.request("tutor", action)

    def test_stale_bootstrap_receipt_cannot_be_replayed(self):
        broker = self.broker()
        self.assertEqual(broker.request("tutor", "start")["status"], "bootstrap_verified")
        (self.root / "ROADMAP.md").write_text("placeholder", encoding="utf-8")
        with self.assertRaisesRegex(GateClosed, "truncated"):
            broker.request("tutor", "inspect")
        with self.assertRaisesRegex(GateClosed, "truncated"):
            broker.prompt_context()

    def test_branch_switch_after_start_cannot_reuse_receipt(self):
        broker = self.broker()
        self.head_mock.return_value = "f"*40
        with self.assertRaisesRegex(GateClosed, "HEAD"):
            broker.request("coach", "start")

    def test_refuse_unregistered_role_and_context(self):
        broker = self.broker()
        with self.assertRaisesRegex(GateClosed, "Unknown"):
            broker.request("copilot-write", "start")
        agents, roadmap = broker.prompt_context()
        self.assertIn("ROADMAP.md", agents)
        self.assertIn("RM-10", roadmap)


if __name__ == "__main__":
    unittest.main()
