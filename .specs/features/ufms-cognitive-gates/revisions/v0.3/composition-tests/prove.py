#!/usr/bin/env python3
"""Read-only proof of PR #5's *synthetic* GitHub merge composition.

Never updates Git refs and never claims C1-C27 functional proof or GQ-D approval.
The PR event base SHA may lag; the GitHub merge parents and live main ref
are checked independently instead of trusting stale metadata.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

REPO = "Andraus35/UFMS-MEU-ESTUDO"
R2_SOURCE_BLOB = "a1482c25e064a1ccc06c4a649a704fbd5bf97cf5"
R2_PLAN_SHA256 = "b1dbe81a4723163bb209af39d3ae4a9637e22a9075de2ebce6d1197275a2ad55"
R2_CHECKS_SHA256 = "57f1b2c49226a1ed9a0f836c99084f42e4b655fcd2300251feb169791e6f5568"
PREFIX = Path(".specs/features/ufms-cognitive-gates/revisions/v0.3")
REQUIRED = (
    "AGENTS.md", "settings.json", "scripts/bootstrap.py", "scripts/validate.py",
    "tests/test_harness.py", "edital/manifest.json", "edital/INDEX.md",
    ".github/workflows/validate.yml",
    str(PREFIX / "approved-r2/plan.md"),
    str(PREFIX / "approved-r2/checks.md"),
    str(PREFIX / "proposals/r2/plan.md"),
)


def verify_parent_chain(parents, main_sha, head_sha):
    if not isinstance(parents, list) or parents != [main_sha, head_sha]:
        raise ValueError("COMPOSITION_PARENT_DRIFT")
    if not all(isinstance(x, str) and len(x) == 40 for x in parents):
        raise ValueError("COMPOSITION_SHA_INVALID")
    return True


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify_paths(root):
    root = Path(root)
    for name in REQUIRED:
        path = root / name
        if path.is_symlink() or not path.is_file() or not path.read_bytes().strip():
            raise ValueError("COMPOSITION_FILE_MISSING: " + name)
    source = (root / PREFIX / "proposals/r2/plan.md").read_bytes()
    plan = (root / PREFIX / "approved-r2/plan.md").read_bytes()
    checks = (root / PREFIX / "approved-r2/checks.md").read_bytes()
    if git_blob(source) != R2_SOURCE_BLOB:
        raise ValueError("APPROVED_SOURCE_DRIFT")
    if hashlib.sha256(plan).hexdigest() != R2_PLAN_SHA256:
        raise ValueError("APPROVED_PLAN_DRIFT")
    if hashlib.sha256(checks).hexdigest() != R2_CHECKS_SHA256:
        raise ValueError("APPROVED_CHECKS_DRIFT")
    return True


def verify_event(event, parents, checked_sha, live_main, root):
    pr = event.get("pull_request") or {}
    if event.get("repository", {}).get("full_name") != REPO:
        raise ValueError("WRONG_REPOSITORY")
    if pr.get("number") != 5 or pr.get("state") != "open":
        raise ValueError("WRONG_PR")
    if pr.get("base", {}).get("ref") != "main":
        raise ValueError("WRONG_BASE_BRANCH")
    head = pr.get("head", {}).get("sha")
    if (not isinstance(checked_sha, str) or len(checked_sha) != 40
            or not isinstance(live_main, str) or len(live_main) != 40):
        raise ValueError("COMPOSITION_SHA_INVALID")
    verify_parent_chain(parents, live_main, head)
    verify_paths(root)
    return {
        "result": "SYNTHETIC_COMPOSITION_VERIFIED",
        "merge_sha": checked_sha,
        "base_main_sha": live_main,
        "pr5_head_sha": head,
        "base_pr5_parent_order": "main_then_pr5",
        "approved_r2_integrity": "PASS",
        "harness_paths_present": True,
        "functional_checks_C1_C27": "NOT_RUN",
        "GQD": "NOT_HOMOLOGATED",
        "production_merge": False,
    }


def cli():
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        raise ValueError("MISSING_GITHUB_EVENT")
    event = json.loads(Path(path).read_text(encoding="utf-8"))
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    parents = subprocess.check_output(
        ["git", "show", "-s", "--format=%P", "HEAD"], text=True
    ).strip().split()
    branch = subprocess.check_output(
        ["git", "ls-remote", "origin", "refs/heads/main"], text=True
    ).strip().split()
    if len(branch) != 2 or branch[1] != "refs/heads/main":
        raise ValueError("LIVE_MAIN_NOT_READABLE")
    receipt = verify_event(event, parents, sha, branch[0], Path("."))
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    cli()
