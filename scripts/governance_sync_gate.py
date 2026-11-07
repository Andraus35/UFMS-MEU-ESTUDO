"""Deterministic validator for the current governance checkpoint."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = "docs/governanca/STATUS_BRANCHES_RECONCILIADO_20261105.md"
TASK_RE = r"(?:SIM-\d{2}|RM-\d{2}(?:-(?:PREP|BASELINE))?)"
SHA_RE = re.compile(r"[0-9a-f]{40}")


def _read(root, path):
    return (root / path).read_text(encoding="utf-8")


def _current_block(text):
    """Only the explicitly delimited current checkpoint is authoritative."""
    start = text.find("<!-- GOVERNANCE-CHECKPOINT:START -->")
    end = text.find("<!-- GOVERNANCE-CHECKPOINT:END -->")
    if start < 0 or end < 0 or end <= start:
        raise ValueError("bloco de checkpoint vigente ausente ou malformado")
    return text[start:end]


def verify(root=ROOT):
    root = Path(root)
    workflow = json.loads(_read(root, "state/WORKFLOW.json"))
    active = workflow.get("active")
    merged = workflow.get("last_merged")
    next_task = workflow.get("next_task_after_merge")
    if not isinstance(merged, dict):
        raise ValueError("WORKFLOW sem recibo do último merge")
    number, merge_sha, merged_task = merged.get("pr_number"), merged.get("merge_commit_sha"), merged.get("task_id")
    if type(number) is not int or number < 1:
        raise ValueError("WORKFLOW sem PR do último merge")
    if not isinstance(merge_sha, str) or not SHA_RE.fullmatch(merge_sha):
        raise ValueError("WORKFLOW sem SHA válido do último merge")
    if not isinstance(merged_task, str) or not re.fullmatch(TASK_RE, merged_task):
        raise ValueError("WORKFLOW sem tarefa válida no último merge")
    if not isinstance(next_task, str) or not re.fullmatch(r"(?:DONE|" + TASK_RE + r")", next_task):
        raise ValueError("WORKFLOW sem próxima tarefa válida")

    if not isinstance(active, dict):
        raise ValueError("WORKFLOW.active deve preservar a referência histórica do último ciclo")
    task, branch, pr, phase = (active.get("task_id"), active.get("branch"),
                               active.get("pr_number"), active.get("phase"))
    if not isinstance(task, str) or not re.fullmatch(TASK_RE, task):
        raise ValueError("WORKFLOW sem task_id válido")
    if not isinstance(branch, str) or not branch or branch == "main" or ".." in branch:
        raise ValueError("WORKFLOW sem branch de ciclo válida")
    if pr is not None and (type(pr) is not int or pr < 1):
        raise ValueError("WORKFLOW com PR ativo inválido")
    if phase not in ({"work"} if pr is None else {"work", "review", "merge_ready"}):
        raise ValueError("WORKFLOW com fase incompatível")
    if pr is not None and pr == number:
        raise ValueError("WORKFLOW não pode marcar como ativo o PR já registrado como último merge")
    if pr is None and phase != "work":
        raise ValueError("Tarefa preparada sem PR deve estar em fase work")

    paths = {
        "HANDOFF": "memory/HANDOFF.md",
        "ROADMAP": "ROADMAP.md",
        "STATUS": STATUS,
    }
    docs = {name: _current_block(_read(root, path)) for name, path in paths.items()}
    next_marker = (f"**Próxima tarefa: {next_task}**" if next_task != "DONE"
                   else "**Fila de simplificação concluída**")
    for name, content in docs.items():
        required = [
            f"Último merge comprovado: PR #{number}",
            merge_sha,
            next_marker,
            f"**{task} / PR {'pendente' if pr is None else '#' + str(pr)}**",
            f"`{branch}`",
        ]
        for marker in required:
            if marker not in content:
                raise ValueError(f"{name} diverge do WORKFLOW: marcador ausente {marker}")
    return {
        "result": "PASS",
        "state": "prepared" if pr is None else "active",
        "active_task": task,
        "active_pr": pr,
        "active_branch": branch,
        "last_merged_pr": number,
        "last_merge_sha": merge_sha,
        "next_task": next_task,
        "documents": list(docs),
    }


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit("FALHA: governance sync gate: " + str(exc))
