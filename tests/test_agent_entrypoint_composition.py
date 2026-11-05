"""Real-tree composition tests. External operations are never performed."""
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from agent_entrypoint import AgentBroker, GateClosed, MANDATORY, verify_start

SHA = "f" * 40

class ComposedBrokerTests(unittest.TestCase):
    def setUp(self):
        self.head = patch("agent_entrypoint._git_head", return_value=SHA)
        self.clean = patch("agent_entrypoint._git_clean")
        self.head.start()
        self.clean.start()
        self.addCleanup(self.head.stop)
        self.addCleanup(self.clean.stop)

    def broker(self):
        return AgentBroker(ROOT, SHA)

    def test_real_repo_has_ten_verified_documents(self):
        current = verify_start(ROOT, SHA)
        self.assertEqual(set(current["hashes"]), set(MANDATORY))
        self.assertEqual(len(current["hashes"]), 10)
        self.assertIn("RM-10", current["roadmap"])

    def test_all_hashes_match_real_bytes(self):
        data = self.broker().document_manifest()
        self.assertFalse(data["external_effects_enabled"])
        self.assertEqual(data["mandatory_count"], 10)
        for rel, digest in data["sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), digest)

    def test_limited_text_read_is_hash_checked(self):
        broker = self.broker()
        selected = broker.read_verified_document("edital/INDEX.md")
        self.assertEqual(selected["path"], "edital/INDEX.md")
        self.assertIn("sha256", selected)
        self.assertTrue(selected["text"].strip())

    def test_large_canonical_edital_not_injected_into_prompt(self):
        with self.assertRaisesRegex(GateClosed, "too large"):
            self.broker().read_verified_document("EDITAL_UFMS_152_2026.md")

    def test_no_unscoped_or_secret_file_read(self):
        broker = self.broker()
        for rel in ("../settings.json", ".env", "state/events/2026-11.jsonl",
                    "docs/governanca/STATUS_VIGENTE.md"):
            with self.subTest(rel=rel), self.assertRaisesRegex(
                    GateClosed, "outside mandatory"):
                broker.read_verified_document(rel)

    def test_model_preamble_gets_autonomy_but_no_external_power(self):
        broker = self.broker()
        a, r = broker.prompt_context()
        self.assertIn("sem aprovação humana por mensagem", a)
        self.assertIn("RM-10", r)
        self.assertEqual(broker.request("tutor", "start")["scope"],
                         "local_read_only")
        for action in ("zapia.send", "calendar.create", "github.write",
                       "private.store", "merge"):
            with self.subTest(action=action), self.assertRaises(GateClosed):
                broker.request("coach", action)

    def test_invalid_max_bytes_rejected(self):
        broker = self.broker()
        for limit in (True, False, 0, -1, 32769, "1024"):
            with self.subTest(limit=limit), self.assertRaisesRegex(
                    GateClosed, "Invalid bounded"):
                broker.read_verified_document("edital/INDEX.md",
                                             max_bytes=limit)
if __name__ == "__main__":
    unittest.main()
