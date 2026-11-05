"""Pré-validação pura para propostas de escrita via API GitHub.

É uma ferramenta para clientes cooperativos: não intercepta a API, não autentica
o GitHub nem impede push de atores que a ignorem. O chamador deve obter
contexto fresco por leitura autenticada, empregar SHA/lease e validar readback.
Bloqueia os caminhos pessoais conhecidos nesta fase, mas NAO inspeciona\no conteudo de documentos permitidos: revisao humana e privacidade seguem obrigatorias.
"""
import json
import re
import subprocess
from pathlib import PurePosixPath
from urllib.parse import quote

REPOSITORY = "Andraus35/UFMS-MEU-ESTUDO"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
BRANCH = re.compile(r"^(setup|automation|fix|docs|audit)/[a-zA-Z0-9][a-zA-Z0-9._/-]{0,160}$")
BLOCKED_PREFIXES = (
    "state/", "edital/", "private/", "raw/", "exports/",
    "screenshots/", "relatorios-brutos/", "guardrails/", "rules/",
    "hooks/", ".github/", "secrets/",
)
BLOCKED_FILES = frozenset({
    "AGENTS.md", "settings.json", ".gitignore", "memory/DECISIONS.md",
    "memory/PROFILE.md", "scripts/write_policy.py", "scripts/validate.py",
    "scripts/rebuild.py", "scripts/agent_gates.py",
    "scripts/api_write_guard.py", "scripts/ci_gate_contract.py",
})
ALLOW_PREFIXES = ("docs/", "tests/", "templates/", "scripts/")
ALLOW_FILES = frozenset({"README.md", "memory/HANDOFF.md", "config/project.json"})


def _sha(value, label):
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        raise ValueError(label + " precisa ser SHA-1 Git completo")
    return value


def _path(value):
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        raise ValueError("Caminho inválido")
    p = PurePosixPath(value)
    if str(p) != value or any(x in (".", "..", "") for x in value.split("/")):
        raise ValueError("Caminho normalizado inválido")
    if value in BLOCKED_FILES or value.startswith(BLOCKED_PREFIXES):
        raise ValueError("Caminho sensível exige revisão humana independente: " + value)
    if not (value in ALLOW_FILES or value.startswith(ALLOW_PREFIXES)):
        raise ValueError("Caminho não autorizado neste fluxo: " + value)
    if p.name.startswith(".") or p.suffix.lower() in {".pem", ".key", ".env", ".sqlite", ".db"}:
        raise ValueError("Arquivo secreto ou binário bloqueado: " + value)
    return value


def check_proposal(proposal):
    """Valida dados recebidos de leitura autenticada; NÃO autentica tais dados."""
    if not isinstance(proposal, dict):
        raise ValueError("Proposta inválida")
    if proposal.get("repository") != REPOSITORY:
        raise ValueError("Repositório divergente")
    if proposal.get("base_branch") != "main":
        raise ValueError("Base não é main")
    branch = proposal.get("branch")
    if not isinstance(branch, str) or not BRANCH.fullmatch(branch) or branch in {"main", "master"}:
        raise ValueError("Escrita fora de branch de trabalho")
    number = proposal.get("pr_number")
    if type(number) is not int or number < 1:
        raise ValueError("Numero de PR precisa ser inteiro positivo")
    if proposal.get("draft") is not True:
        raise ValueError("PR precisa estar em draft")
    if proposal.get("merged") is not False or proposal.get("state") != "open":
        raise ValueError("PR encerrado ou já mesclado")
    expected = _sha(proposal.get("expected_head_sha"), "expected_head_sha")
    observed = _sha(proposal.get("observed_head_sha"), "observed_head_sha")
    if expected != observed:
        raise ValueError("HEAD mudou; recomeçar preflight com leitura autenticada")
    files = proposal.get("files")
    if not isinstance(files, list) or not files or len(files) > 20:
        raise ValueError("Lista de arquivos inválida")
    seen = set()
    for file in files:
        if not isinstance(file, dict):
            raise ValueError("Arquivo de proposta inválido")
        path = _path(file.get("path"))
        if path in seen:
            raise ValueError("Arquivo duplicado na proposta")
        seen.add(path)
        mode = file.get("operation")
        if mode == "update":
            _sha(file.get("expected_blob_sha"), "expected_blob_sha")
        elif mode == "create":
            if file.get("expected_blob_sha") is not None:
                raise ValueError("Criação não pode ter blob anterior")
        else:
            raise ValueError("Operação não autorizada")
    return {
        "repository": REPOSITORY, "branch": branch, "expected_head_sha": expected,
        "files": tuple(sorted(seen)), "pr_number": number,
        "preflight": "structure_only_not_authenticated",
        "authenticated_remote_read": False, "server_side_enforcement": False,
        "merge_authorized": False,
    }


def check_readback(proposal, committed_sha, observed_head_sha, ci_sha, ci_conclusion):
    """Consistency check of caller claims; no authenticated CI readback."""
    summary = check_proposal(proposal)
    committed = _sha(committed_sha, "committed_sha")
    observed = _sha(observed_head_sha, "observed_head_sha")
    validated = _sha(ci_sha, "ci_sha")
    if committed != observed:
        raise ValueError("Readback remoto divergente; HEAD não corresponde ao commit")
    if committed != validated or ci_conclusion != "success":
        raise ValueError("CI não aprovada para SHA exato do commit")
    return {**summary, "committed_sha": committed,
            "claimed_ci": "success_unverified",
            "readback": "caller_asserted_only",
            "ci_verified": False, "authenticated_remote_read": False,
            "merge_authorized": False}


def github_get_live(path):
    """Authenticated host-side HTTP read using GitHub CLI (not the LLM)."""
    if (not isinstance(path, str)
            or not path.startswith("repos/" + REPOSITORY + "/")
            or "\r" in path or "\n" in path):
        raise ValueError("GitHub API path not permitted")
    try:
        result = subprocess.run(["gh", "api", "-i", path], check=False,
                                capture_output=True, text=True, timeout=25)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Authenticated GitHub read unavailable") from exc
    output = result.stdout.replace("\r\n", "\n")
    headers = list(re.finditer(r"(?m)^HTTP/[0-9.]+\s+([0-9]{3})(?:\s|$)",
                              output))
    if not headers:
        raise ValueError("GitHub HTTP status not found")
    status = int(headers[-1].group(1))
    sep = output.find("\n\n", headers[-1].end())
    if sep < 0 or status not in (200, 404):
        raise ValueError("GitHub HTTP response unavailable")
    if result.returncode != 0 and not (status == 404 and result.returncode == 1):
        raise ValueError("GitHub CLI returned failure")
    try:
        body = json.loads(output[sep + 2:].strip())
    except ValueError as exc:
        raise ValueError("Malformed GitHub JSON") from exc
    if not isinstance(body, dict):
        raise ValueError("Malformed GitHub response shape")
    return {"status": status, "body": body}


def _read(getter, path, allowed=(200,)):
    if not callable(getter):
        raise ValueError("Trusted authenticated reader required")
    try:
        response = getter(path)
    except Exception as exc:
        raise ValueError("Authenticated read unavailable") from exc
    if (not isinstance(response, dict)
            or type(response.get("status")) is not int
            or response["status"] not in allowed
            or not isinstance(response.get("body"), dict)):
        raise ValueError("Authenticated read rejected or malformed")
    return response["status"], response["body"]


def check_authenticated_proposal(proposal, getter=github_get_live):
    """Verify LIVE PR, branch, base and all expected file blobs.

    The getter must be supplied by a trusted executor, never by the model.
    Even with fresh readbacks this is only a cooperative preflight, not
    a permission to write, an atomic Git transaction, or merge approval.
    """
    record = check_proposal(proposal)
    prefix = "repos/" + REPOSITORY
    pr_id = record["pr_number"]
    branch = record["branch"]
    head_sha = record["expected_head_sha"]
    _, pr = _read(getter, prefix + "/pulls/" + str(pr_id))
    if (pr.get("number") != pr_id or pr.get("state") != "open"
            or pr.get("draft") is not True or pr.get("merged_at") is not None
            or pr.get("merged") is True):
        raise ValueError("Remote PR is closed, merged or not draft")
    remote_head, remote_base = pr.get("head"), pr.get("base")
    if not isinstance(remote_head, dict) or not isinstance(remote_base, dict):
        raise ValueError("Remote PR missing refs")
    if (remote_head.get("sha") != head_sha
            or remote_head.get("ref") != branch
            or not isinstance(remote_head.get("repo"), dict)
            or remote_head["repo"].get("full_name") != REPOSITORY
            or remote_base.get("ref") != "main"
            or not isinstance(remote_base.get("repo"), dict)
            or remote_base["repo"].get("full_name") != REPOSITORY):
        raise ValueError("Remote PR identity mismatch")
    _, main = _read(getter, prefix + "/branches/main")
    main_sha = main.get("commit", {}).get("sha")
    _sha(main_sha, "main_sha")
    if remote_base.get("sha") != main_sha:
        raise ValueError("PR base stale against main")
    _, work = _read(getter, prefix + "/branches/" + quote(branch, safe="/"))
    if work.get("commit", {}).get("sha") != head_sha:
        raise ValueError("PR branch HEAD changed")
    for entry in proposal["files"]:
        path = _path(entry["path"])
        uri = prefix + "/contents/" + quote(path, safe="/") + "?ref=" + head_sha
        status, body = _read(getter, uri, allowed=(200, 404))
        if entry["operation"] == "update":
            if (status != 200 or body.get("type") != "file"
                    or body.get("sha") != entry["expected_blob_sha"]):
                raise ValueError("Blob not confirmed for update")
        elif status != 404:
            raise ValueError("Create target already exists")
    return {**record, "authenticated_remote_read": True,
            "preflight": "authenticated_snapshot_only",
            "base_sha": main_sha, "merge_authorized": False}


def check_authenticated_commit_readback(proposal, committed_sha,
                                         expected_base_sha,
                                         getter=github_get_live):
    """Read GitHub post-commit; require a single direct-descendant commit.

    The host supplies the authenticated getter and the pre-commit baseline.
    This reports identity/ancestry only: CI remains UNVERIFIED and merger
    authorization remains False.
    """
    original = check_proposal(proposal)
    new_sha = _sha(committed_sha, "committed_sha")
    main_sha = _sha(expected_base_sha, "expected_base_sha")
    old_sha = original["expected_head_sha"]
    if new_sha == old_sha:
        raise ValueError("No new commit to confirm")
    prefix = "repos/" + REPOSITORY
    number = original["pr_number"]
    branch = original["branch"]
    _, pr = _read(getter, prefix + "/pulls/" + str(number))
    if (pr.get("number") != number or pr.get("state") != "open"
            or pr.get("draft") is not True or pr.get("merged_at") is not None
            or pr.get("merged") is True):
        raise ValueError("PR not open draft at post-commit readback")
    head, base = pr.get("head"), pr.get("base")
    if not isinstance(head, dict) or not isinstance(base, dict):
        raise ValueError("PR refs unavailable")
    if (head.get("sha") != new_sha or head.get("ref") != branch
            or not isinstance(head.get("repo"), dict)
            or head["repo"].get("full_name") != REPOSITORY
            or base.get("ref") != "main" or base.get("sha") != main_sha
            or not isinstance(base.get("repo"), dict)
            or base["repo"].get("full_name") != REPOSITORY):
        raise ValueError("PR identity or base changed after commit")
    _, main = _read(getter, prefix + "/branches/main")
    if main.get("commit", {}).get("sha") != main_sha:
        raise ValueError("Main changed after preflight")
    _, work = _read(getter, prefix + "/branches/"
                    + quote(branch, safe="/"))
    if work.get("commit", {}).get("sha") != new_sha:
        raise ValueError("Branch did not advance to committed SHA")
    _, commit = _read(getter, prefix + "/git/commits/" + new_sha)
    parents = commit.get("parents")
    if (not isinstance(parents, list) or len(parents) != 1
            or not isinstance(parents[0], dict)
            or parents[0].get("sha") != old_sha):
        raise ValueError("New commit not a direct descendant of expected HEAD")
    return {**original, "committed_sha": new_sha, "base_sha": main_sha,
            "readback": "authenticated_postcommit_direct_descendant",
            "authenticated_remote_read": True, "ci_verified": False,
            "merge_authorized": False}
