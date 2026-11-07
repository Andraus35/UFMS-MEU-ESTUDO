"""Deterministic governance checkpoint gate for active and post-merge states."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = "docs/governanca/STATUS_BRANCHES_RECONCILIADO_20261105.md"
TASK_RE = r"(?:SIM-\\d{2}|RM-\\d{2}(?:-PREP)?)"


def verify(root=ROOT):
    root = Path(root)
    workflow = json.loads((root / "state/WORKFLOW.json").read_text(encoding="utf-8"))
    active, merged = workflow.get("active"), workflow.get("last_merged", {})
    next_task = workflow.get("next_task_after_merge")
    if not isinstance(merged.get("pr_number"), int) or merged["pr_number"] < 1:
        raise ValueError("WORKFLOW sem PR do último merge")
    if not re.fullmatch(r"[0-9a-f]{40}", str(merged.get("merge_commit_sha", ""))):
        raise ValueError("WORKFLOW sem SHA válido do último merge")
    if not isinstance(merged.get("task_id"), str) or not re.fullmatch(TASK_RE, merged["task_id"]):
        raise ValueError("WORKFLOW sem tarefa válida no último merge")
    if not isinstance(next_task, str) or not re.fullmatch(r"(?:DONE|" + TASK_RE + r")", next_task):
        raise ValueError("WORKFLOW sem próxima tarefa válida")

    handoff = (root / "memory/HANDOFF.md").read_text(encoding="utf-8").split("\\n---\\n", 1)[0]
    roadmap_lines = (root / "ROADMAP.md").read_text(encoding="utf-8").splitlines()[:18]
    status_lines = (root / STATUS).read_text(encoding="utf-8").splitlines()[:24]
    docs = {"HANDOFF": handoff, "ROADMAP": "\\n".join(roadmap_lines),
            "STATUS": "\\n".join(status_lines)}
    merge_markers = (f"Último merge comprovado: PR #{merged['pr_number']}",
                     f"`{merged['merge_commit_sha']}`")
    for name, content in docs.items():
        missing = [x for x in merge_markers if x not in content]
        if missing:
            raise ValueError(f"{name} sem recibo do último merge: " + ", ".join(missing))
    next_marker = (f"**Próxima tarefa: {next_task}**" if next_task != "DONE"
                   else "**Fila de simplificação concluída**")
    for name in ("HANDOFF", "ROADMAP", "STATUS"):
        if next_marker not in docs[name]:
            raise ValueError(f"{name} diverge da próxima tarefa {next_task}")

    if active is None:
        for name, content in docs.items():
            if "**Nenhuma frente ativa**" not in content:
                raise ValueError(f"{name} não declara ausência de frente ativa")
        return {"result": "PASS", "state": "idle", "active_task": None,
                "active_pr": None, "last_merged_pr": merged["pr_number"],
                "next_task": next_task, "documents": list(docs)}
    if not isinstance(active, dict):
        raise ValueError("WORKFLOW.active deve ser objeto ou null")
    task, branch, pr, phase = (active.get("task_id"), active.get("branch"),
                               active.get("pr_number"), active.get("phase"))
    if not isinstance(task, str) or not re.fullmatch(TASK_RE, task):
        raise ValueError("WORKFLOW sem task_id válido")
    if not isinstance(branch, str) or not branch or branch == "main":
        raise ValueError("WORKFLOW sem branch ativa válida")
    if pr is not None and (type(pr) is not int or pr < 1):
        raise ValueError("WORKFLOW com PR ativo inválido")
    if phase not in ({"work"} if pr is None else {"review", "merge_ready", "work"}):
        raise ValueError("WORKFLOW com fase incompatível com PR")
    active_markers = (f"**{task}" + (f" / PR #{pr}**" if pr else " / PR pendente**"),
                      f"`{branch}`")
    for name, content in docs.items():
        missing = [x for x in active_markers if x not in content]
        if missing:
            raise ValueError(f"{name} diverge da frente ativa: " + ", ".join(missing))
    return {"result": "PASS", "state": "active" if pr else "prepared",
            "active_task": task, "active_pr": pr, "active_branch": branch,
            "last_merged_pr": merged["pr_number"], "next_task": next_task,
            "documents": list(docs)}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit("FALHA: governance sync gate: " + str(exc))
