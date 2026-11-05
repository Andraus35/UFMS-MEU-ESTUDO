"""Mutation/adversarial tests of document reconciliation (never call GitHub)."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import saneamento_documental as sut


SHA = "a" * 40
MAIN = "b" * 40

DOCS = list(sut.TARGETS) + list(sut.PRESERVED)
NINE = ["AGENTS.md", "settings.json", "rules/CORE.md", "guardrails/CORE.md",
        "memory/INDEX.md", "memory/HANDOFF.md", "state/CURRENT.json",
        "EDITAL_UFMS_152_2026.md", "edital/INDEX.md"]


def fixture(root, ten=False):
    mandatory = NINE[:1] + ["ROADMAP.md"] + NINE[1:] if ten else NINE
    for name in set(DOCS):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# " + name + "\nHistoric text: PR #1 draft.\n",
                     encoding="utf-8")
    (root / "AGENTS.md").write_text("# Contract\n" +
                                    "\n".join(mandatory) + "\n", encoding="utf-8")
    (root / "settings.json").write_text(json.dumps({
        "bootstrap": {"mandatory": mandatory},
        "storage": {"repository_must_be_private_for_personal_results": True,
                    "personal_results_writes_enabled": False},
    }), encoding="utf-8")
    if ten:
        (root / "ROADMAP.md").write_text("# Roadmap\nRM-00 to RM-10\n",
                                         encoding="utf-8")


def snapshot():
    return {"repository": sut.REPOSITORY, "main_sha": MAIN,
            "visibility": "public", "main_protected": True,
            "pull_requests": [
                {"number": 1, "state": "closed", "merged": True,
                 "draft": False, "head": SHA, "base": "main"},
                {"number": 9, "state": "open", "merged": False,
                 "draft": True, "head": "c" * 40, "base": "main"},
                {"number": 10, "state": "closed", "merged": False,
                 "draft": True, "head": "d" * 40, "base": "main"},
            ]}


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        fixture(self.root)

    def test_detect_and_repair_bounded_changes(self):
        before = (self.root / "memory/HANDOFF.md").read_bytes()
        delta = sut.changes(self.root, snapshot(), "audit/example", SHA)
        self.assertIn(sut.STATUS_PATH, delta)
        for path, value in delta.items():
            sut.write_atomic(sut.safe_file(self.root, path, allow_missing=True),
                             value)
        self.assertFalse(sut.changes(self.root, snapshot(), "audit/example", SHA))
        after = (self.root / "memory/HANDOFF.md").read_bytes()
        self.assertTrue(after.startswith(b"# memory/HANDOFF.md\n"))
        self.assertIn(b"Historic text: PR #1 draft.\n", after)
        self.assertEqual(after.count(sut.START.encode()), 1)

    def test_non_destructive_historical_adr(self):
        delta = sut.changes(self.root, snapshot(), "audit/example", SHA)
        self.assertIn("não são apagados", delta["memory/DECISIONS.md"])
        self.assertIn("Historic text: PR #1 draft.",
                      delta["memory/DECISIONS.md"])

    def test_nine_and_ten_bootstrap_supported(self):
        self.assertEqual(sut.validate_local(self.root)["mandatory_count"], 9)
        fixture(self.root, ten=True)
        self.assertEqual(sut.validate_local(self.root)["mandatory_count"], 10)

    def test_bootstrap_mismatch_fails_closed(self):
        (self.root / "ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
        with self.assertRaisesRegex(sut.ReconciliationError,
                                    "ROADMAP presence"):
            sut.validate_local(self.root)

    def test_private_results_flag_cannot_be_enabled(self):
        path = self.root / "settings.json"
        cfg = json.loads(path.read_text(encoding="utf-8"))
        cfg["storage"]["personal_results_writes_enabled"] = True
        path.write_text(json.dumps(cfg), encoding="utf-8")
        with self.assertRaisesRegex(sut.ReconciliationError,
                                    "Personal-result"):
            sut.validate_local(self.root)

    def test_duplicate_pr_refused(self):
        data = snapshot()
        data["pull_requests"].append(dict(data["pull_requests"][0]))
        with self.assertRaisesRegex(sut.ReconciliationError,
                                    "duplicated PR"):
            sut.validate_snapshot(data)

    def test_merged_pr_marked_open_refused(self):
        data = snapshot()
        data["pull_requests"][0]["state"] = "open"
        with self.assertRaisesRegex(sut.ReconciliationError, "cannot be open"):
            sut.validate_snapshot(data)

    def test_symlink_target_refused(self):
        target = self.root / "memory/INDEX.md"
        target.unlink()
        target.symlink_to(self.root / "settings.json")
        with self.assertRaisesRegex(sut.ReconciliationError, "Symlink"):
            sut.changes(self.root, snapshot(), "audit/example", SHA)

    def test_broken_marker_refused(self):
        path = self.root / "memory/INDEX.md"
        path.write_text("# Memory\n" + sut.START + "\nUnpaired\n",
                        encoding="utf-8")
        with self.assertRaisesRegex(sut.ReconciliationError, "managed-block"):
            sut.changes(self.root, snapshot(), "audit/example", SHA)

    def test_gate_matrix_has_separate_authorities(self):
        doc = sut.status_document(snapshot(), sut.validate_local(self.root),
                                  "audit/example", SHA)
        self.assertIn("## Matriz de gates e autoridade", doc)
        self.assertIn("GQ-D / GQ-C / GQ-O", doc)
        self.assertIn("não exige autorização humana por mensagem", doc)

    def test_markup_untrusted_is_not_executed(self):
        data = snapshot()
        data["pull_requests"][1]["base"] = "main|malicious\nheader"
        rendered = sut.status_document(data, sut.validate_local(self.root),
                                       "audit/example", SHA)
        self.assertIn("main\\|malicious header", rendered)
        self.assertNotIn("main|malicious\n", rendered)

    def test_self_candidate_does_not_self_invalidate(self):
        current = snapshot()
        current["pull_requests"].append({
            "number": 12, "state": "open", "merged": False,
            "draft": True, "head": SHA, "base": "main"})
        before = sut.status_document(current, sut.validate_local(self.root),
                                     "audit/example", SHA)
        current["pull_requests"][-1]["head"] = "e" * 40
        after = sut.status_document(current, sut.validate_local(self.root),
                                    "audit/example", "e" * 40)
        self.assertEqual(before, after)
        self.assertIn("SELF_CANDIDATE", after)

    def test_no_permission_to_edit_policies_or_private_state(self):
        for path in ("state/CURRENT.json", "AGENTS.md", "settings.json",
                     ".github/workflows/validate.yml",
                     "scripts/api_write_guard.py"):
            if path in (sut.PRESERVED + tuple(sut.TARGETS) + (sut.STATUS_PATH,)):
                continue
            with self.assertRaises(sut.ReconciliationError):
                sut.safe_file(self.root, path, allow_missing=True)
        keys = sut.changes(self.root, snapshot(), "audit/example", SHA)
        self.assertNotIn("settings.json", keys)
        self.assertNotIn("AGENTS.md", keys)

    def test_reapply_updates_only_generated_metadata(self):
        original = (self.root / "docs/pedagogia/HANDOFF.md").read_text()
        for p, content in sut.changes(self.root, snapshot(), "audit/example", SHA).items():
            sut.write_atomic(sut.safe_file(self.root, p, allow_missing=True), content)
        later = snapshot()
        later["pull_requests"][1]["state"] = "closed"
        diff = sut.changes(self.root, later, "audit/example", SHA)
        self.assertIn("docs/pedagogia/HANDOFF.md", diff)
        self.assertTrue(diff["docs/pedagogia/HANDOFF.md"].startswith(
            "# docs/pedagogia/HANDOFF.md\n"))
        self.assertIn("Historic text: PR #1 draft.\n",
                      diff["docs/pedagogia/HANDOFF.md"])
        self.assertEqual(diff["docs/pedagogia/HANDOFF.md"].count(sut.START), 1)


if __name__ == "__main__":
    unittest.main()
