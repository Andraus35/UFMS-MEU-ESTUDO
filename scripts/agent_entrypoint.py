"""Fail-closed local START gate for a future Tutor/Coach broker.

This library has NO write-capable actions. The production agent runtime must
hold credentials and route every tool invocation through its own gate.
An LLM instruction, CLI invocation or receipt cannot restrict a client that
has been given direct provider credentials.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

MANDATORY = (
    "AGENTS.md", "ROADMAP.md", "settings.json", "rules/CORE.md",
    "guardrails/CORE.md", "memory/INDEX.md", "memory/HANDOFF.md",
    "state/CURRENT.json", "EDITAL_UFMS_152_2026.md", "edital/INDEX.md",
)
SHA40 = re.compile(r"^[a-f0-9]{40}$")
ROW = re.compile(r"^\|\s*(RM-\d{2})\s*\|\s*(P[0-2])\s*\|")
STATES = frozenset({
    "planejado", "em_andamento", "implementado_nao_homologado",
    "bloqueado", "homologado",
})
ROLES = frozenset({"tutor", "coach", "engineer", "auditor"})
READ_ACTIONS = frozenset({"start", "inspect"})


class GateClosed(Exception):
    """An operation cannot continue without a verified START."""


def _file(root, relative):
    base = Path(root).resolve()
    candidate = base / relative
    if (candidate.is_symlink() or not candidate.resolve().is_relative_to(base)
            or not candidate.is_file()):
        raise GateClosed("Mandatory file missing or escaped root: " + relative)
    try:
        raw = candidate.read_bytes()
        decoded = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise GateClosed("Cannot read mandatory UTF-8: " + relative) from exc
    if not raw.strip():
        raise GateClosed("Empty mandatory document: " + relative)
    return decoded, hashlib.sha256(raw).hexdigest()


def _roadmap(rows):
    if len(rows.encode("utf-8")) < 3000:
        raise GateClosed("ROADMAP truncated")
    if "## Governança e leitura obrigatória" not in rows:
        raise GateClosed("Missing roadmap governance")
    ids = []
    for line in rows.splitlines():
        matched = ROW.match(line)
        if not matched:
            continue
        items = [c.strip() for c in line.split("|")[1:-1]]
        if len(items) != 5 or items[3] not in STATES or len(items[4]) < 25:
            raise GateClosed("Invalid roadmap row")
        ids.append(matched.group(1))
    if ids != [f"RM-{n:02d}" for n in range(11)]:
        raise GateClosed("Incomplete or reordered roadmap queue")


def _git_head(root):
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateClosed("Cannot inspect Git HEAD") from exc
    if proc.returncode != 0:
        raise GateClosed("Repository checkout unavailable")
    return proc.stdout.strip()


def _git_clean(root):
    """A local changed checkout cannot impersonate a reviewed Git revision."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateClosed("Cannot verify clean checkout") from exc
    if proc.returncode != 0 or proc.stdout.strip():
        raise GateClosed("Dirty or unverifiable checkout")


def verify_start(root, trusted_head):
    """Verify a trusted revision and mandated bytes; no caller-controlled bypass."""
    if not isinstance(trusted_head, str) or not SHA40.fullmatch(trusted_head):
        raise GateClosed("Trusted SHA not provided or malformed")
    root = Path(root).resolve()
    observed = _git_head(root)
    if observed != trusted_head:
        raise GateClosed("HEAD changed or was not the trusted SHA")
    _git_clean(root)
    texts, hashes = {}, {}
    for relative in MANDATORY:
        texts[relative], hashes[relative] = _file(root, relative)
    try:
        mandatory = json.loads(texts["settings.json"])["bootstrap"]["mandatory"]
    except (ValueError, KeyError, TypeError) as exc:
        raise GateClosed("Invalid settings") from exc
    if mandatory != list(MANDATORY):
        raise GateClosed("Mandatory file list/order mismatch")
    if "2. \`ROADMAP.md\`" not in texts["AGENTS.md"]:
        raise GateClosed("AGENTS missing ordered roadmap contract")
    _roadmap(texts["ROADMAP.md"])
    return {
        "head": trusted_head,
        "hashes": hashes,
        "roadmap": texts["ROADMAP.md"],
        "agents": texts["AGENTS.md"],
    }


class AgentBroker:
    """No provider credentials, no tool execution, no outward write routes."""
    def __init__(self, root, trusted_head):
        self._root = Path(root).resolve()
        self._trusted_head = trusted_head
        self._snapshot = verify_start(self._root, trusted_head)

    def _refresh(self):
        # START receipt cannot be replayed after local code/files change.
        self._snapshot = verify_start(self._root, self._trusted_head)

    def request(self, role, action):
        if role not in ROLES:
            raise GateClosed("Unknown agent role")
        if action not in READ_ACTIONS:
            raise GateClosed("No protected writes enabled in this broker")
        self._refresh()
        return {
            "status": "bootstrap_verified",
            "scope": "local_read_only",
            "head": self._snapshot["head"],
            "role": role,
            "action": action,
            "roadmap_sha256": self._snapshot["hashes"]["ROADMAP.md"],
            "mandatory_count": len(MANDATORY),
            "docs_to_supply_to_model": ("AGENTS.md", "ROADMAP.md"),
        }

    def prompt_context(self):
        """Return trusted texts after fresh validation for the actual model call."""
        self._refresh()
        return self._snapshot["agents"], self._snapshot["roadmap"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=sorted(ROLES), required=True)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    try:
        broker = AgentBroker(args.root, os.environ.get("UFMS_TRUSTED_HEAD_SHA", ""))
        print(json.dumps(broker.request(args.role, "start"), sort_keys=True))
    except GateClosed as exc:
        raise SystemExit("BLOCKED: " + str(exc))


if __name__ == "__main__":
    main()
