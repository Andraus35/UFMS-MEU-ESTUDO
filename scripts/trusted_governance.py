"""Read-only governance gate executed ONLY from the protected base branch.
Never execute/import PR code. For strategic changes require a human-held Ed25519
signature, not an approval that a credentialed agent can forge.
"""
import base64
import binascii
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

REPOSITORY = "Andraus35/UFMS-MEU-ESTUDO"
OWNER_ID = 273433050
OWNER_LOGIN = "Andraus35"
LOCKED = frozenset({
    ".github/workflows/trusted-governance.yml",
    "scripts/trusted_governance.py",
    "tests/test_trusted_governance.py",
    "scripts/trusted_app_check.py",
    "tests/test_trusted_app_check.py",
})
SENSITIVE_EXACT = frozenset({
    "AGENTS.md", "ROADMAP.md", "settings.json",
    ".github/CODEOWNERS", "README.md",
    "scripts/agent_gates.py", "scripts/bootstrap.py",
    "scripts/roadmap_gate.py", "scripts/ci_gate_contract.py",
    "scripts/validate.py", "scripts/write_policy.py",
    "scripts/api_write_guard.py", "scripts/protect_main.py",
})
SENSITIVE_PREFIXES = (
    ".github/", "scripts/", "tests/", "rules/", "guardrails/",
    "hooks/", "config/", "edital/", "state/", "memory/",
    "docs/",
)
SHA = re.compile(r"^[0-9a-f]{40}$")


def _check_sha(value, label):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError(label + " is not a full Git SHA")
    return value


def _path(value):
    if (not isinstance(value, str) or not value or value.startswith("/")
            or "\\" in value or any(x in ("", ".", "..") for x in value.split("/"))):
        raise ValueError("Unsafe changed path")
    return value


def approval_text(pr_number, head_sha, base_sha):
    if type(pr_number) is not int or pr_number <= 0:
        raise ValueError("Invalid PR number")
    _check_sha(head_sha, "HEAD")
    _check_sha(base_sha, "BASE")
    return f"GOVERNANCE-REVIEWED PR={pr_number} HEAD={head_sha} BASE={base_sha}"


def signature_comment(message, signature):
    return message + " SIG=" + base64.b64encode(signature).decode("ascii")


def verify_signature(message, signature_b64, pubkey_b64):
    """Verify signature against admin-set PUBLIC key, never PR-provided keys."""
    if not pubkey_b64:
        return False
    try:
        signature = base64.b64decode(signature_b64, validate=True)
        pubkey = base64.b64decode(pubkey_b64, validate=True)
        if len(signature) != 64 or not pubkey.startswith(b"-----BEGIN PUBLIC KEY-----\n"):
            return False
        with tempfile.TemporaryDirectory(prefix="ufms-trust-") as folder:
            path = Path(folder)
            (path / "key.pem").write_bytes(pubkey)
            (path / "approval.txt").write_bytes(message.encode("utf-8"))
            (path / "signature.bin").write_bytes(signature)
            proc = subprocess.run(
                ["openssl", "pkeyutl", "-verify", "-pubin",
                 "-inkey", str(path / "key.pem"), "-rawin",
                 "-in", str(path / "approval.txt"),
                 "-sigfile", str(path / "signature.bin")],
                capture_output=True, check=False, timeout=10,
            )
            return proc.returncode == 0
    except (ValueError, binascii.Error, OSError, subprocess.TimeoutExpired):
        return False


def evaluate(pr_number, head_sha, base_sha, paths, comments, pubkey_b64=""):
    """Fail-closed policy: paths/comments obtained by authenticated GitHub REST."""
    expected = approval_text(pr_number, head_sha, base_sha)
    if not isinstance(paths, list) or not paths:
        raise ValueError("Missing PR files or empty diff")
    if not isinstance(comments, list):
        raise ValueError("Missing approval comments")
    # GitHub reports renamed files with current *and* previous names.
    # A protected file removed by renaming must never disappear from the diff gate.
    modified = set()
    for item in paths:
        if not isinstance(item, dict):
            raise ValueError("PR file record must contain GitHub filename and status")
        status = item.get("status")
        if status not in {"added", "modified", "removed", "renamed", "changed", "copied"}:
            raise ValueError("Unknown PR file change status")
        current = _path(item.get("filename"))
        modified.add(current)
        old_name = item.get("previous_filename")
        if status == "renamed":
            if not isinstance(old_name, str) or old_name == current:
                raise ValueError("Renamed file without distinct previous_filename")
            modified.add(_path(old_name))
        elif old_name is not None:
            # A non-renamed record with a previous path is suspicious; fail closed.
            raise ValueError("Unexpected previous_filename outside rename")
    frozen = sorted(modified & LOCKED)
    if frozen:
        raise ValueError("Immutable trusted gate modified: " + ", ".join(frozen))
    sensitive = sorted(p for p in modified
                       if p in SENSITIVE_EXACT or p.startswith(SENSITIVE_PREFIXES))
    if not sensitive:
        return {"result": "pass", "protected_files": 0, "signed_review": False}
    approved = False
    for comment in comments:
        if not isinstance(comment, dict) or not isinstance(comment.get("user"), dict):
            continue
        user = comment["user"]
        if (user.get("login") != OWNER_LOGIN or user.get("id") != OWNER_ID
                or user.get("type") != "User"):
            continue
        body = comment.get("body", "")
        if not isinstance(body, str) or not body.startswith(expected + " SIG="):
            continue
        signature = body[len(expected) + 5:].strip()
        if (" " in signature or "\n" in signature or not signature):
            continue
        if verify_signature(expected, signature, pubkey_b64):
            approved = True
            break
    if not approved:
        raise ValueError("Governance paths require Ed25519 human signature for EXACT HEAD/BASE: "
                         + ", ".join(sensitive))
    return {"result": "pass", "protected_files": len(sensitive), "signed_review": True}


def get_json(path, token):
    req = urllib.request.Request(
        "https://api.github.com/" + path,
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "ufms-trusted-governance-read-only"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)
    except (urllib.error.URLError, ValueError, OSError) as exc:
        raise ValueError("GitHub read failed; fail closed") from exc


def get_collection(path, token, max_pages=10):
    output = []
    for page in range(1, max_pages + 1):
        part = get_json(path + ("&" if "?" in path else "?")
                        + f"per_page=100&page={page}", token)
        if not isinstance(part, list):
            raise ValueError("Unexpected GitHub collection response")
        output.extend(part)
        if len(part) < 100:
            return output
    raise ValueError("Collection exceeds maximum audited page count")


def _identity(metadata, number, head, base):
    if not isinstance(metadata, dict):
        raise ValueError("Malformed PR metadata")
    if (metadata.get("number") != number
            or metadata.get("base", {}).get("ref") != "main"
            or metadata.get("base", {}).get("sha") != base
            or metadata.get("head", {}).get("sha") != head
            or metadata.get("state") != "open"):
        raise ValueError("PR identity / event SHA mismatch")
    count = metadata.get("changed_files")
    if type(count) is not int or not 1 <= count <= 3000:
        raise ValueError("Missing or excessive changed_files")
    return count


def enforce(env):
    token = env.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("Missing read-only GitHub token")
    if env.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise ValueError("Unexpected repository")
    if env.get("GITHUB_EVENT_NAME") not in {"pull_request_target", "trusted_github_app"}:
        raise ValueError("Untrusted event type for privileged gate")
    pr_number = int(env["PR_NUMBER"])
    head = _check_sha(env["PR_HEAD_SHA"], "Event HEAD")
    base = _check_sha(env["PR_BASE_SHA"], "Event BASE")
    endpoint = f"repos/{REPOSITORY}/pulls/{pr_number}"
    count = _identity(get_json(endpoint, token), pr_number, head, base)

    records = get_collection(f"{endpoint}/files", token, max_pages=30)
    if len(records) != count:
        raise ValueError("Partial or inconsistent PR diff: changed_files mismatch")
    # Reject duplicate file records even if the count was manipulated.
    names = [record.get("filename") if isinstance(record, dict) else None
             for record in records]
    if None in names or len(set(names)) != len(names):
        raise ValueError("Malformed or duplicated PR files")

    comments = get_collection(
        f"repos/{REPOSITORY}/issues/{pr_number}/comments", token,
        max_pages=30)
    # Identity and count MUST still match after the separate API reads.
    if _identity(get_json(endpoint, token), pr_number, head, base) != count:
        raise ValueError("PR diff changed during governance evaluation")
    branch = get_json(f"repos/{REPOSITORY}/branches/main", token)
    if not isinstance(branch, dict) or branch.get("protected") is not True:
        raise ValueError("Main branch protection not independently confirmed")
    if branch.get("commit", {}).get("sha") != base:
        raise ValueError("Main branch advanced while evaluating PR")

    return evaluate(pr_number, head, base, records, comments,
                    env.get("UFMS_APPROVAL_PUBKEY_B64", ""))


def main():
    if sys.argv[1:] != ["--check"]:
        raise SystemExit("Usage: python scripts/trusted_governance.py --check")
    try:
        result = enforce(os.environ)
    except (ValueError, TypeError, KeyError) as exc:
        print("FAIL-CLOSED: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
    print("OK: checked against protected base: "
          + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
