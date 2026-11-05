"""Negative tests for the live draft-PR preflight; no external API calls."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from api_write_guard import (
    check_proposal, check_authenticated_proposal,
    check_authenticated_commit_readback, github_get_live,
)

REPO = "Andraus35/UFMS-MEU-ESTUDO"
ROOT = "repos/" + REPO
HEAD, BASE, BLOB = "a"*40, "b"*40, "c"*40
BRANCH = "audit/clean-docs-20261105"

def proposal(number=12, operation="update", path="docs/OPERACAO.md"):
    return {
        "repository": REPO, "branch": BRANCH, "base_branch": "main",
        "pr_number": number, "draft": True, "merged": False, "state": "open",
        "expected_head_sha": HEAD, "observed_head_sha": HEAD,
        "files": [{"path": path, "operation": operation,
                   "expected_blob_sha": BLOB if operation == "update" else None,
                   "expected_new_blob_sha": "f" * 40}],
    }

def fixture(p):
    file_path = p["files"][0]["path"]
    exists = p["files"][0]["operation"] == "update"
    return {
        ROOT + "/pulls/" + str(p["pr_number"]): {"status": 200, "body": {
            "number": p["pr_number"], "state": "open", "draft": True,
            "merged_at": None, "head": {
                "sha": HEAD, "ref": BRANCH, "repo": {"full_name": REPO}},
            "base": {
                "sha": BASE, "ref": "main", "repo": {"full_name": REPO}},
        }},
        ROOT + "/branches/main": {"status": 200, "body": {"commit": {"sha": BASE}}},
        ROOT + "/branches/" + BRANCH: {
            "status": 200, "body": {"commit": {"sha": HEAD}}},
        ROOT + "/contents/" + file_path + "?ref=" + HEAD: {
            "status": 200 if exists else 404,
            "body": {"type": "file", "sha": BLOB} if exists
                    else {"message": "Not Found"}},
    }

class ApiRemoteTests(unittest.TestCase):
    def setUp(self):
        self.p = proposal()
        self.items = fixture(self.p)

    def verify(self, p=None, data=None):
        return check_authenticated_proposal(
            p if p is not None else self.p,
            (data if data is not None else self.items).__getitem__)

    def test_open_draft_pr12_passes_with_readbacks(self):
        out = self.verify()
        self.assertEqual(out["pr_number"], 12)
        self.assertTrue(out["authenticated_remote_read"])
        self.assertFalse(out["merge_authorized"])
        self.assertFalse(out["server_side_enforcement"])

    def test_other_positive_pr_can_be_valid(self):
        for number in (9, 12, 31):
            p = proposal(number)
            self.assertEqual(self.verify(p, fixture(p))["pr_number"], number)

    def test_standalone_structural_check_is_not_remote(self):
        self.assertFalse(check_proposal(self.p)["authenticated_remote_read"])

    def test_invalid_pr_number_rejected(self):
        for number in (0, True, False, -1, "12"):
            with self.subTest(number=number):
                with self.assertRaisesRegex(ValueError, "inteiro positivo"):
                    check_proposal(proposal(number))

    def test_pr_not_draft_closed_or_merged_rejected(self):
        key = ROOT + "/pulls/12"
        for change in ({"state": "closed"}, {"draft": False},
                       {"merged_at": "2026-11-04T00:00:00Z"},
                       {"merged": True}):
            data = copy.deepcopy(self.items)
            data[key]["body"].update(change)
            with self.assertRaisesRegex(ValueError, "closed, merged or not draft"):
                self.verify(data=data)

    def test_head_sha_ref_fork_and_base_mismatch_rejected(self):
        key = ROOT + "/pulls/12"
        for item, prop, val in (
            ("head", "sha", "d"*40), ("head", "ref", "main"),
            ("head", "repo", {"full_name": "evil/fork"}),
            ("base", "ref", "feature"),
            ("base", "repo", {"full_name": "evil/fork"}),
        ):
            data = copy.deepcopy(self.items)
            data[key]["body"][item][prop] = val
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                self.verify(data=data)

    def test_main_moves_or_base_is_stale_rejected(self):
        data = copy.deepcopy(self.items)
        data[ROOT + "/branches/main"]["body"]["commit"]["sha"] = "d"*40
        with self.assertRaisesRegex(ValueError, "base stale"):
            self.verify(data=data)

    def test_branch_moves_before_write_rejected(self):
        data = copy.deepcopy(self.items)
        data[ROOT + "/branches/" + BRANCH]["body"]["commit"]["sha"] = "d"*40
        with self.assertRaisesRegex(ValueError, "HEAD changed"):
            self.verify(data=data)

    def test_blob_change_symlink_or_missing_rejected(self):
        key = ROOT + "/contents/docs/OPERACAO.md?ref=" + HEAD
        for val in ({"sha": "d"*40, "type": "file"},
                    {"sha": BLOB, "type": "symlink"},
                    {"message": "Not Found"}):
            data = copy.deepcopy(self.items)
            data[key] = {"status": 200 if "sha" in val else 404, "body": val}
            with self.assertRaisesRegex(ValueError, "Blob not confirmed"):
                self.verify(data=data)

    def test_verified_create_accepts_404_only(self):
        p = proposal(operation="create", path="docs/new.md")
        self.assertTrue(self.verify(p, fixture(p))["authenticated_remote_read"])
        data = fixture(p)
        data[ROOT + "/contents/docs/new.md?ref=" + HEAD] = {
            "status": 200, "body": {"type": "file", "sha": BLOB}}
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.verify(p, data)

    def test_api_403_429_and_incomplete_rejected(self):
        for status in (403, 429):
            data = copy.deepcopy(self.items)
            data[ROOT + "/pulls/12"]["status"] = status
            with self.assertRaisesRegex(ValueError, "Authenticated read rejected"):
                self.verify(data=data)
        data = copy.deepcopy(self.items)
        del data[ROOT + "/pulls/12"]
        with self.assertRaisesRegex(ValueError, "Authenticated read unavailable"):
            self.verify(data=data)

    def test_governance_and_personal_files_remain_blocked(self):
        for path in ("settings.json", "AGENTS.md", "rules/CORE.md",
                     "state/CURRENT.json", "scripts/api_write_guard.py",
                     ".github/workflows/validate.yml"):
            with self.assertRaisesRegex(ValueError, "sensível"):
                check_proposal(proposal(path=path))

    def postcommit(self):
        data = copy.deepcopy(self.items)
        data[ROOT + "/pulls/12"]["body"]["head"]["sha"] = "d" * 40
        data[ROOT + "/branches/" + BRANCH]["body"]["commit"]["sha"] = "d" * 40
        data[ROOT + "/git/commits/" + "d" * 40] = {
            "status": 200, "body": {"parents": [{"sha": HEAD}]}}
        data[ROOT + "/compare/" + HEAD + "..." + "d" * 40] = {
            "status": 200, "body": {
                "status": "ahead", "ahead_by": 1, "behind_by": 0,
                "total_commits": 1,
                "files": [{"filename": "docs/OPERACAO.md", "status": "modified",
                           "sha": "f" * 40}]}}
        data[ROOT + "/contents/docs/OPERACAO.md?ref=" + "d" * 40] = {
            "status": 200, "body": {"type": "file", "sha": "f" * 40}}
        return data

    def test_postcommit_live_readback_passes_without_ci_promotion(self):
        d = self.postcommit()
        result = check_authenticated_commit_readback(
            self.p, "d" * 40, BASE, d.__getitem__)
        self.assertTrue(result["authenticated_remote_read"])
        self.assertFalse(result["ci_verified"])
        self.assertFalse(result["merge_authorized"])
        self.assertEqual(result["changed_files_verified"], 1)
        self.assertTrue(result["content_bound_to_proposal"])
        self.assertEqual(result["readback"],
                         "authenticated_postcommit_exact_file_delta")

    def test_postcommit_pr_retarget_fails_closed(self):
        d = self.postcommit()
        d[ROOT + "/pulls/12"]["body"]["base"]["ref"] = "feature"
        with self.assertRaisesRegex(ValueError, "identity or base changed"):
            check_authenticated_commit_readback(
                self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_rewritten_head_fails_closed(self):
        d = self.postcommit()
        d[ROOT + "/pulls/12"]["body"]["head"]["sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "identity or base changed"):
            check_authenticated_commit_readback(
                self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_main_moved_fails_closed(self):
        d = self.postcommit()
        d[ROOT + "/branches/main"]["body"]["commit"]["sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "Main changed"):
            check_authenticated_commit_readback(
                self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_wrong_parent_rejected(self):
        d = self.postcommit()
        d[ROOT + "/git/commits/" + "d" * 40]["body"]["parents"] = [
            {"sha": "e" * 40}]
        with self.assertRaisesRegex(ValueError, "not a direct descendant"):
            check_authenticated_commit_readback(
                self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_merge_commit_rejected(self):
        d = self.postcommit()
        d[ROOT + "/git/commits/" + "d" * 40]["body"]["parents"] = [
            {"sha": HEAD}, {"sha": BASE}]
        with self.assertRaisesRegex(ValueError, "not a direct descendant"):
            check_authenticated_commit_readback(
                self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_branch_changed_rejected(self):
        d = self.postcommit()
        d[ROOT + "/branches/" + BRANCH]["body"]["commit"]["sha"] = HEAD
        with self.assertRaisesRegex(ValueError, "did not advance"):
            check_authenticated_commit_readback(
                self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_git_read_unavailable_rejected(self):
        d = self.postcommit()
        del d[ROOT + "/git/commits/" + "d" * 40]
        with self.assertRaisesRegex(ValueError, "Authenticated read unavailable"):
            check_authenticated_commit_readback(
                self.p, "d" * 40, BASE, d.__getitem__)


    def test_postcommit_sensitive_extra_file_rejected(self):
        d = self.postcommit()
        diff = d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]["body"]
        diff["files"].append({"filename": ".github/workflows/validate.yml",
                              "status": "modified", "sha": "e" * 40})
        with self.assertRaisesRegex(ValueError, "changed-file set"):
            check_authenticated_commit_readback(self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_same_path_wrong_final_content_rejected(self):
        d = self.postcommit()
        diff = d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]["body"]
        diff["files"][0]["sha"] = "e" * 40
        d[ROOT + "/contents/docs/OPERACAO.md?ref=" + "d" * 40]["body"]["sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "proposed final content"):
            check_authenticated_commit_readback(self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_unexpected_file_rejected(self):
        d = self.postcommit()
        d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]["body"]["files"][0]["filename"] = "docs/other.md"
        with self.assertRaisesRegex(ValueError, "Unexpected file"):
            check_authenticated_commit_readback(self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_remove_rename_or_wrong_operation_rejected(self):
        for status in ("removed", "renamed", "added"):
            with self.subTest(status=status):
                d = self.postcommit()
                d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]["body"]["files"][0]["status"] = status
                with self.assertRaisesRegex(ValueError, "Unexpected file"):
                    check_authenticated_commit_readback(self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_missing_or_truncated_delta_rejected(self):
        for mode in ("missing", "empty", "malformed", "no_blob"):
            with self.subTest(mode=mode):
                d = self.postcommit()
                diff = d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]["body"]
                if mode == "missing": diff.pop("files")
                elif mode == "empty": diff["files"] = []
                elif mode == "malformed": diff["files"] = "not a list"
                else: diff["files"][0].pop("sha")
                with self.assertRaises(ValueError):
                    check_authenticated_commit_readback(self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_diff_must_be_exact_one_commit(self):
        for field, value in (("status", "diverged"), ("ahead_by", 2),
                             ("behind_by", 1), ("total_commits", 2),
                             ("total_commits", None)):
            with self.subTest(field=field):
                d = self.postcommit()
                d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]["body"][field] = value
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    check_authenticated_commit_readback(self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_compare_unavailable_fails_closed(self):
        d = self.postcommit()
        del d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]
        with self.assertRaisesRegex(ValueError, "Authenticated read unavailable"):
            check_authenticated_commit_readback(self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_blob_mismatch_symlink_and_404_rejected(self):
        path = ROOT + "/contents/docs/OPERACAO.md?ref=" + "d" * 40
        for value in (
            {"status": 200, "body": {"type": "file", "sha": "e" * 40}},
            {"status": 200, "body": {"type": "symlink", "sha": "f" * 40}},
            {"status": 404, "body": {"message": "Not Found"}},
        ):
            with self.subTest(value=value):
                d = self.postcommit()
                d[path] = value
                with self.assertRaises(ValueError):
                    check_authenticated_commit_readback(self.p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_create_requires_added_and_live_blob(self):
        p = proposal(operation="create", path="docs/new.md")
        d = self.postcommit()
        diff = d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]["body"]
        diff["files"] = [{"filename": "docs/new.md", "status": "added", "sha": "f" * 40}]
        d[ROOT + "/contents/docs/new.md?ref=" + "d" * 40] = {
            "status": 200, "body": {"type": "file", "sha": "f" * 40}}
        self.assertEqual(check_authenticated_commit_readback(
            p, "d" * 40, BASE, d.__getitem__)["changed_files_verified"], 1)
        diff["files"][0]["status"] = "modified"
        with self.assertRaisesRegex(ValueError, "Unexpected file"):
            check_authenticated_commit_readback(p, "d" * 40, BASE, d.__getitem__)

    def test_postcommit_diff_cannot_claim_ci_success(self):
        d = self.postcommit()
        d[ROOT + "/compare/" + HEAD + "..." + "d" * 40]["body"]["ci"] = "success"
        result = check_authenticated_commit_readback(
            self.p, "d" * 40, BASE, d.__getitem__)
        self.assertFalse(result["ci_verified"])
        self.assertFalse(result["merge_authorized"])

    @patch("api_write_guard.subprocess.run")
    def test_gh_reader_accepts_http_200_json(self, run):
        run.return_value = SimpleNamespace(
            stdout='HTTP/2 200 OK\nheader: x\n\n{"state":"open"}\n',
            returncode=0)
        self.assertEqual(github_get_live(ROOT + "/pulls/12")["status"], 200)

    @patch("api_write_guard.subprocess.run")
    def test_gh_reader_accepts_verified_404_json(self, run):
        run.return_value = SimpleNamespace(
            stdout='HTTP/2 404 Not Found\n\n{"message":"Not Found"}\n',
            returncode=1)
        self.assertEqual(github_get_live(ROOT + "/contents/x?ref=" + HEAD)["status"], 404)

    @patch("api_write_guard.subprocess.run")
    def test_gh_reader_rejects_unstructured_response(self, run):
        run.return_value = SimpleNamespace(stdout='{"state":"open"}',
                                           returncode=0)
        with self.assertRaisesRegex(ValueError, "status not found"):
            github_get_live(ROOT + "/pulls/12")

if __name__ == "__main__":
    unittest.main()
