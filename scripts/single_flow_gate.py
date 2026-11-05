"""Gate de fluxo unico: uma tarefa, uma branch de trabalho, um PR e merge antes da proxima.

Nao impede criar PRs pela API/GitHub; verifica o inventario remoto em CI.
Nao modifica GitHub e nao processa resultados de estudo.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from core import ROOT
except ModuleNotFoundError:
    from scripts.core import ROOT

VALID_PHASES = {"work", "review", "merge_ready"}
EXPECTED_POLICY = "single_branch_single_pr_single_merge"


def validate_local(root=ROOT):
    root = Path(root)
    data = json.loads((root / "state/WORKFLOW.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("policy") != EXPECTED_POLICY:
        raise ValueError("Política sequencial ausente ou alterada")
    rules = data.get("rules", {})
    required = {
        "max_open_pull_requests": 1,
        "max_active_work_branches": 1,
        "require_previous_merge_before_next": True,
        "allow_parallel_work": False,
        "allow_concurrent_prs": False,
        "require_head_ci": True,
        "require_negative_tests_for_high_medium": True,
        "allow_legacy_archived_branches_without_open_pr": True,
    }
    for key, expected in required.items():
        if type(rules.get(key)) is not type(expected) or rules.get(key) != expected:
            raise ValueError("Regra sequencial enfraquecida: " + key)
    active = data.get("active", {})
    task = active.get("task_id")
    if not isinstance(task, str) or not re.fullmatch(r"SIM-\\d{2}", task):
        raise ValueError("Tarefa ativa inválida")
    if not isinstance(active.get("pr_number"), int) or active["pr_number"] < 1:
        raise ValueError("PR ativo inválido")
    if active.get("phase") not in VALID_PHASES or active.get("base") != "main":
        raise ValueError("Fase/base inválida")
    branch = active.get("branch")
    if not isinstance(branch, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_./-]{2,150}", branch):
        raise ValueError("Branch ativa inválida")
    if branch == "main" or ".." in branch or "//" in branch or branch.endswith("/"):
        raise ValueError("Branch principal/reservada não é branch de trabalho")
    next_task = data.get("next_task_after_merge")
    if not isinstance(next_task, str) or not re.fullmatch(r"SIM-\\d{2}", next_task):
        raise ValueError("Próxima tarefa inválida")
    if next_task == task:
        raise ValueError("Próxima tarefa não pode repetir a ativa")
    roadmap = (root / "ROADMAP.md").read_text(encoding="utf-8")
    if ("| " + task + " |") not in roadmap or ("| " + next_task + " |") not in roadmap:
        raise ValueError("Tarefa atual ou próxima ausente no roadmap")
    deferred = data.get("deferred_pull_requests")
    if not isinstance(deferred, list) or not deferred:
        raise ValueError("Inventário de PRs legados ausente")
    seen_numbers = {active["pr_number"]}
    seen_branches = {branch}
    for item in deferred:
        if not isinstance(item, dict):
            raise ValueError("PR histórico inválido")
        number, old_branch, sha = item.get("number"), item.get("branch"), item.get("sha")
        if (not isinstance(number, int) or number < 1 or number in seen_numbers
                or not isinstance(old_branch, str) or not old_branch or old_branch in seen_branches
                or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha)
                or item.get("archived_without_merge") is not True
                or len(item.get("reason", "")) < 12):
            raise ValueError("PR legado inconsistente, duplicado ou sem SHA")
        seen_numbers.add(number)
        seen_branches.add(old_branch)
    for path in ("AGENTS.md", "ROADMAP.md", "memory/HANDOFF.md"):
        text = (root / path).read_text(encoding="utf-8")
        if "state/WORKFLOW.json" not in text:
            raise ValueError("Instrução de retomada sem estado único: " + path)
    return data


def validate_remote(data, open_prs, event_name, ref_name, head_ref=""):
    if not isinstance(open_prs, list):
        raise ValueError("Inventário remoto de PRs inválido")
    active = data["active"]
    if len(open_prs) > data["rules"]["max_open_pull_requests"]:
        raise ValueError("Múltiplos PRs abertos: interromper fluxo paralelo")
    if open_prs:
        only = open_prs[0]
        if only.get("number") != active["pr_number"]:
            raise ValueError("PR remoto diferente do único PR ativo")
        if only.get("head", {}).get("ref") != active["branch"]:
            raise ValueError("Branch remota diferente da branch ativa")
    elif ref_name != "main":
        raise ValueError("Branch ativa sem PR aberto: concluir criação do PR antes de continuar")
    if event_name == "pull_request" and (not open_prs or head_ref != active["branch"]):
        raise ValueError("PR concorrente ou branch do evento diferente da tarefa ativa")
    if event_name == "push" and ref_name not in ("main", active["branch"]):
        raise ValueError("Push em branch fora da única frente ativa")
    return True


def fetch_open_prs(repository, token=None):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository or ""):
        raise ValueError("GITHUB_REPOSITORY ausente ou inválido")
    request = Request(
        "https://api.github.com/repos/" + repository + "/pulls?state=open&per_page=100",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "UFMS-single-flow-gate",
            **({"Authorization": "Bearer " + token} if token else {}),
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            items = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ValueError("Inventário remoto indisponível; não assumir conformidade") from exc
    if not isinstance(items, list):
        raise ValueError("Resposta GitHub não é lista de PRs")
    if len(items) >= 100:
        raise ValueError("Inventário remoto excede limite de leitura segura")
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--remote", action="store_true")
    args = parser.parse_args()
    try:
        data = validate_local()
        if args.remote:
            prs = fetch_open_prs(os.getenv("GITHUB_REPOSITORY"), os.getenv("GITHUB_TOKEN"))
            validate_remote(data, prs, os.getenv("GITHUB_EVENT_NAME", ""),
                            os.getenv("GITHUB_REF_NAME", ""),
                            os.getenv("GITHUB_HEAD_REF", ""))
        print("OK: política de tarefa única; PR ativo #" + str(data["active"]["pr_number"]))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print("FALHA: fluxo sequencial: " + str(exc), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
