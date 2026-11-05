"""Integration tests: the composed real repository must be self-consistent.

No GitHub calls, no mocks of the documents under test, no writes. The
recorded snapshot is reconstructed from the versioned STATUS_VIGENTE.md.
This verifies idempotence of the generated output against the actual PR tree,
not merely a small in-memory fixture.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import saneamento_documental as sut

SELF = "a" * 40
BRANCH = "audit/compose-roadmap-document-reconciliation-20261105"
STATUS = ROOT / sut.STATUS_PATH
ROW = re.compile(
    r"^\| #([0-9]+) \| (MERGED|CLOSED_UNMERGED|OPEN_DRAFT|OPEN_READY) "
    r"\| ([a-f0-9]{40}|SELF_CANDIDATE) \| ([^|]+) \|$")


def read_snapshot():
    body = STATUS.read_text(encoding="utf-8")
    def field(prefix):
        found = [line[len(prefix):] for line in body.splitlines()
                 if line.startswith(prefix)]
        if len(found) != 1:
            raise ValueError("Missing or duplicated status field: " + prefix)
        return found[0]
    prs = []
    for line in body.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        number, status, sha, base = match.groups()
        prs.append({
            "number": int(number),
            "state": "open" if status.startswith("OPEN_") else "closed",
            "merged": status == "MERGED",
            "draft": status == "OPEN_DRAFT",
            "head": SELF if sha == "SELF_CANDIDATE" else sha,
            "base": base,
        })
    if not prs:
        raise ValueError("No recorded PR evidence")
    main = field("- Main (HEAD confirmado): ")
    visibility = field("- Visibilidade: ")
    protected = field("- Campo main.protected: ").split(" ", 1)[0] == "true"
    record = {"repository": sut.REPOSITORY, "main_sha": main,
              "visibility": visibility, "main_protected": protected,
              "pull_requests": prs}
    sut.validate_snapshot(record)
    return record, body


class ComposedRepositoryTests(unittest.TestCase):
    def test_actual_bootstrap_ten_and_personal_results_denied(self):
        observed = sut.validate_local(ROOT)
        self.assertEqual(observed["mandatory_count"], 10)
        self.assertTrue(observed["has_roadmap"])
        self.assertIn("## Autonomia cognitiva e gates proporcionais",
                      (ROOT / "ROADMAP.md").read_text(encoding="utf-8"))

    def test_all_status_headers_exist_once_with_valid_reference(self):
        for path, relative in sut.TARGETS.items():
            with self.subTest(path=path):
                data = (ROOT / path).read_text(encoding="utf-8")
                self.assertEqual(data.count(sut.START), 1)
                self.assertEqual(data.count(sut.END), 1)
                self.assertIn("STATUS_VIGENTE.md", data)
                dest = (ROOT / path).parent / relative
                self.assertTrue(dest.is_file(), path)

    def test_pr9_preface_is_preserved_after_managed_header(self):
        data = (ROOT / "memory/HANDOFF.md").read_text(encoding="utf-8")
        self.assertTrue(data.startswith(sut.START))
        self.assertGreater(data.index("> **Handoff corretivo vigente"),
                           data.index(sut.END))
        self.assertGreater(data.index("# Handoff — harness"),
                           data.index("> **ESTADO VIGENTE EM"))

    def test_status_file_matches_pure_reconciliation_no_drift(self):
        snap, doc = read_snapshot()
        self.assertEqual(
            len([p for p in snap["pull_requests"] if p["head"] == SELF]), 1)
        self.assertIn("Bootstrap desta revisão: 10 documentos", doc)
        self.assertIn("ROADMAP incluído: true", doc)
        differences = sut.changes(ROOT, snap, BRANCH, SELF)
        if differences:
            import difflib
            current = (ROOT / sut.STATUS_PATH).read_text(encoding="utf-8")
            expected = differences.get(sut.STATUS_PATH, current)
            excerpt = "".join(list(difflib.unified_diff(
                current.splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile="committed", tofile="generated"))[:55])
            self.fail("Committed documents drift from deterministic output:\n"
                      + excerpt + "\nchanged=" + repr(sorted(differences)))


if __name__ == "__main__":
    unittest.main()
