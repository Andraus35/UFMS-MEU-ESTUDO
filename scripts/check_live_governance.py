"""Read-only, fail-closed GitHub protection snapshot for an INSTALLED GitHub App.

This is evidence collection, NOT a merge authorization. A green check can
remain valid at GitHub after the publisher goes offline. Only an independent
deployment/branch-protection test can address that operational risk.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time

REPO = "Andraus35/UFMS-MEU-ESTUDO"
APP_CHECK = "ufms-governance/app-verified"
ACTION_APP_ID = 15368
SHA = re.compile(r"^[a-f0-9]{40}$")


class EvidenceMissing(Exception):
    pass


def require(ok, reason):
    if not ok:
        raise EvidenceMissing(reason)


def github_get(path):
    try:
        response = subprocess.run(["gh", "api", path], capture_output=True,
                                  text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EvidenceMissing("gh CLI unavailable") from exc
    if response.returncode:
        raise EvidenceMissing("GitHub API denied or unavailable: " + path)
    try:
        return json.loads(response.stdout)
    except ValueError as exc:
        raise EvidenceMissing("GitHub returned malformed JSON") from exc


def status_fresh(run, now, max_age_seconds=600):
    stamp = run.get("completed_at")
    if not isinstance(stamp, str):
        return False
    try:
        when = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if when.tzinfo is None:
            return False
        seconds = now - when.timestamp()
        return 0 <= seconds <= max_age_seconds
    except (ValueError, OverflowError, TypeError):
        return False


def complete_check_runs(get, path, max_pages=100):
    """Fetch a complete bounded check history, refusing pagination anomalies."""
    all_runs, seen_ids, expected = [], set(), None
    for page in range(1, max_pages + 1):
        url = path if page == 1 else f"{path}&page={page}"
        try:
            response = get(url)
        except Exception as exc:
            raise EvidenceMissing("Incomplete check-run listing: page unavailable") from exc
        if not isinstance(response, dict):
            raise EvidenceMissing("Incomplete check-run listing: malformed page")
        count = response.get("total_count")
        batch = response.get("check_runs")
        if (type(count) is not int or count < 0 or
                not isinstance(batch, list) or len(batch) > 100):
            raise EvidenceMissing("Incomplete check-run listing: invalid count/page")
        if expected is None:
            expected = count
        if count != expected:
            raise EvidenceMissing("Incomplete check-run listing: count changed")
        for item in batch:
            if (not isinstance(item, dict) or
                    type(item.get("id")) is not int or item["id"] in seen_ids):
                raise EvidenceMissing("Incomplete check-run listing: duplicate/invalid ID")
            seen_ids.add(item["id"])
        all_runs.extend(batch)
        if len(all_runs) == expected:
            return all_runs
        if len(all_runs) > expected or len(batch) != 100:
            raise EvidenceMissing("Incomplete check-run listing: short/inconsistent page")
    raise EvidenceMissing("Incomplete check-run listing: page limit exceeded")


def assert_check(runs, name, appid, merge_sha, external_id, now, max_age_seconds=600):
    matched = [c for c in runs if isinstance(c, dict) and c.get("name") == name]
    require(matched, "Check absent on test merge: " + name)
    require(all(c.get("app", {}).get("id") == appid for c in matched),
            "Check source ambiguous or not the expected App: " + name)
    latest = sorted(matched, key=lambda r: r.get("id", 0), reverse=True)[0]
    require(latest.get("head_sha") == merge_sha, "Check attached to wrong SHA")
    require(latest.get("status") == "completed" and latest.get("conclusion") == "success",
            "Latest required check is not successful: " + name)
    require(status_fresh(latest, now, max_age_seconds), "Check timestamp exceeds snapshot freshness window")
    if external_id is not None:
        require(latest.get("external_id") == external_id, "PR identity mismatch in App check")
    return {"name": name, "app_id": appid, "check_id": latest.get("id"),
            "completed_at": latest.get("completed_at")}


def verify_snapshot(number, expected_head, expected_base, app_id, get=github_get, now=None):
    require(type(number) is int and number > 0, "Invalid PR number")
    require(type(app_id) is int and app_id > 0 and app_id != ACTION_APP_ID,
            "External App ID must be distinct from GitHub Actions")
    for title, sha in (("HEAD", expected_head), ("base", expected_base)):
        require(isinstance(sha, str) and SHA.fullmatch(sha), "Invalid expected " + title)
    now = time.time() if now is None else now
    prefix = f"repos/{REPO}"
    pr_path = f"{prefix}/pulls/{number}"
    pr = get(pr_path)
    require(isinstance(pr, dict) and pr.get("number") == number and pr.get("state") == "open",
            "PR identity or open state mismatch")
    head = pr.get("head", {}).get("sha")
    base = pr.get("base", {}).get("sha")
    merge = pr.get("merge_commit_sha")
    require(head == expected_head and base == expected_base
            and pr.get("base", {}).get("ref") == "main",
            "PR HEAD/base mismatch")
    require(isinstance(merge, str) and SHA.fullmatch(merge), "No test merge SHA")
    branch = get(f"{prefix}/branches/main")
    require(branch.get("protected") is True
            and branch.get("commit", {}).get("sha") == base,
            "Main unprotected or moved")
    protection = get(f"{prefix}/branches/main/protection")
    require(protection.get("enforce_admins", {}).get("enabled") is True,
            "Administrator enforcement not proven")
    require(protection.get("allow_force_pushes", {}).get("enabled") is False
            and protection.get("allow_deletions", {}).get("enabled") is False,
            "Force push / deletion not blocked")
    reviews = protection.get("required_pull_request_reviews")
    require(isinstance(reviews, dict)
            and reviews.get("required_approving_review_count", 0) >= 1
            and reviews.get("dismiss_stale_reviews") is True,
            "Independent review / stale dismissal not enforced")
    required = protection.get("required_status_checks")
    require(isinstance(required, dict) and required.get("strict") is True,
            "Strict required status checks not proven")
    checks = required.get("checks", [])
    must = {("validate", ACTION_APP_ID), (APP_CHECK, app_id)}
    require(isinstance(checks, list)
            and must.issubset({(c.get("context"), c.get("app_id")) for c in checks}),
            "App-bound required checks missing")
    ref = get(f"{prefix}/git/ref/pull/{number}/merge")
    require(ref.get("ref") == f"refs/pull/{number}/merge"
            and ref.get("object", {}).get("sha") == merge,
            "Synthetic merge ref mismatch")
    commit = get(f"{prefix}/commits/{merge}")
    require(commit.get("sha") == merge
            and [p.get("sha") for p in commit.get("parents", [])] == [base, head],
            "Synthetic merge parents mismatch")
    runs = complete_check_runs(get, f"{prefix}/commits/{merge}/check-runs?per_page=100")
    external_id = f"pr{number}:{head}:{base}:{merge}"
    checked = [
        assert_check(runs, "validate", ACTION_APP_ID, merge, None, now, 7 * 24 * 3600),
        assert_check(runs, APP_CHECK, app_id, merge, external_id, now),
    ]
    pr2, branch2 = get(pr_path), get(f"{prefix}/branches/main")
    require(pr2.get("head", {}).get("sha") == head
            and pr2.get("base", {}).get("sha") == base
            and pr2.get("merge_commit_sha") == merge
            and branch2.get("commit", {}).get("sha") == base,
            "PR/base moved during evidence collection")
    # Check freshness here is evidence, NOT the native GitHub merge decision.
    # The required checks must also be present on GitHub's selected SHA.
    return {"snapshot": "PASS_AT_INSTANT_ONLY", "pr": number, "head": head,
            "base": base, "merge": merge, "checks": checked,
            "merge_authorized": False,
            "offline_stale_green_risk": "OPEN_NOT_ENFORCED_BY_GITHUB"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--app-id", type=int, required=True)
    args = parser.parse_args()
    try:
        result = verify_snapshot(args.pr, args.head, args.base, args.app_id)
    except (EvidenceMissing, TypeError, ValueError, KeyError, AttributeError) as exc:
        print("BLOCKED (no homologation): " + str(exc), file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("NOTE: snapshot is NOT merge permission or an offline fail-closed guarantee.",
          file=sys.stderr)


if __name__ == "__main__":
    main()
