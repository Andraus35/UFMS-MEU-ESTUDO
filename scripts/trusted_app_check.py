"""External GitHub App check publisher: run from a trusted, PINNED Oracle checkout.

NOT a GitHub Actions job; its checks have the GitHub App's OWN app ID.
Run as a short-lived cron job. No webhook port, LLM or candidate-code execution.
Environment secrets: UFMS_GITHUB_APP_ID, UFMS_GITHUB_APP_KEY_FILE,
UFMS_APPROVAL_PUBKEY_B64. Never expose these to Tutor/Coach.
"""
import argparse
import base64
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from trusted_governance import REPOSITORY, _check_sha, enforce

CHECK_NAME = "ufms-governance/app-verified"
APP_ID = re.compile(r"^[1-9][0-9]{0,18}$")


def _b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def app_jwt(app_id, private_key_file, now=None):
    """Generate RS256 JWT locally. The App RSA private key never crosses the API."""
    if not isinstance(app_id, str) or not APP_ID.fullmatch(app_id):
        raise ValueError("App ID invalid")
    key = Path(private_key_file)
    if not key.is_file() or key.is_symlink():
        raise ValueError("App private key missing or symlinked")
    t = int(time.time() if now is None else now)
    header = _b64url(b'{"alg":"RS256","typ":"JWT"}')
    claims = _b64url(json.dumps({
        "iat": t-60, "exp": t+540, "iss": app_id,
    }, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    message = (header+"."+claims).encode("ascii")
    try:
        proc = subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(key)],
                              input=message, capture_output=True, check=False,
                              timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Cannot sign GitHub App JWT") from exc
    if proc.returncode != 0:
        raise ValueError("GitHub App JWT signature failed")
    return message.decode("ascii")+"."+_b64url(proc.stdout)


def api_json(method, path, token, payload=None):
    if not isinstance(path, str) or not path.startswith(("repos/", "app", "user")):
        raise ValueError("Invalid GitHub API path")
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ufms-governance-external-app",
    }
    data = None
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        "https://api.github.com/" + path, headers=headers, data=data,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        # Do not include token, private key, or GitHub's full error body.
        raise ValueError("GitHub App API unavailable; no success emitted") from exc


def installation_token(jwt, app_id):
    app = api_json("GET", "app", jwt)
    if not isinstance(app, dict) or app.get("id") != int(app_id):
        raise ValueError("JWT is not issued by the expected GitHub App")
    install = api_json("GET", f"repos/{REPOSITORY}/installation", jwt)
    if (not isinstance(install, dict)
            or install.get("app_id") != int(app_id)
            or type(install.get("id")) is not int):
        raise ValueError("Unexpected app installation")
    answer = api_json(
        "POST", f"app/installations/{install['id']}/access_tokens", jwt,
        {"repositories": [REPOSITORY.split("/")[1]],
         "permissions": {
             "checks": "write", "pull_requests": "read", "issues": "read",
         }},
    )
    if not isinstance(answer, dict) or not isinstance(answer.get("token"), str):
        raise ValueError("No valid short-lived installation token")
    return answer["token"]


def verify_one(pr_number, installation, app_id, public_key):
    if type(pr_number) is not int or pr_number <= 0:
        raise ValueError("Invalid PR")
    endpoint = f"repos/{REPOSITORY}/pulls/{pr_number}"
    metadata = api_json("GET", endpoint, installation)
    if (not isinstance(metadata, dict) or metadata.get("number") != pr_number
            or metadata.get("state") != "open"
            or metadata.get("base", {}).get("ref") != "main"):
        raise ValueError("PR missing, closed or wrong base branch")
    head = _check_sha(metadata.get("head", {}).get("sha"), "PR HEAD")
    base = _check_sha(metadata.get("base", {}).get("sha"), "PR BASE")

    # Use the same fail-closed policy, but the App, rather than Actions, is the
    # attested check run SOURCE. A failing evaluation still publishes failure.
    env = {
        "GITHUB_TOKEN": installation,
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_EVENT_NAME": "trusted_github_app",
        "PR_NUMBER": str(pr_number),
        "PR_HEAD_SHA": head,
        "PR_BASE_SHA": base,
        "UFMS_APPROVAL_PUBKEY_B64": public_key,
    }
    verdict, explanation = "failure", "Policy check failed (fail closed)"
    try:
        enforce(env)
        verdict, explanation = "success", "Trusted-base policy passed"
    except (ValueError, TypeError, KeyError):
        pass

    # Prevent reporting a success when HEAD/base move after evaluation.
    try:
        after = api_json("GET", endpoint, installation)
        if (after.get("head", {}).get("sha") != head
                or after.get("base", {}).get("sha") != base
                or after.get("state") != "open"):
            verdict, explanation = "failure", "PR changed after evaluation"
    except (ValueError, AttributeError):
        verdict, explanation = "failure", "PR identity readback failed"

    body = {
        "name": CHECK_NAME,
        "head_sha": head,
        "status": "completed",
        "conclusion": verdict,
        "external_id": f"pr{pr_number}:{head}",
        "output": {"title": "UFMS independent governance policy",
                   "summary": explanation},
    }
    checked = api_json("POST", f"repos/{REPOSITORY}/check-runs", installation, body)
    if (not isinstance(checked, dict) or checked.get("head_sha") != head
            or checked.get("name") != CHECK_NAME
            or checked.get("app", {}).get("id") != int(app_id)
            or checked.get("conclusion") != verdict):
        raise ValueError("GitHub check readback identity mismatch")
    return {"pr": pr_number, "head": head, "conclusion": verdict,
            "check_name": CHECK_NAME, "app_id": int(app_id)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--once", action="store_true", required=True)
    args = parser.parse_args()
    appid = os.environ.get("UFMS_GITHUB_APP_ID", "")
    keyfile = os.environ.get("UFMS_GITHUB_APP_KEY_FILE", "")
    pubkey = os.environ.get("UFMS_APPROVAL_PUBKEY_B64", "")
    if not pubkey:
        raise SystemExit("BLOCKED: missing public verification key")
    # Hold a local lock to prevent concurrent cron passes using stale status.
    with tempfile.TemporaryFile() as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            jwt = app_jwt(appid, keyfile)
            installation = installation_token(jwt, appid)
            result = verify_one(args.pr, installation, appid, pubkey)
        except (ValueError, KeyError, TypeError) as exc:
            raise SystemExit("BLOCKED: " + str(exc))
    print(json.dumps(result, sort_keys=True))
    if result["conclusion"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
