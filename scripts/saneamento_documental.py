"""Safe, idempotent, evidence-based governance-document reconciliation.

Only writes reviewable snapshots and bounded status banners in a non-main
draft-PR checkout. Never edits historical bodies, policy, edital, state,
credentials, hooks, branch protection, or GitHub settings.
GitHub state is read through authenticated gh api, never guessed from prose.
"""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

REPOSITORY = "Andraus35/UFMS-MEU-ESTUDO"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
START = "<!-- governance-current:start -->"
END = "<!-- governance-current:end -->"
STATUS_PATH = "docs/governanca/STATUS_VIGENTE.md"
TARGETS = {
    "memory/INDEX.md": "../docs/governanca/STATUS_VIGENTE.md",
    "memory/HANDOFF.md": "../docs/governanca/STATUS_VIGENTE.md",
    "memory/DECISIONS.md": "../docs/governanca/STATUS_VIGENTE.md",
    "docs/API_WRITE_GOVERNANCE.md": "governanca/STATUS_VIGENTE.md",
    "docs/pedagogia/HANDOFF.md": "../governanca/STATUS_VIGENTE.md",
    "docs/pedagogia/PROTOCOLO_ENTREGA_CONTINUIDADE.md":
        "../governanca/STATUS_VIGENTE.md",
}
PRESERVED = (
    "AGENTS.md", "settings.json", "rules/CORE.md", "guardrails/CORE.md",
    "memory/HANDOFF.md", "state/CURRENT.json", "EDITAL_UFMS_152_2026.md",
    "edital/INDEX.md",
)
MANUAL = (
    ("P0", "AUD-01", "Executor/broker de agentes não instalado: "
     "scripts e hooks locais não impõem START a clientes externos."),
    ("P0", "AUD-02", "Proteção administrativa e origem independente dos "
     "checks não homologadas; nenhum check pode ser promovido por esta rotina."),
    ("P1", "AUD-03", "scripts/api_write_guard.py continua fixo no PR #1 "
     "mesclado; exige revisão específica de segurança antes de generalizar."),
    ("P1", "AUD-07", "Tutor/Coach, comunicação e armazenamento individual "
     "não foram homologados pelo saneamento documental."),
    ("P1", "AUD-09", "Monitoramento de retificações requer executor, "
     "recibos e teste operacional próprios."),
    ("P2", "AUD-15", "Provas isoladas do PR #5 não equivalem a "
     "homologação integrada de C1–C27."),
)


class ReconciliationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReconciliationError(message)


def safe_file(root, relative, allow_missing=False):
    require(relative == STATUS_PATH or relative in TARGETS
            or relative in PRESERVED or relative == "ROADMAP.md",
            "Path outside allowed reconciliation scope")
    root = Path(root).resolve()
    candidate = root / relative
    require(not candidate.is_symlink()
            and candidate.parent.resolve().is_relative_to(root),
            "Symlink or directory escape")
    require(not candidate.exists() or candidate.is_file(),
            "Target is not a normal file")
    require(allow_missing or candidate.is_file(), "Required file missing: " + relative)
    return candidate


def read(root, relative):
    return safe_file(root, relative).read_text(encoding="utf-8")


def validate_local(root):
    for name in PRESERVED:
        require(read(root, name).strip(), "Empty mandatory file: " + name)
    settings = json.loads(read(root, "settings.json"))
    mandatory = settings.get("bootstrap", {}).get("mandatory")
    require(isinstance(mandatory, list) and len(mandatory) in (9, 10),
            "Unexpected bootstrap length")
    expected = list(PRESERVED)
    expected.insert(1, "rules/CORE.md") if False else None
    # Canonical list: do not derive policy from an uncontrolled README.
    nine = ["AGENTS.md", "settings.json", "rules/CORE.md",
            "guardrails/CORE.md", "memory/INDEX.md", "memory/HANDOFF.md",
            "state/CURRENT.json", "EDITAL_UFMS_152_2026.md",
            "edital/INDEX.md"]
    ten = nine[:1] + ["ROADMAP.md"] + nine[1:]
    require(mandatory == (ten if len(mandatory) == 10 else nine),
            "Bootstrap order differs from approved harness contract")
    has_roadmap = safe_file(root, "ROADMAP.md", allow_missing=True).exists()
    require(has_roadmap == (len(mandatory) == 10),
            "ROADMAP presence and settings mandatory list disagree")
    if has_roadmap:
        require(read(root, "ROADMAP.md").strip(), "ROADMAP empty")
    agent = read(root, "AGENTS.md")
    for name in mandatory:
        require(name in agent, "AGENTS lacks mandatory document: " + name)
    storage = settings.get("storage", {})
    require(storage.get("personal_results_writes_enabled") is False,
            "Personal-result write guard is disabled")
    require(storage.get("repository_must_be_private_for_personal_results") is True,
            "Private-storage prerequisite disabled")
    return {"mandatory_count": len(mandatory), "has_roadmap": has_roadmap}


def gh(path):
    try:
        r = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                           check=False, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReconciliationError("Authenticated GitHub read unavailable") from exc
    require(r.returncode == 0, "Authenticated GitHub read failed")
    try:
        return json.loads(r.stdout)
    except ValueError as exc:
        raise ReconciliationError("Malformed GitHub response") from exc


def remote_snapshot():
    repo = gh("repos/" + REPOSITORY)
    main = gh("repos/" + REPOSITORY + "/branches/main")
    require(repo.get("full_name") == REPOSITORY, "Repository identity mismatch")
    require(repo.get("visibility") in ("public", "private", "internal"),
            "Repository visibility not verified")
    require(isinstance(main.get("protected"), bool),
            "Branch protection summary not verified")
    main_sha = main.get("commit", {}).get("sha")
    require(isinstance(main_sha, str) and SHA40.fullmatch(main_sha),
            "Invalid main HEAD")
    prs = []
    for page in range(1, 21):
        batch = gh("repos/" + REPOSITORY +
                   "/pulls?state=all&per_page=100&page=" + str(page))
        require(isinstance(batch, list), "Incomplete PR listing")
        prs.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ReconciliationError("PR listing exceeds audited page limit")
    snapshot = {
        "repository": REPOSITORY, "main_sha": main_sha,
        "visibility": repo["visibility"], "main_protected": main["protected"],
        "pull_requests": [
            {"number": p.get("number"), "state": p.get("state"),
             "merged": p.get("merged_at") is not None,
             "draft": p.get("draft"), "head": p.get("head", {}).get("sha"),
             "base": p.get("base", {}).get("ref")}
            for p in prs
        ],
    }
    return validate_snapshot(snapshot)


def validate_snapshot(snapshot):
    require(isinstance(snapshot, dict)
            and snapshot.get("repository") == REPOSITORY,
            "Snapshot repository mismatch")
    require(isinstance(snapshot.get("main_sha"), str)
            and SHA40.fullmatch(snapshot["main_sha"]),
            "Snapshot missing verified main SHA")
    require(snapshot.get("visibility") in ("public", "private", "internal")
            and type(snapshot.get("main_protected")) is bool,
            "Snapshot missing visibility/protection summary")
    prs = snapshot.get("pull_requests")
    require(isinstance(prs, list), "Malformed PR collection")
    seen = set()
    for p in prs:
        require(isinstance(p, dict)
                and type(p.get("number")) is int and p["number"] > 0
                and p["number"] not in seen, "Invalid or duplicated PR number")
        seen.add(p["number"])
        require(p.get("state") in ("open", "closed")
                and type(p.get("merged")) is bool
                and type(p.get("draft")) is bool
                and isinstance(p.get("head"), str)
                and SHA40.fullmatch(p["head"])
                and isinstance(p.get("base"), str),
                "Invalid PR identity/status fields")
        require(not p["merged"] or p["state"] == "closed",
                "Merged PR cannot be open")
    return snapshot


def git_value(root, *args):
    try:
        p = subprocess.run(["git", "-C", str(root), *args],
                           capture_output=True, text=True, check=False, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReconciliationError("Git checkout unavailable") from exc
    require(p.returncode == 0, "Git checkout command failed")
    return p.stdout.strip()


def safe_branch(root, snapshot, expected_head):
    branch = git_value(root, "branch", "--show-current")
    sha = git_value(root, "rev-parse", "HEAD")
    require(branch.startswith(("audit/", "docs/", "fix/"))
            and branch not in ("main", "master"),
            "Writes permitted only on review branches")
    require(isinstance(expected_head, str)
            and SHA40.fullmatch(expected_head) and sha == expected_head,
            "HEAD lease mismatch")
    own = [p for p in snapshot["pull_requests"]
           if p["state"] == "open" and p["draft"]
           and p["head"] == sha]
    require(len(own) == 1, "No unique open draft PR at exact HEAD")
    require(git_value(root, "status", "--porcelain") == "",
            "Dirty checkout: refusing to overwrite pending changes")
    return branch, sha


def md(value):
    return str(value).replace("|", r"\|").replace("\r", "").replace("\n", " ")[:120]


def pr_status(p):
    if p["merged"]:
        return "MERGED"
    if p["state"] == "closed":
        return "CLOSED_UNMERGED"
    return "OPEN_DRAFT" if p["draft"] else "OPEN_READY"


def status_document(snapshot, context, branch, sha):
    lines = [
        "# Estado de governança — fotografia verificável",
        "",
        "**Aviso:** este arquivo é um snapshot de leitura autenticada. "
        "NÃO substitui consulta ao GitHub na hora de autorizar ações, "
        "não altera aprovações, nem representa revisão administrativa completa.",
        "",
        "- Repositório: " + REPOSITORY,
        "- Main (HEAD confirmado): " + snapshot["main_sha"],
        "- Revisão local: " + sha + " (" + branch + ")",
        "- Visibilidade: " + snapshot["visibility"],
        "- Campo main.protected: " + str(snapshot["main_protected"]).lower()
          + " (não comprova detalhes de rulesets/bypass)",
        "- Bootstrap desta revisão: " + str(context["mandatory_count"])
          + " documentos; ROADMAP incluído: "
          + str(context["has_roadmap"]).lower(),
        "- Personal-result writes: BLOQUEADO (invariante local verificada)",
        "",
        "## Pull requests observados",
        "",
        "| PR | Estado | HEAD | Base |",
        "|---|---|---|---|",
    ]
    for p in sorted(snapshot["pull_requests"], key=lambda p: p["number"]):
        lines.append("| #" + str(p["number"]) + " | " + pr_status(p)
                     + " | " + p["head"] + " | " + md(p["base"]) + " |")
    lines += [
        "", "## Regras de interpretação",
        "",
        "1. Um PR fechado sem merge continua HISTÓRICO, não normativo.",
        "2. Um PR draft não integra a main nem homologa funcionalidade.",
        "3. Aprovação de especificação não é aprovação de implementação, "
        "operação ou CI independente.",
        "4. Main protegida em resumo não comprova detalhes de política; "
        "readback administrativo permanece separado.",
        "5. Preferir decisões vigentes e checkpoints mais recentes do "
        "mesmo HEAD; blocos históricos abaixo não podem ser usados "
        "como instruções atuais sem revalidação.",
        "",
        "## Pendências que este saneador não pode decidir",
        "",
    ]
    for severity, code, issue in MANUAL:
        lines.append("- " + severity + " " + code + ": " + issue)
    lines += ["", "## Proveniência", "",
              "Fonte: GET autenticado via gh api de repositório, "
              "branch main e listagem paginada de PRs. "
              "Nenhum endpoint administrativo de proteção detalhada "
              "foi aceito como substituto da evidência ausente.", ""]
    return "\n".join(lines)


def upsert_header(content, banner):
    require(content.startswith("# "), "Unknown document format: first heading absent")
    block = START + "\n" + banner.rstrip() + "\n" + END
    n1, n2 = content.count(START), content.count(END)
    require((n1, n2) in ((0, 0), (1, 1)),
            "Malformed or duplicate managed-block markers")
    if n1:
        before, tail = content.split(START, 1)
        _, after = tail.split(END, 1)
        return before + block + after
    first, rest = content.split("\n", 1)
    return first + "\n\n" + block + "\n" + rest


def changes(root, snapshot, branch, sha):
    context = validate_local(root)
    validate_snapshot(snapshot)
    desired = {STATUS_PATH: status_document(snapshot, context, branch, sha)}
    merged = [p["number"] for p in snapshot["pull_requests"] if p["merged"]]
    closed = [p["number"] for p in snapshot["pull_requests"]
              if p["state"] == "closed" and not p["merged"]]
    banner = (
        "**Situação vigente (readback autenticado):** main "
        + snapshot["main_sha"] + "; PRs mesclados: "
        + (", ".join("#" + str(n) for n in sorted(merged)) or "nenhum")
        + "; fechados sem merge: "
        + (", ".join("#" + str(n) for n in sorted(closed)) or "nenhum")
        + ". O texto original a seguir é histórico quando mencionar "
        "PRs antigos; rever o estado atual antes de cada operação.")
    for path, link in TARGETS.items():
        current = read(root, path)
        if path == "memory/INDEX.md":
            intro = (
                "**Estado corrente recomendado para leitura seletiva:** "
                "[" + STATUS_PATH + "](" + link + "). "
                "Não substituir o bootstrap obrigatório nem o readback remoto.")
        elif path == "memory/DECISIONS.md":
            intro = banner + " Registros ADR anteriores não são apagados "
            intro += "nem automaticamente revogados por este script."
        elif path.startswith("docs/pedagogia/"):
            intro = banner + " PRs #1/#2 foram mesclados; nenhum motor "
            intro += "Tutor/Coach é homologado por essa mudança documental."
        else:
            intro = banner
        desired[path] = upsert_header(current, intro + " "
                                      + "Consultar [" + STATUS_PATH + "]("
                                      + link + ").")
    return {p: v for p, v in desired.items()
            if (safe_file(root, p, allow_missing=(p == STATUS_PATH)).read_text(
                encoding="utf-8") if (root / p).exists() else None) != v}


def write_atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.is_symlink(), "Symlink target detected")
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         newline="\n", dir=str(path.parent),
                                         prefix=".governance-", delete=False) as out:
            temp = Path(out.name)
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--mode", choices=("audit", "check", "apply"),
                        default="audit")
    parser.add_argument("--expected-head", default=None)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        snapshot = remote_snapshot()
        if args.mode == "apply":
            branch, sha = safe_branch(root, snapshot, args.expected_head)
        else:
            branch, sha = (git_value(root, "branch", "--show-current"),
                           git_value(root, "rev-parse", "HEAD"))
        delta = changes(root, snapshot, branch, sha)
        result = {"repository": REPOSITORY, "mode": args.mode,
                  "branch": branch, "head": sha,
                  "files_requiring_sync": sorted(delta),
                  "manual_unresolved": [{"severity": s, "id": code, "note": note}
                                        for s, code, note in MANUAL],
                  "mutated": False}
        if args.mode == "apply":
            for path, content in delta.items():
                write_atomic(safe_file(root, path, allow_missing=True), content)
            result["mutated"] = bool(delta)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        if args.mode == "check" and delta:
            return 2
        return 0
    except (ReconciliationError, OSError, UnicodeError, ValueError, KeyError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
