"""Adversarial offline tests for host-only Git object transaction."""
import base64
import copy
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from api_write_guard import git_blob_sha
from api_write_transaction import _commit_once, github_write_live, PREFIX

HEAD, BASE = "a"*40, "b"*40
BRANCH = "audit/clean-docs-20261105"
NEW, TREE, OLD_TREE = "d"*40, "e"*40, "9"*40
PATH = "docs/OPERACAO.md"
RAW = "Novo conteúdo seguro\n"
FINAL = git_blob_sha(RAW)
ORIGINAL = "c"*40


def proposal():
    return {
        "repository": "Andraus35/UFMS-MEU-ESTUDO",
        "branch": BRANCH, "base_branch": "main", "pr_number": 12,
        "draft": True, "merged": False, "state": "open",
        "expected_head_sha": HEAD, "observed_head_sha": HEAD,
        "files": [{"path": PATH, "operation": "update",
                   "expected_blob_sha": ORIGINAL,
                   "expected_new_blob_sha": FINAL}],
    }


class FakeApi:
    def __init__(self):
        self.data = {
            PREFIX + "/pulls/12": {"status": 200, "body": {
                "number": 12, "state": "open", "draft": True, "merged_at": None,
                "head": {"sha": HEAD, "ref": BRANCH,
                         "repo": {"full_name": "Andraus35/UFMS-MEU-ESTUDO"}},
                "base": {"sha": BASE, "ref": "main",
                         "repo": {"full_name": "Andraus35/UFMS-MEU-ESTUDO"}},
            }},
            PREFIX + "/branches/main":
                {"status": 200, "body": {"commit": {"sha": BASE}}},
            PREFIX + "/branches/" + BRANCH:
                {"status": 200, "body": {"commit": {"sha": HEAD}}},
            PREFIX + "/contents/" + PATH + "?ref=" + HEAD:
                {"status": 200, "body": {"type": "file", "sha": ORIGINAL}},
            PREFIX + "/git/commits/" + HEAD:
                {"status": 200, "body": {"tree": {"sha": OLD_TREE}}},
        }
        self.writes = []
        self.conflict = False
        self.forge_response = False
        self.blob_override = None

    def get(self, path):
        return self.data[path]

    def write(self, method, path, payload):
        self.writes.append((method, path, copy.deepcopy(payload)))
        if method == "POST" and path.endswith("/git/blobs"):
            sha = git_blob_sha(base64.b64decode(payload["content"]))
            return {"status": 201, "body": {
                "sha": self.blob_override or sha,
            }}
        if method == "POST" and path.endswith("/git/trees"):
            return {"status": 201, "body": {"sha": TREE}}
        if method == "POST" and path.endswith("/git/commits"):
            return {"status": 201, "body": {"sha": NEW}}
        if method == "PATCH":
            if self.conflict:
                return {"status": 409, "body": {"message": "Update is not a fast forward"}}
            if not self.forge_response:
                self.data[PREFIX + "/pulls/12"]["body"]["head"]["sha"] = NEW
                self.data[PREFIX + "/branches/" + BRANCH]["body"]["commit"]["sha"] = NEW
                self.data[PREFIX + "/git/commits/" + NEW] = {
                    "status": 200, "body": {"parents": [{"sha": HEAD}]}}
                self.data[PREFIX + "/compare/" + HEAD + "..." + NEW] = {
                    "status": 200, "body": {
                        "status": "ahead", "ahead_by": 1,
                        "behind_by": 0, "total_commits": 1,
                        "files": [{"filename": PATH, "status": "modified", "sha": FINAL}],
                    }}
                self.data[PREFIX + "/contents/" + PATH + "?ref=" + NEW] = {
                    "status": 200, "body": {"type": "file", "sha": FINAL}}
            return {"status": 200, "body": {
                "ref": "refs/heads/" + BRANCH,
                "object": {"sha": NEW},
            }}
        raise AssertionError("Unexpected write: " + path)


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeApi()

    def run_transaction(self, p=None, content=None):
        return _commit_once(
            proposal() if p is None else p,
            {PATH: RAW} if content is None else content,
            "safe test commit", self.api.get, self.api.write,
        )

    def test_happy_path_single_nonforced_ref_update(self):
        result = self.run_transaction()
        self.assertTrue(result["content_bound_to_proposal"])
        self.assertFalse(result["ci_verified"])
        self.assertFalse(result["merge_authorized"])
        patches = [w for w in self.api.writes if w[0] == "PATCH"]
        self.assertEqual(len(patches), 1)
        self.assertEqual(patches[0][2], {"sha": NEW, "force": False})

    def test_bad_content_cannot_stage_any_blob(self):
        with self.assertRaisesRegex(ValueError, "Content bytes differ"):
            self.run_transaction(content={PATH: "conteúdo não aprovado"})
        self.assertEqual(self.api.writes, [])

    def test_unexpected_path_cannot_stage_any_blob(self):
        with self.assertRaisesRegex(ValueError, "Content paths differ"):
            self.run_transaction(content={PATH: RAW, "docs/EXTRA.md": "x"})
        self.assertEqual(self.api.writes, [])

    def test_rejects_server_blob_sha_mismatch(self):
        self.api.blob_override = "f" * 40
        with self.assertRaisesRegex(ValueError, "GitHub blob does not match"):
            self.run_transaction()
        self.assertFalse(any(m == "PATCH" for m, _, _ in self.api.writes))

    def test_conflicting_ref_patch_fails_closed(self):
        self.api.conflict = True
        with self.assertRaisesRegex(ValueError, "Authenticated write failed closed"):
            self.run_transaction()
        self.assertEqual(self.api.writes[-1][2]["force"], False)

    def test_forged_reference_ack_cannot_pass_readback(self):
        self.api.forge_response = True
        with self.assertRaises(ValueError):
            self.run_transaction()

    def test_move_before_patch_does_not_advance_ref(self):
        reads = [0]
        def get(path):
            if path == PREFIX + "/pulls/12":
                reads[0] += 1
                if reads[0] > 1:
                    self.api.data[path]["body"]["head"]["sha"] = "8" * 40
            return self.api.get(path)
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            _commit_once(proposal(), {PATH: RAW}, "msg", get, self.api.write)
        self.assertFalse(any(m == "PATCH" for m, _, _ in self.api.writes))

    def test_invalid_commit_message_rejected_without_reads(self):
        with self.assertRaisesRegex(ValueError, "message invalid"):
            _commit_once(
                proposal(), {PATH: RAW}, "secret\nmessage", self.api.get, self.api.write)
        self.assertEqual(self.api.writes, [])

    def test_host_writer_stays_disabled_by_default(self):
        with patch.dict(os.environ, {"UFMS_ENABLE_GITHUB_WRITE": "0", "GH_TOKEN": "dummy"}):
            with self.assertRaisesRegex(ValueError, "disabled"):
                github_write_live("PATCH", PREFIX + "/git/refs/heads/" + BRANCH,
                                  {"sha": NEW, "force": False})

    @patch("api_write_transaction.subprocess.run")
    def test_live_writer_never_uses_force_and_does_not_leak_token_in_argv(self, runner):
        runner.return_value = SimpleNamespace(
            stdout='HTTP/2 200 OK\n\n{"ref":"refs/heads/'+BRANCH+'","object":{"sha":"'+NEW+'"}}',
            returncode=0)
        env = {"UFMS_ENABLE_GITHUB_WRITE": "1", "GH_TOKEN": "SECRET_DONT_LOG", "GH_HOST": "github.com"}
        with patch.dict(os.environ, env):
            out = github_write_live("PATCH", PREFIX + "/git/refs/heads/" + BRANCH,
                                    {"sha": NEW, "force": False})
            self.assertEqual(out["status"], 200)
            args = runner.call_args.args[0]
            self.assertNotIn("SECRET_DONT_LOG", " ".join(args))
            self.assertIn("--input", args)
            self.assertEqual(json.loads(runner.call_args.kwargs["input"]),
                             {"sha": NEW, "force": False})
            with self.assertRaisesRegex(ValueError, "Non-forced"):
                github_write_live("PATCH", PREFIX + "/git/refs/heads/" + BRANCH,
                                  {"sha": NEW, "force": True})
