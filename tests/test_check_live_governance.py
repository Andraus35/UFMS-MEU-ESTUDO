"""Negative and positive cases for READ-ONLY Termux live governance snapshot."""
import copy
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from check_live_governance import EvidenceMissing, verify_snapshot, APP_CHECK

PR, HEAD, BASE, MERGE, APP = 10, "a"*40, "b"*40, "c"*40, 87654
NOW = 1700000000
WHEN = datetime.fromtimestamp(NOW-5, timezone.utc).isoformat()


def fixture():
    prefix = "repos/Andraus35/UFMS-MEU-ESTUDO"
    return {
        f"{prefix}/pulls/{PR}": {"number": PR, "state": "open",
            "head": {"sha": HEAD}, "base": {"ref": "main", "sha": BASE},
            "merge_commit_sha": MERGE},
        f"{prefix}/branches/main": {"protected": True, "commit": {"sha": BASE}},
        f"{prefix}/branches/main/protection": {
            "enforce_admins": {"enabled": True},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
            "required_pull_request_reviews": {
                "required_approving_review_count": 1, "dismiss_stale_reviews": True},
            "required_status_checks": {"strict": True, "checks": [
                {"context": "validate", "app_id": 15368},
                {"context": APP_CHECK, "app_id": APP},
            ]}},
        f"{prefix}/git/ref/pull/{PR}/merge": {
            "ref": f"refs/pull/{PR}/merge", "object": {"sha": MERGE}},
        f"{prefix}/commits/{MERGE}": {
            "sha": MERGE, "parents": [{"sha": BASE}, {"sha": HEAD}]},
        f"{prefix}/commits/{MERGE}/check-runs?per_page=100": {
            "total_count": 2, "check_runs": [
                {"id": 1, "name": "validate", "app": {"id": 15368},
                 "head_sha": MERGE, "status": "completed",
                 "conclusion": "success", "completed_at": WHEN},
                {"id": 2, "name": APP_CHECK, "app": {"id": APP},
                 "head_sha": MERGE, "status": "completed",
                 "conclusion": "success", "completed_at": WHEN,
                 "external_id": f"pr{PR}:{HEAD}:{BASE}:{MERGE}"},
            ]},
    }


class LiveEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.values = fixture()
        self.prefix = "repos/Andraus35/UFMS-MEU-ESTUDO"

    def run_probe(self):
        return verify_snapshot(PR, HEAD, BASE, APP,
                               get=lambda p: copy.deepcopy(self.values[p]), now=NOW)

    def must_fail(self, fragment):
        with self.assertRaisesRegex(EvidenceMissing, fragment):
            self.run_probe()

    def test_reference_snapshot_requires_two_proper_checks(self):
        data = self.run_probe()
        self.assertEqual(data["snapshot"], "PASS_AT_INSTANT_ONLY")
        self.assertFalse(data["merge_authorized"])
        self.assertEqual(len(data["checks"]), 2)

    def test_app_not_required_rejected(self):
        self.values[f"{self.prefix}/branches/main/protection"]["required_status_checks"]["checks"].pop()
        self.must_fail("required checks")

    def test_spoofed_check_wrong_app_denied(self):
        check = self.values[f"{self.prefix}/commits/{MERGE}/check-runs?per_page=100"]["check_runs"][1]
        check["app"]["id"] = 15368
        self.must_fail("source ambiguous")

    def test_validate_older_than_ten_minutes_still_valid(self):
        path = f"{self.prefix}/commits/{MERGE}/check-runs?per_page=100"
        self.values[path]["check_runs"][0]["completed_at"] = datetime.fromtimestamp(
            NOW - 1800, timezone.utc).isoformat()
        self.assertEqual(self.run_probe()["snapshot"], "PASS_AT_INSTANT_ONLY")

    def test_validate_older_than_seven_days_rejected(self):
        path = f"{self.prefix}/commits/{MERGE}/check-runs?per_page=100"
        self.values[path]["check_runs"][0]["completed_at"] = datetime.fromtimestamp(
            NOW - 7*86400 - 1, timezone.utc).isoformat()
        self.must_fail("freshness")

    def test_old_success_denied_as_snapshot(self):
        check = self.values[f"{self.prefix}/commits/{MERGE}/check-runs?per_page=100"]["check_runs"][1]
        check["completed_at"] = datetime.fromtimestamp(
            NOW-601, timezone.utc).isoformat()
        self.must_fail("freshness")

    def test_app_check_external_id_from_other_pr_denied(self):
        check = self.values[f"{self.prefix}/commits/{MERGE}/check-runs?per_page=100"]["check_runs"][1]
        check["external_id"] = f"pr11:{HEAD}:{BASE}:{MERGE}"
        self.must_fail("PR identity mismatch")

    def test_fail_when_app_last_check_failed(self):
        self.values[f"{self.prefix}/commits/{MERGE}/check-runs?per_page=100"]["check_runs"][1]["conclusion"] = "failure"
        self.must_fail("not successful")

    def test_missing_admin_enforcement_denied(self):
        self.values[f"{self.prefix}/branches/main/protection"]["enforce_admins"]["enabled"] = False
        self.must_fail("Administrator")

    def test_missing_independent_reviews_denied(self):
        self.values[f"{self.prefix}/branches/main/protection"]["required_pull_request_reviews"] = None
        self.must_fail("Independent review")

    def test_stale_approvals_not_dismissed_denied(self):
        self.values[f"{self.prefix}/branches/main/protection"]["required_pull_request_reviews"]["dismiss_stale_reviews"] = False
        self.must_fail("stale dismissal")

    def test_merge_parent_order_mutant_denied(self):
        self.values[f"{self.prefix}/commits/{MERGE}"]["parents"].reverse()
        self.must_fail("merge parents")

    def test_partial_check_run_list_denied(self):
        self.values[f"{self.prefix}/commits/{MERGE}/check-runs?per_page=100"]["total_count"] = 200
        self.must_fail("Incomplete")

    def test_protected_main_sha_changed_denied(self):
        self.values[f"{self.prefix}/branches/main"]["commit"]["sha"] = "0"*40
        self.must_fail("Main unprotected or moved")

    def test_no_force_pushes_or_deletion(self):
        obj = self.values[f"{self.prefix}/branches/main/protection"]
        for field in ("allow_force_pushes", "allow_deletions"):
            obj[field]["enabled"] = True
            with self.subTest(field=field):
                self.must_fail("Force push")
            obj[field]["enabled"] = False

    def test_malformed_expected_app_id_rejected(self):
        with self.assertRaisesRegex(EvidenceMissing, "distinct"):
            verify_snapshot(PR, HEAD, BASE, 15368,
                            get=lambda p: copy.deepcopy(self.values[p]), now=NOW)

    def test_unknown_admin_api_403_denied(self):
        def get(path):
            if path.endswith("/protection"):
                raise EvidenceMissing("GitHub API denied or unavailable")
            return copy.deepcopy(self.values[path])
        with self.assertRaisesRegex(EvidenceMissing, "denied"):
            verify_snapshot(PR, HEAD, BASE, APP, get=get, now=NOW)


if __name__ == "__main__":
    unittest.main()
