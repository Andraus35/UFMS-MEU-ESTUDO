"""Adversarial tests for the read-only PR #5 composition contract."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prove import PREFIX, REQUIRED, R2_PLAN_SHA256, R2_CHECKS_SHA256
from prove import git_blob, verify_parent_chain, verify_event

BASE = "a" * 40
HEAD = "b" * 40
MERGE = "c" * 40


def event():
    return {
        "repository": {"full_name": "Andraus35/UFMS-MEU-ESTUDO"},
        "pull_request": {"number": 5, "state": "open",
                         "base": {"ref": "main"}, "head": {"sha": HEAD}},
    }


class CompositionContractTests(unittest.TestCase):
    def test_correct_parent_order(self):
        self.assertTrue(verify_parent_chain([BASE, HEAD], BASE, HEAD))

    def test_swap_or_missing_parent_fails(self):
        for parents in ([HEAD, BASE], [BASE], [], [BASE, HEAD, HEAD]):
            with self.subTest(parents=parents), self.assertRaisesRegex(
                    ValueError, "COMPOSITION_PARENT_DRIFT"):
                verify_parent_chain(parents, BASE, HEAD)

    def test_moving_main_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "COMPOSITION_PARENT_DRIFT"):
            verify_parent_chain([BASE, HEAD], "d" * 40, HEAD)

    def test_non_pr5_or_foreign_repo_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            for field in ("number", "repository", "base"):
                payload = event()
                if field == "number":
                    payload["pull_request"]["number"] = 4
                elif field == "repository":
                    payload["repository"]["full_name"] = "other/repo"
                else:
                    payload["pull_request"]["base"]["ref"] = "test"
                with self.subTest(field=field), self.assertRaises(ValueError):
                    verify_event(payload, [BASE, HEAD], MERGE, BASE, tmp)

    def test_missing_harness_fails_even_when_parents_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "COMPOSITION_FILE_MISSING"):
                verify_event(event(), [BASE, HEAD], MERGE, BASE, tmp)

    def test_provenance_pins_are_canonical_shapes(self):
        self.assertEqual(len(REQUIRED), 11)
        self.assertEqual(len(R2_PLAN_SHA256), 64)
        self.assertEqual(len(R2_CHECKS_SHA256), 64)
        self.assertTrue(str(PREFIX).endswith("revisions/v0.3"))

    def test_git_blob_follows_git_hash_object(self):
        raw = b"abc"
        self.assertEqual(
            git_blob(raw),
            hashlib.sha1(b"blob 3\0abc").hexdigest(),
        )

    def test_real_composition_if_present(self):
        repo = Path(__file__).resolve().parents[6]
        if (repo / "edital/manifest.json").is_file():
            from prove import verify_paths
            self.assertTrue(verify_paths(repo))


if __name__ == "__main__":
    unittest.main()
