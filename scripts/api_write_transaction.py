"""Cooperative, opt-in GitHub Git-object transaction with non-forced ref update.

For a trusted host ONLY: never give the GitHub credential to an LLM.
This cannot prevent a separately credentialed client from bypassing this script.
"""
import base64
import json
import os
import re
import subprocess
from urllib.parse import quote

try:
    from api_write_guard import (
        REPOSITORY, BRANCH, _sha, _read, _path, check_authenticated_proposal,
        check_authenticated_commit_readback, git_blob_sha, github_get_live,
    )
except ModuleNotFoundError:
    from scripts.api_write_guard import (
        REPOSITORY, BRANCH, _sha, _read, _path, check_authenticated_proposal,
        check_authenticated_commit_readback, git_blob_sha, github_get_live,
    )

PREFIX = "repos/" + REPOSITORY
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 1024 * 1024


def github_write_live(method, path, payload):
    """HTTP Git write via gh on the trusted host; disabled unless opted in.

    No subprocess shell, token in argv, credentials in logs, or force writes.
    This checks *configuration*, not the token's actual least-privilege scopes.
    """
    if os.environ.get("UFMS_ENABLE_GITHUB_WRITE") != "1":
        raise ValueError("Live GitHub write disabled by default")
    if not os.environ.get("GH_TOKEN"):
        raise ValueError("Dedicated GH_TOKEN required on trusted host")
    if os.environ.get("GH_HOST", "github.com") != "github.com":
        raise ValueError("Unexpected GitHub host")
    target = path.removeprefix(PREFIX + "/")
    if not path.startswith(PREFIX + "/"):
        raise ValueError("GitHub write path outside bound repository")
    allowed_posts = {"git/blobs", "git/trees", "git/commits"}
    if method == "POST" and target in allowed_posts:
        pass
    elif method == "PATCH" and target.startswith("git/refs/heads/"):
        branch = target.removeprefix("git/refs/heads/")
        if not BRANCH.fullmatch(branch):
            raise ValueError("Git reference not allowed")
        if (not isinstance(payload, dict) or set(payload) != {"sha", "force"}
                or payload["force"] is not False):
            raise ValueError("Non-forced ref update required")
        _sha(payload["sha"], "next_sha")
    else:
        raise ValueError("GitHub write endpoint not permitted")
    if not isinstance(payload, dict):
        raise ValueError("GitHub request body must be an object")
    try:
        proc = subprocess.run(
            ["gh", "api", "-i", "-X", method, "--input", "-", path],
            input=json.dumps(payload, ensure_ascii=True),
            text=True, capture_output=True, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("GitHub write unavailable") from exc
    output = proc.stdout.replace("\r\n", "\n")
    matches = list(re.finditer(r"(?m)^HTTP/[0-9.]+\s+([0-9]{3})(?:\s|$)", output))
    if not matches:
        raise ValueError("GitHub write missing HTTP status")
    status = int(matches[-1].group(1))
    split = output.find("\n\n", matches[-1].end())
    if status not in (200, 201) or split < 0 or proc.returncode != 0:
        # Deliberately omit stderr/body: could contain submitted file content.
        raise ValueError("GitHub write rejected or ambiguous")
    try:
        body = json.loads(output[split + 2:].strip())
    except ValueError as exc:
        raise ValueError("GitHub write malformed JSON") from exc
    if not isinstance(body, dict):
        raise ValueError("GitHub write malformed result")
    return {"status": status, "body": body}


def _write(writer, method, endpoint, payload, expected_status):
    if not callable(writer):
        raise ValueError("Trusted writer required")
    try:
        response = writer(method, endpoint, payload)
    except Exception as exc:
        raise ValueError("Authenticated write unavailable") from exc
    if (not isinstance(response, dict)
            or type(response.get("status")) is not int
            or response["status"] != expected_status
            or not isinstance(response.get("body"), dict)):
        raise ValueError("Authenticated write failed closed")
    return response["body"]


def _commit_once(proposal, contents, message, getter, writer):
    """Testable transaction core. Mock injection belongs ONLY in unit tests.

    Actual invocation is commit_live() with fixed authenticated transports.
    A successful ref update is not automatically reverted if later readback
    fails; the returned result therefore never authorizes merge or CI.
    """
    if (not isinstance(message, str) or not 1 <= len(message) <= 120
            or "\n" in message or "\r" in message or "\x00" in message):
        raise ValueError("Commit message invalid")
    if not isinstance(contents, dict):
        raise ValueError("Trusted final content map required")
    # Validate proposal and all exact outgoing bytes BEFORE any write.
    planned = check_authenticated_proposal(proposal, getter=getter)
    wanted = {entry["path"]: entry for entry in proposal["files"]}
    if set(contents) != set(wanted):
        raise ValueError("Content paths differ from authorized proposal")
    blobs = {}
    total = 0
    for path, entry in wanted.items():
        _path(path)
        value = contents[path]
        if not isinstance(value, str) or "\x00" in value:
            raise ValueError("Text content required; no NUL")
        try:
            raw = value.encode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise ValueError("Content not UTF-8 encodable") from exc
        total += len(raw)
        if len(raw) > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
            raise ValueError("Content exceeds safety limit")
        digest = git_blob_sha(raw)
        if digest != entry["expected_new_blob_sha"]:
            raise ValueError("Content bytes differ from proposed final blob")
        blobs[path] = (raw, digest)

    old_head = planned["expected_head_sha"]
    _, old_commit = _read(getter, PREFIX + "/git/commits/" + old_head)
    old_tree = old_commit.get("tree")
    if not isinstance(old_tree, dict):
        raise ValueError("Original commit tree unavailable")
    base_tree = _sha(old_tree.get("sha"), "base_tree_sha")

    # Writing orphan blobs/trees does not change a branch. The actual branch
    # update is a single non-forced PATCH; a concurrent divergent commit
    # causes 409/422, not overwrite.
    tree_entries = []
    for path in sorted(blobs):
        raw, digest = blobs[path]
        result = _write(writer, "POST", PREFIX + "/git/blobs", {
            "content": base64.b64encode(raw).decode("ascii"), "encoding": "base64",
        }, 201)
        if result.get("sha") != digest:
            raise ValueError("GitHub blob does not match planned bytes")
        tree_entries.append({
            "path": path, "mode": "100644", "type": "blob", "sha": digest,
        })
    tree = _write(writer, "POST", PREFIX + "/git/trees", {
        "base_tree": base_tree, "tree": tree_entries,
    }, 201)
    new_tree_sha = _sha(tree.get("sha"), "new_tree_sha")
    commit = _write(writer, "POST", PREFIX + "/git/commits", {
        "message": message, "tree": new_tree_sha, "parents": [old_head],
    }, 201)
    new_sha = _sha(commit.get("sha"), "new_commit_sha")
    if new_sha == old_head:
        raise ValueError("GitHub commit did not advance")
    # Recheck snapshot before attempting the atomic reference update.
    second = check_authenticated_proposal(proposal, getter=getter)
    if second["base_sha"] != planned["base_sha"]:
        raise ValueError("Base moved before reference update")
    ref = PREFIX + "/git/refs/heads/" + quote(proposal["branch"], safe="/")
    updated = _write(writer, "PATCH", ref, {
        "sha": new_sha, "force": False,
    }, 200)
    if (updated.get("ref") != "refs/heads/" + proposal["branch"]
            or not isinstance(updated.get("object"), dict)
            or updated["object"].get("sha") != new_sha):
        raise ValueError("GitHub reference response diverged")
    verified = check_authenticated_commit_readback(
        proposal, new_sha, planned["base_sha"], getter=getter,
    )
    return {**verified, "ref_update": "non_forced_fast_forward",
            "ci_verified": False, "merge_authorized": False}


def commit_live(proposal, trusted_final_contents, message):
    """Production entrypoint. Never accepts caller-supplied GET/POST transports.

    The host must compute expected_new_blob_sha from its trusted payload bytes
    and keep GH_TOKEN out of the model/container exposed to agent prompts.
    """
    return _commit_once(
        proposal, trusted_final_contents, message,
        github_get_live, github_write_live,
    )
