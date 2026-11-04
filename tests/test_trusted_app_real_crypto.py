"""Full policy-to-App flow with REAL OpenSSL Ed25519 signatures.

Only GitHub REST transport is simulated. No monkeypatch of verify_signature(),
evaluate() or trusted_governance.enforce(). Production verify_one() executes.
Not an installed GitHub App or real GitHub branch-protection acceptance test.
"""
import base64
import copy
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import trusted_governance as policy
import trusted_app_check as app

PR, BASE, HEAD, MERGE = 9, "b"*40, "a"*40, "c"*40
APP_ID = "456789"


class SignedGithubFixture:
    def __init__(self):
        self.files = [{"filename": "ROADMAP.md", "status": "modified"}]
        self.comments = []
        self.checks = []
        self.writes = []
        self.prs = {
            9: self.pr(9, HEAD, MERGE),
        }
        self.main = BASE
        self.merge_parents = [BASE, HEAD]
        self.fail = None
        self.invalid_app_id = None

    @staticmethod
    def pr(number, head, merge):
        return {"number": number, "state": "open",
                "head": {"sha": head}, "base": {"ref": "main", "sha": BASE},
                "merge_commit_sha": merge}

    def gh_app(self, method, path, token, payload=None):
        if token != "install-token" or not path.startswith("repos/"+policy.REPOSITORY+"/"):
            raise AssertionError("Unexpected GitHub App request")
        if path == self.fail:
            raise ValueError("Simulated provider failure")
        tail = path[len("repos/"+policy.REPOSITORY+"/"):]
        if method == "POST":
            if tail != "check-runs":
                raise AssertionError("Unexpected write")
            self.writes.append(copy.deepcopy(payload))
            result = {
                **copy.deepcopy(payload), "id": 1000+len(self.writes),
                "app": {"id": self.invalid_app_id or int(APP_ID)},
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            self.checks.append(result)
            return result
        if method != "GET":
            raise AssertionError("Unexpected method")
        if tail == "pulls?state=open&per_page=100&page=1":
            return [{"number": n} for n in self.prs]
        if tail.startswith("pulls/") and "/" not in tail[6:]:
            return copy.deepcopy(self.prs[int(tail[6:])])
        if tail == "git/ref/pull/9/merge":
            return {"ref": "refs/pull/9/merge", "object": {"sha": MERGE}}
        if tail == f"commits/{MERGE}":
            return {"sha": MERGE, "parents": [{"sha": p} for p in self.merge_parents]}
        if tail == f"commits/{MERGE}/check-runs?per_page=100":
            return {"total_count": len(self.checks),
                    "check_runs": copy.deepcopy(self.checks)}
        raise AssertionError("Unexpected App request " + tail)

    def gh_policy(self, path, token):
        if token != "install-token":
            raise AssertionError("Unexpected policy token")
        if path == f"repos/{policy.REPOSITORY}/pulls/{PR}":
            return {**copy.deepcopy(self.prs[PR]), "changed_files": len(self.files)}
        if path == f"repos/{policy.REPOSITORY}/branches/main":
            return {"protected": True, "commit": {"sha": self.main}}
        raise AssertionError("Unexpected policy request " + path)

    def gh_collection(self, path, token, max_pages=10):
        if path.endswith("/files"):
            return copy.deepcopy(self.files)
        if path.endswith("/comments"):
            return copy.deepcopy(self.comments)
        raise AssertionError("Unexpected collection")

    def execute(self):
        with mock.patch.object(app, "api_json", side_effect=self.gh_app), \
             mock.patch.object(policy, "get_json", side_effect=self.gh_policy), \
             mock.patch.object(policy, "get_collection", side_effect=self.gh_collection):
            return app.verify_one(PR, "install-token", APP_ID, self.public_key)

    @property
    def public_key(self):
        return self._public_key

    @public_key.setter
    def public_key(self, value):
        self._public_key = value


class RealSignatureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ufms-crypto-")
        folder = Path(cls.temp.name)
        cls.private = folder / "private.pem"
        cls.public = folder / "public.pem"
        cls.other_private = folder / "impostor.pem"
        for path in (cls.private, cls.other_private):
            subprocess.run(["openssl", "genpkey", "-algorithm", "Ed25519",
                            "-out", str(path)], check=True, capture_output=True)
        subprocess.run(["openssl", "pkey", "-in", str(cls.private), "-pubout",
                        "-out", str(cls.public)], check=True, capture_output=True)
        cls.pubkey = base64.b64encode(cls.public.read_bytes()).decode("ascii")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.gh = SignedGithubFixture()
        self.gh.public_key = self.pubkey

    def signed_comment(self, number=PR, head=HEAD, base=BASE,
                       signer=None, login=None, owner_id=None):
        message = policy.approval_text(number, head, base)
        with tempfile.TemporaryDirectory(prefix="ufms-sign-") as folder:
            msg = Path(folder)/"message"
            sig = Path(folder)/"signature"
            msg.write_bytes(message.encode("utf-8"))
            subprocess.run(
                ["openssl", "pkeyutl", "-sign", "-rawin",
                 "-inkey", str(signer or self.private), "-in", str(msg),
                 "-out", str(sig)],
                check=True, capture_output=True, timeout=10)
            body = policy.signature_comment(message, sig.read_bytes())
        return {"body": body,
                "user": {"login": login or policy.OWNER_LOGIN,
                         "id": owner_id if owner_id is not None else policy.OWNER_ID,
                         "type": "User"}}

    def test_real_ed25519_signature_passes_full_policy_and_app(self):
        self.gh.comments = [self.signed_comment()]
        result = self.gh.execute()
        self.assertEqual(result["conclusion"], "success")
        self.assertEqual(result["merge_sha"], MERGE)
        self.assertEqual(self.gh.writes[-1]["head_sha"], MERGE)
        self.assertEqual(self.gh.checks[-1]["app"]["id"], int(APP_ID))

    def test_no_signature_fails_closed_on_real_policy(self):
        result = self.gh.execute()
        self.assertEqual(result["conclusion"], "failure")

    def test_forged_signature_with_different_private_key_denied(self):
        self.gh.comments = [self.signed_comment(signer=self.other_private)]
        self.assertEqual(self.gh.execute()["conclusion"], "failure")

    def test_tampered_signature_denied_by_openssl(self):
        fake = self.signed_comment()
        prefix, signature = fake["body"].rsplit(" SIG=", 1)
        raw = bytearray(base64.b64decode(signature))
        raw[0] ^= 1
        fake["body"] = prefix + " SIG=" + base64.b64encode(raw).decode("ascii")
        self.gh.comments = [fake]
        self.assertEqual(self.gh.execute()["conclusion"], "failure")

    def test_real_signatures_for_other_pr_head_base_all_fail(self):
        variants = [
            self.signed_comment(number=PR+1),
            self.signed_comment(head="0"*40),
            self.signed_comment(base="1"*40),
        ]
        for comment in variants:
            with self.subTest(body=comment["body"][:90]):
                self.gh.comments = [comment]
                self.assertEqual(self.gh.execute()["conclusion"], "failure")

    def test_real_signature_reposted_by_wrong_account_denied(self):
        for invalid in (self.signed_comment(login="attacker"),
                        self.signed_comment(owner_id=1)):
            self.gh.comments = [invalid]
            self.assertEqual(self.gh.execute()["conclusion"], "failure")

    def test_signed_change_to_locked_guardian_still_denied(self):
        self.gh.comments = [self.signed_comment()]
        self.gh.files = [{"filename": "scripts/trusted_app_check.py",
                          "status": "modified"}]
        self.assertEqual(self.gh.execute()["conclusion"], "failure")

    def test_revoked_comment_becomes_failure_when_app_is_online(self):
        self.gh.comments = [self.signed_comment()]
        self.assertEqual(self.gh.execute()["conclusion"], "success")
        self.gh.comments = []
        self.assertEqual(self.gh.execute()["conclusion"], "failure")
        self.assertEqual([c["conclusion"] for c in self.gh.writes],
                         ["success", "failure"])

    def test_both_github_checks_same_name_wrong_app_not_reused(self):
        self.gh.checks.append({
            "id": 77, "name": app.CHECK_NAME, "head_sha": MERGE,
            "status": "completed", "conclusion": "success",
            "external_id": f"pr{PR}:{HEAD}:{BASE}:{MERGE}",
            "app": {"id": 15368},
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })
        self.gh.comments = [self.signed_comment()]
        result = self.gh.execute()
        self.assertNotIn("reused_verified_check", result)
        self.assertEqual(self.gh.checks[-1]["app"]["id"], int(APP_ID))

    def test_offline_after_real_signed_success_preserves_stale_check_risk(self):
        self.gh.comments = [self.signed_comment()]
        self.assertEqual(self.gh.execute()["conclusion"], "success")
        self.gh.comments = []  # revocation while App is now OFFLINE
        # No execution means no failure check. This is a known limitation,
        # not a protection that can be verified by local unit tests.
        self.assertEqual(self.gh.checks[-1]["conclusion"], "success")
        self.assertEqual(len(self.gh.writes), 1)

    def test_main_sha_mutation_fails_closed(self):
        self.gh.comments = [self.signed_comment()]
        self.gh.main = "0"*40
        self.assertEqual(self.gh.execute()["conclusion"], "failure")

    def test_missing_public_key_fails_closed_despite_valid_comment(self):
        self.gh.comments = [self.signed_comment()]
        self.gh.public_key = ""
        self.assertEqual(self.gh.execute()["conclusion"], "failure")


if __name__ == "__main__":
    unittest.main()
