"""Mutation-oriented adversarial contract tests for GitHub App verification.

All scenarios exercise the PRODUCTION verify_one()/merge_target()/reuse policy
against a deterministic fake GitHub REST backend. Nothing is written to GitHub.
An offline unittest cannot prove server-side branch protection enforcement.
"""
import copy
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from trusted_app_check import CHECK_NAME, verify_one, merge_target, refuse_shared_head
from trusted_governance import REPOSITORY

APP_ID = "456789"
BASE = "b" * 40
HEAD_A = "a" * 40
HEAD_B = "f" * 40
MERGE_A = "c" * 40
MERGE_B = "d" * 40


class FakeGitHub:
    def __init__(self):
        self.prs = {
            9: self.pr(9, HEAD_A, MERGE_A),
            10: self.pr(10, HEAD_B, MERGE_B),
        }
        self.refs = {9: MERGE_A, 10: MERGE_B}
        self.parents = {MERGE_A: [BASE, HEAD_A], MERGE_B: [BASE, HEAD_B]}
        self.checks = {MERGE_A: [], MERGE_B: []}
        self.published = []
        self.policy_denied = set()
        self.fail_on = set()
        self.after_first_pr_read = None
        self.reads = {}

    @staticmethod
    def pr(number, head, merge):
        return {
            "number": number, "state": "open",
            "head": {"sha": head}, "base": {"ref": "main", "sha": BASE},
            "merge_commit_sha": merge,
        }

    def api(self, method, path, token, payload=None):
        if token != "installation":
            raise AssertionError("Wrong installation token")
        if not path.startswith("repos/" + REPOSITORY + "/"):
            raise AssertionError("Unexpected endpoint " + path)
        if path in self.fail_on:
            raise ValueError("Simulated API outage")
        if method == "POST":
            if path != f"repos/{REPOSITORY}/check-runs":
                raise AssertionError("Unexpected write")
            self.published.append(copy.deepcopy(payload))
            check = {
                **copy.deepcopy(payload), "id": 100 + len(self.published),
                "app": {"id": int(APP_ID)},
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            self.checks.setdefault(payload["head_sha"], []).append(check)
            return check
        if method != "GET":
            raise AssertionError("Unknown API method")
        endpoint = path.split(f"repos/{REPOSITORY}/", 1)[1]
        if endpoint.startswith("pulls?"):
            return [{"number": n} for n, pr in sorted(self.prs.items())
                    if pr["state"] == "open"]
        if endpoint.startswith("pulls/") and endpoint.count("/") == 1:
            number = int(endpoint.split("/")[-1])
            self.reads[number] = self.reads.get(number, 0) + 1
            obj = copy.deepcopy(self.prs[number])
            if (self.after_first_pr_read is not None and number == 9
                    and self.reads[number] == 1):
                self.after_first_pr_read(self)
            return obj
        if endpoint.startswith("git/ref/pull/"):
            number = int(endpoint.split("/")[-2])
            return {"ref": f"refs/pull/{number}/merge",
                    "object": {"sha": self.refs[number]}}
        if endpoint.startswith("commits/") and endpoint.endswith("/check-runs?per_page=100"):
            sha = endpoint.split("/")[1]
            return {"check_runs": copy.deepcopy(self.checks.get(sha, []))}
        if endpoint.startswith("commits/"):
            sha = endpoint.split("/")[-1]
            return {"sha": sha, "parents": [{"sha": p} for p in self.parents[sha]]}
        raise AssertionError("Unmodelled GitHub endpoint " + path)

    def run(self, number=9, deny=None):
        if deny is None:
            deny = number in self.policy_denied
        def policy(env):
            if deny:
                raise ValueError("Rejected by trusted-base policy")
            if int(env["PR_NUMBER"]) != number:
                raise AssertionError("Wrong PR checked")
            if env["PR_HEAD_SHA"] != self.prs[number]["head"]["sha"]:
                raise ValueError("HEAD mutated during evaluation")
        with mock.patch("trusted_app_check.api_json", side_effect=self.api):
            with mock.patch("trusted_app_check.enforce", side_effect=policy):
                return verify_one(number, "installation", APP_ID, "public-key")


class AdversarialGitHubAppTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeGitHub()

    def test_two_distinct_prs_never_share_check_target(self):
        a = self.fake.run(9)
        b = self.fake.run(10)
        self.assertEqual((a["merge_sha"], b["merge_sha"]), (MERGE_A, MERGE_B))
        self.assertEqual({x["head_sha"] for x in self.fake.published},
                         {MERGE_A, MERGE_B})
        self.assertNotIn(HEAD_A, self.fake.checks)
        self.assertNotIn(HEAD_B, self.fake.checks)

    def test_two_prs_same_head_both_rejected_even_if_only_one_was_signed(self):
        self.fake.prs[10]["head"]["sha"] = HEAD_A
        self.fake.parents[MERGE_B] = [BASE, HEAD_A]
        for number in (9, 10):
            with self.subTest(pr=number):
                result = self.fake.run(number, deny=(number == 10))
                self.assertEqual(result["conclusion"], "failure")
                self.assertEqual(self.fake.published[-1]["conclusion"], "failure")

    def test_valid_one_and_invalid_another_get_distinct_results(self):
        self.fake.policy_denied.add(10)
        self.assertEqual(self.fake.run(9)["conclusion"], "success")
        self.assertEqual(self.fake.run(10)["conclusion"], "failure")
        self.assertEqual(self.fake.checks[MERGE_A][-1]["conclusion"], "success")
        self.assertEqual(self.fake.checks[MERGE_B][-1]["conclusion"], "failure")

    def test_revocation_after_green_while_app_is_running_publishes_failure(self):
        self.assertEqual(self.fake.run(9)["conclusion"], "success")
        self.fake.policy_denied.add(9)
        self.assertEqual(self.fake.run(9)["conclusion"], "failure")
        self.assertEqual([c["conclusion"] for c in self.fake.checks[MERGE_A]],
                         ["success", "failure"])

    def test_app_offline_does_not_revoke_old_success_known_limitation(self):
        self.fake.run(9)
        check_before = copy.deepcopy(self.fake.checks[MERGE_A])
        # No new call: local refresh TTL is NOT enforced by GitHub.
        self.assertEqual(self.fake.checks[MERGE_A], check_before)
        self.assertEqual(self.fake.checks[MERGE_A][-1]["conclusion"], "success")
        # This test documents a KNOWN P0 residual risk, not approval of it.

    def test_same_named_check_from_actions_is_not_reused_as_app_check(self):
        self.fake.checks[MERGE_A].append({
            "id": 50, "name": CHECK_NAME, "head_sha": MERGE_A,
            "status": "completed", "conclusion": "success",
            "app": {"id": 15368}, "external_id": f"pr9:{HEAD_A}:{BASE}:{MERGE_A}",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })
        result = self.fake.run(9)
        self.assertNotIn("reused_verified_check", result)
        self.assertEqual(len(self.fake.published), 1)
        self.assertEqual(self.fake.checks[MERGE_A][-1]["app"]["id"], int(APP_ID))

    def test_success_check_cannot_be_reused_after_policy_revocation(self):
        self.fake.run(9)
        self.fake.policy_denied.add(9)
        result = self.fake.run(9)
        self.assertEqual(result["conclusion"], "failure")
        self.assertNotIn("reused_verified_check", result)

    def test_merge_ref_mismatch_fails_closed_before_success(self):
        self.fake.refs[9] = "0" * 40
        with self.assertRaisesRegex(ValueError, "test merge ref"):
            self.fake.run(9)
        self.assertEqual(self.fake.published, [])

    def test_wrong_merge_parent_order_or_extra_parent_fails(self):
        for parents in ([HEAD_A, BASE], [BASE, HEAD_A, "0"*40],
                        ["0"*40, HEAD_A]):
            with self.subTest(parents=parents):
                self.fake.parents[MERGE_A] = parents
                with self.assertRaisesRegex(ValueError, "merge parents"):
                    self.fake.run(9)
                self.assertEqual(self.fake.published, [])

    def test_main_base_changes_after_first_read_does_not_emit_success(self):
        def race(fake):
            fake.prs[9]["base"]["sha"] = "0" * 40
        self.fake.after_first_pr_read = race
        result = self.fake.run(9)
        self.assertEqual(result["conclusion"], "failure")
        self.assertEqual(self.fake.published[-1]["conclusion"], "failure")

    def test_pr_head_changes_after_first_read_does_not_emit_success(self):
        def race(fake):
            fake.prs[9]["head"]["sha"] = "0" * 40
        self.fake.after_first_pr_read = race
        result = self.fake.run(9)
        self.assertEqual(result["conclusion"], "failure")

    def test_new_pr_with_shared_head_between_reads_denies_success(self):
        def race(fake):
            fake.prs[10]["head"]["sha"] = HEAD_A
        self.fake.after_first_pr_read = race
        # First check of the other open PR discovers the duplicate.
        result = self.fake.run(9)
        self.assertEqual(result["conclusion"], "failure")

    def test_pr_listing_api_error_fails_closed(self):
        self.fake.fail_on.add(
            f"repos/{REPOSITORY}/pulls?state=open&per_page=100&page=1")
        result = self.fake.run(9)
        self.assertEqual(result["conclusion"], "failure")

    def test_second_merge_ref_mismatch_denies_success(self):
        # First lookup of PR metadata occurs before the revocation.
        counter = {"calls": 0}
        original = self.fake.api
        def altered(method, path, token, payload=None):
            if path.endswith("/git/ref/pull/9/merge"):
                counter["calls"] += 1
                if counter["calls"] == 2:
                    return {"ref": "refs/pull/9/merge", "object": {"sha": "0"*40}}
            return original(method, path, token, payload)
        with mock.patch("trusted_app_check.api_json", side_effect=altered):
            with mock.patch("trusted_app_check.enforce", return_value=None):
                result = verify_one(9, "installation", APP_ID, "pubkey")
        self.assertEqual(result["conclusion"], "failure")
        self.assertEqual(self.fake.published[-1]["conclusion"], "failure")

    def full_stack(self, records, comments=(), allow_signature=False):
        """Actual enforce() + verify_one(); only GitHub I/O and crypto isolated."""
        import trusted_governance
        from trusted_governance import approval_text
        from trusted_app_check import verify_one
        repo = REPOSITORY
        pr = self.fake.prs[9]
        author = {"id": trusted_governance.OWNER_ID,
                  "login": trusted_governance.OWNER_LOGIN, "type": "User"}
        attestation = approval_text(9, HEAD_A, BASE) + " SIG=" + "YQ=="
        normalized = []
        for item in comments:
            normalized.append({"body": attestation if item == "valid" else item,
                               "user": copy.deepcopy(author)})
        def get_json(path, token):
            if path == f"repos/{repo}/pulls/9":
                return {**copy.deepcopy(pr), "changed_files": len(records)}
            if path == f"repos/{repo}/branches/main":
                return {"protected": True, "commit": {"sha": BASE}}
            raise AssertionError("Unexpected governance REST path: " + path)
        def get_collection(path, token, max_pages=10):
            if path.endswith("/files"):
                return copy.deepcopy(records)
            if path.endswith("/comments"):
                return copy.deepcopy(normalized)
            raise AssertionError("Unexpected governance collection " + path)
        with mock.patch("trusted_app_check.api_json", side_effect=self.fake.api):
            with mock.patch("trusted_governance.get_json", side_effect=get_json):
                with mock.patch("trusted_governance.get_collection",
                                side_effect=get_collection):
                    with mock.patch("trusted_governance.verify_signature",
                                    return_value=allow_signature):
                        return verify_one(9, "installation", APP_ID, "public-key")

    def test_full_stack_governance_without_signature_denied(self):
        result = self.full_stack([
            {"filename": "ROADMAP.md", "status": "modified"}])
        self.assertEqual(result["conclusion"], "failure")
        self.assertEqual(self.fake.published[-1]["head_sha"], MERGE_A)

    def test_full_stack_valid_signature_on_same_snapshot_passes(self):
        result = self.full_stack([
            {"filename": "ROADMAP.md", "status": "modified"}],
            comments=["valid"], allow_signature=True)
        self.assertEqual(result["conclusion"], "success")
        self.assertEqual(self.fake.published[-1]["app"]["id"], int(APP_ID))

    def test_full_stack_lockfile_rename_denied_even_if_signed(self):
        result = self.full_stack([
            {"filename": "templates/inactive.py", "status": "renamed",
             "previous_filename": "scripts/trusted_governance.py"}],
            comments=["valid"], allow_signature=True)
        self.assertEqual(result["conclusion"], "failure")

    def test_full_stack_duplicate_files_rejected(self):
        rec = {"filename": "templates/x.md", "status": "modified"}
        result = self.full_stack([rec, rec])
        self.assertEqual(result["conclusion"], "failure")

    def test_full_stack_revocation_after_green_publishes_failure(self):
        record = {"filename": "ROADMAP.md", "status": "modified"}
        approved = self.full_stack([record], comments=["valid"],
                                   allow_signature=True)
        self.assertEqual(approved["conclusion"], "success")
        revoked = self.full_stack([record])
        self.assertEqual(revoked["conclusion"], "failure")
        self.assertEqual([x["conclusion"] for x in self.fake.published],
                         ["success", "failure"])

    def test_app_check_readback_must_identify_own_app_not_actions(self):
        original = self.fake.api
        def altered(method, path, token, payload=None):
            data = original(method, path, token, payload)
            if method == "POST" and path.endswith("/check-runs"):
                data["app"]["id"] = 15368
            return data
        with mock.patch("trusted_app_check.api_json", side_effect=altered):
            with mock.patch("trusted_app_check.enforce", return_value=None):
                with self.assertRaisesRegex(ValueError, "readback identity mismatch"):
                    verify_one(9, "installation", APP_ID, "pubkey")


if __name__ == "__main__":
    unittest.main()
