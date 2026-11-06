"""Deterministic cross-document governance checkpoint gate.

Checks that the active workflow, latest merged PR receipt, HANDOFF, ROADMAP,
and branch-status snapshot describe the same current engineering checkpoint.
This validates documentary consistency, not semantic comprehension by an LLM.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = "docs/governanca/STATUS_BRANCHES_RECONCILIADO_20261105.md"


def verify(root=ROOT):
    root = Path(root)
    workflow = json.loads((root / "state/WORKFLOW.json").read_text(encoding="utf-8"))
    active = workflow.get("active", {})
    merged = workflow.get("last_merged", {})
    task = active.get("task_id")
    pr = active.get("pr_number")
    branch = active.get("branch")
    next_task = workflow.get("next_task_after_merge")
    merge_pr = merged.get("pr_number")
    merge_sha = merged.get("merge_commit_sha")

    if not isinstance(task, str) or not re.fullmatch(r"(?:SIM-\\d{2}|RM-\\d{2}(?:-PREP)?)", task):
        raise ValueError("WORKFLOW sem task_id válido")
    if type(pr) is not int or pr < 1 or not isinstance(branch, str) or not branch:
        raise ValueError("WORKFLOW sem PR/branch ativa válidos")
    if type(merge_pr) is not int or merge_pr < 1 or merge_pr == pr:
        raise ValueError("WORKFLOW sem recibo distinto do último PR integrado")
    if not isinstance(merge_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", merge_sha):
        raise ValueError("WORKFLOW sem SHA válido do último merge")
    if not isinstance(next_task, str) or not next_task:
        raise ValueError("WORKFLOW sem próxima tarefa")

    handoff = (root / "memory/HANDOFF.md").read_text(encoding="utf-8").split("\\n---\\n", 1)[0]
    roadmap = (root / "ROADMAP.md").read_text(encoding="utf-8").splitlines()[:12]
    status_path = root / STATUS
    status = status_path.read_text(encoding="utf-8").splitlines()[:18]

    active_marker = f"**{task} / PR #{pr}**"
    branch_marker = f"`{branch}`"
    next_marker = (f"**Próxima tarefa: {next_task}**"
                   if next_task != "DONE" else "**Fila de simplificação concluída**")
    merge_marker = f"Último merge comprovado: PR #{merge_pr}"
    sha_marker = f"`{merge_sha}`"

    checks = {
        "HANDOFF": (handoff, (active_marker, branch_marker, next_marker, merge_marker, sha_marker)),
        "ROADMAP": ("\\n".join(roadmap), (f"{task} / PR #{pr}", branch_marker, merge_marker, sha_marker)),
        "STATUS": ("\\n".join(status), (f"{task} / PR #{pr}", branch_marker, merge_marker, sha_marker)),
    }
    for name, (text, markers) in checks.items():
        missing = [marker for marker in markers if marker not in text]
        if missing:
            raise ValueError(f"{name} desatualizado ou divergente: " + ", ".join(missing))
    return {"result": "PASS", "active_task": task, "active_pr": pr,
            "last_merged_pr": merge_pr, "next_task": next_task,
            "documents": ["state/WORKFLOW.json", "memory/HANDOFF.md",
                          "ROADMAP.md", STATUS]}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit("FALHA: governance sync gate: " + str(exc))
