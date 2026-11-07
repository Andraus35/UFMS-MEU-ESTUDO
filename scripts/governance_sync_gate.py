"""Deterministic governance checkpoint gate for prepared and active states."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = "docs/governanca/STATUS_BRANCHES_RECONCILIADO_20261105.md"
TASK_RE = r"(?:SIM-\d{2}|RM-\d{2}(?:-PREP)?)"


def verify(root=ROOT):
    root = Path(root)
    workflow = json.loads((root / "state/WORKFLOW.json").read_text(encoding="utf-8"))
    active = workflow.get("active")
    merged = workflow.get("last_merged", {})
    next_task = workflow.get("next_task_after_merge")
    if type(merged.get("pr_number")) is not int or merged["pr_number"] < 1:
        raise ValueError("WORKFLOW sem PR do último merge")
    merge_sha = merged.get("merge_commit_sha")
    if not isinstance(merge_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", merge_sha):
        raise ValueError("WORKFLOW sem SHA válido do último merge")
    if not isinstance(merged.get("task_id"), str) or not re.fullmatch(TASK_RE, merged["task_id"]):
        raise ValueError("WORKFLOW sem tarefa válida no último merge")
    if not isinstance(next_task, str) or not re.fullmatch(r"(?:DONE|" + TASK_RE + r")", next_task):
        raise ValueError("WORKFLOW sem próxima tarefa válida")

    handoff = (root / "memory/HANDOFF.md").read_text(encoding="utf-8").split("\n---\n", 1)[0]
    roadmap = "\n".join((root / "ROADMAP.md").read_text(encoding="utf-8").splitlines()[:18])
    status = "\n".join((root / STATUS).read_text(encoding="utf-8").splitlines()[:24])
    docs = {"HANDOFF": handoff, "ROADMAP": roadmap, "STATUS": status}
    for name, text in docs.items():
        if f"Último merge comprovado: PR #{merged['pr_number']}" not in text or merge_sha not in text:
            raise ValueError(f"{name} sem recibo do último merge")
        marker = f"**Próxima tarefa: {next_task}**" if next_task != "DONE" else "**Fila de simplificação concluída**"
        if marker not in text:
            raise ValueError(f"{name} diverge da próxima tarefa {next_task}")

    if not isinstance(active, dict):
        raise ValueError("WORKFLOW.active deve representar tarefa preparada ou ativa")
    task, branch, pr, phase = active.get("task_id"), active.get("branch"), active.get("pr_number"), active.get("phase")
    if not isinstance(task, str) or not re.fullmatch(TASK_RE, task):
        raise ValueError("WORKFLOW sem task_id válido")
    if not isinstance(branch, str) or not branch or branch == "main" or ".." in branch:
        raise ValueError("WORKFLOW sem branch ativa válida")
    if pr is not None and (type(pr) is not int or pr < 1):
        raise ValueError("WORKFLOW com PR ativo inválido")
    if phase != ("work" if pr is None else phase) or (pr is not None and phase not in {"work", "review", "merge_ready"}):
        raise ValueError("WORKFLOW com fase incompatível")
    active_marker = f"**{task} / PR pendente**" if pr is None else f"**{task} / PR #{pr}**"
    for name, text in docs.items():
        if active_marker not in text or f"`{branch}`" not in text:
            raise ValueError(f"{name} diverge da frente ativa")
    return {"result": "PASS", "state": "prepared" if pr is None else "active",
            "active_task": task, "active_pr": pr, "active_branch": branch,
            "last_merged_pr": merged["pr_number"], "next_task": next_task,
            "documents": list(docs)}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit("FALHA: governance sync gate: " + str(exc))
