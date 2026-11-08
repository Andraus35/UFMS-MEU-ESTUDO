#!/usr/bin/env python3
"""Registra o recibo de um merge e a nova tarefa ativa nos quatro documentos de estado, de uma vez.

Atualiza `state/WORKFLOW.json`, `ROADMAP.md`, `memory/HANDOFF.md` e o STATUS reconciliado, para que o
`governance_sync_gate` não encontre divergência. Sem --apply, só mostra o que mudaria.

Uso: python scripts/record_merge_receipt.py --merged-pr 69 --merged-sha <40 hex> \
        --new-task RM-08 --new-scope <scope> --new-branch <branch> --new-pr 70 [--apply]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ("ROADMAP.md", "memory/HANDOFF.md", "docs/governanca/STATUS_BRANCHES_RECONCILIADO_20261105.md")
BLOCK_RE = re.compile(r"(<!-- GOVERNANCE-CHECKPOINT:START -->)(.*?)(<!-- GOVERNANCE-CHECKPOINT:END -->)", re.S)
MERGE_RE = re.compile(r"Último merge comprovado: PR #\d+; SHA [0-9a-f]{40}")
ACTIVE_RE = re.compile(r"Frente ativa: \*\*[^*\n]+\*\*; branch `[^`\n]*`; base main; fase \w+\.")


def plan(root: Path, a) -> dict:
    wf_path = root / "state/WORKFLOW.json"
    wf = json.loads(wf_path.read_text(encoding="utf-8"))
    if not re.fullmatch(r"[0-9a-f]{40}", a.merged_sha):
        raise ValueError("--merged-sha precisa ter 40 caracteres hexadecimais")
    if wf["active"].get("pr_number") != a.merged_pr:
        raise ValueError(f"o PR ativo no WORKFLOW é #{wf['active'].get('pr_number')}, não #{a.merged_pr}")
    merged_task = wf["active"]["task_id"]
    wf["last_merged"] = {"task_id": merged_task, "pr_number": a.merged_pr, "merge_commit_sha": a.merged_sha}
    wf["active"] = {"task_id": a.new_task, "scope": a.new_scope, "branch": a.new_branch,
                    "pr_number": a.new_pr, "base": "main", "phase": "review"}
    wf["notes"] = (f"PR #{a.merged_pr} integrado em main no merge commit {a.merged_sha}. Frente única ativa: {a.new_task} "
                   f"({a.new_scope}), branch {a.new_branch}, PR #{a.new_pr}. CURRENT E0, zero eventos/resultados; "
                   "PROGRESS intocado. Repositório público; persistência pessoal, credenciais e integrações externas "
                   "não autorizadas.")
    out = {"state/WORKFLOW.json": json.dumps(wf, ensure_ascii=False, indent=2) + "\n"}
    merge_line = f"Último merge comprovado: PR #{a.merged_pr}; SHA {a.merged_sha}"
    active_line = f"Frente ativa: **{a.new_task} / PR #{a.new_pr}**; branch `{a.new_branch}`; base main; fase review."
    for rel in DOCS:
        text = (root / rel).read_text(encoding="utf-8")
        blocks = BLOCK_RE.findall(text)
        if len(blocks) != 1:
            raise ValueError(f"{rel}: bloco GOVERNANCE-CHECKPOINT ausente ou duplicado")
        inner = blocks[0][1]
        if len(MERGE_RE.findall(inner)) != 1 or len(ACTIVE_RE.findall(inner)) != 1:
            raise ValueError(f"{rel}: linhas do checkpoint ausentes ou duplicadas")
        inner = ACTIVE_RE.sub(lambda _: active_line, MERGE_RE.sub(lambda _: merge_line, inner))
        text = BLOCK_RE.sub(lambda m: m.group(1) + inner + m.group(3), text, count=1)
        out[rel] = text
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--merged-pr", type=int, required=True)
    ap.add_argument("--merged-sha", required=True)
    ap.add_argument("--new-task", required=True)
    ap.add_argument("--new-scope", required=True)
    ap.add_argument("--new-branch", required=True)
    ap.add_argument("--new-pr", type=int, required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root)
    try:
        changes = plan(root, a)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        return 1
    for rel, text in changes.items():
        if a.apply:
            (root / rel).write_text(text, encoding="utf-8")
        print(("gravado: " if a.apply else "mudaria: ") + rel)
    if a.apply:
        print("Em seguida: python scripts/governance_sync_gate.py e python scripts/single_flow_gate.py --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
