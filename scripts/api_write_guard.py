"""Pré-validação pura para propostas de escrita via API GitHub.

É uma ferramenta para clientes cooperativos: não intercepta a API, não autentica
o GitHub nem impede push de atores que a ignorem. O chamador deve obter
contexto fresco por leitura autenticada, empregar SHA/lease e validar readback.
Nenhum dado pessoal pode ser gravado por este caminho nesta fase.
"""
import re
from pathlib import PurePosixPath

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
    if proposal.get("pr_number") != 1 or proposal.get("draft") is not True:
        raise ValueError("PR #1 precisa estar em draft")
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
        "files": tuple(sorted(seen)), "preflight": "accepted_for_cooperative_client",
        "server_side_enforcement": False,
    }


def check_readback(proposal, committed_sha, observed_head_sha, ci_sha, ci_conclusion):
    """Verificação posterior de commit e CI, sem declarar proteção do servidor."""
    summary = check_proposal(proposal)
    committed = _sha(committed_sha, "committed_sha")
    observed = _sha(observed_head_sha, "observed_head_sha")
    validated = _sha(ci_sha, "ci_sha")
    if committed != observed:
        raise ValueError("Readback remoto divergente; HEAD não corresponde ao commit")
    if committed != validated or ci_conclusion != "success":
        raise ValueError("CI não aprovada para SHA exato do commit")
    return {**summary, "committed_sha": committed, "ci": "success",
            "readback": "same_commit", "merge_authorized": False}
