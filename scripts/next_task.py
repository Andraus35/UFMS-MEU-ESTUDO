#!/usr/bin/env python3
"""Qual é o estado do ciclo e qual é o próximo trabalho? Lê só o repositório (sem rede, sem token).

Substitui o prompt de retomada: qualquer sessão executa `python scripts/next_task.py` e obtém
(1) a situação real do PR registrado em `state/WORKFLOW.json`, deduzida do histórico Git;
(2) o próximo item da fila persistida `work_queue` do mesmo arquivo, com o que fazer.

Limite: a detecção de merge procura "(#N)" no assunto dos commits recentes de `main` (padrão do squash
do GitHub). É prova local forte, não substitui a confirmação autenticada no GitHub quando houver dúvida.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCEDURE = "docs/especificacoes/README.md"


def _git(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def cycle_status(root: Path, workflow: dict) -> dict:
    active = workflow["active"]
    pr = active.get("pr_number")
    base = {"pr": pr, "tarefa": active.get("task_id"), "branch": active.get("branch")}
    if pr is None:
        return {**base, "estado": "em_andamento", "acao": "Tarefa ativa sem PR: abrir o PR draft da branch registrada."}
    log = _git(root, "log", "--first-parent", "-n", "60", "--format=%H%x09%s")
    if log is None:
        return {**base, "estado": "indeterminado",
                "acao": "Histórico Git indisponível: confirmar no GitHub se o PR registrado foi mesclado."}
    for line in log.splitlines():
        sha, _, subject = line.partition("\t")
        if subject.rstrip().endswith(f"(#{pr})"):
            return {**base, "estado": "encerrado_recibo_pendente", "merge_sha": sha,
                    "acao": (f"O PR #{pr} já foi mesclado em main (merge {sha}). O WORKFLOW ainda o mostra como ativo "
                             "porque o recibo entra no primeiro commit da próxima tarefa: "
                             "`python scripts/record_merge_receipt.py` (veja --help).")}
    head = (_git(root, "rev-parse", "--abbrev-ref", "HEAD") or "").strip()
    return {**base, "estado": "em_andamento",
            "acao": (f"O PR #{pr} não aparece mesclado no histórico de main"
                     + (" (esta é a branch dele)" if head == active.get("branch") else "")
                     + ": continuar nele; confirmar no GitHub antes de assumir outro estado.")}


def queue_status(root: Path, workflow: dict) -> dict:
    queue = workflow.get("work_queue", [])
    ids = [i["id"] for i in queue]
    done = {i["id"] for i in queue if (root / i["deliverable"]).is_file()}
    pending = [i for i in queue if i["id"] not in done]
    nxt = next((i for i in pending if all(d in done for d in i.get("depends_on", []))), None)
    out = {"feitos": [i for i in ids if i in done], "pendentes": [i["id"] for i in pending]}
    if nxt is None:
        out["proximo"] = None
        out["acao"] = ("Fila concluída: definir com o proprietário o próximo item." if not pending
                       else "Itens pendentes com dependências não atendidas: verificar `depends_on`.")
        return out
    out["proximo"] = {
        "id": nxt["id"], "titulo": nxt["title"], "tarefa_roadmap": nxt["roadmap_task"],
        "entrega": nxt["deliverable"], "depende_de": nxt.get("depends_on", []),
        "bloqueio_do_proprietario": nxt.get("blocking_inputs", []),
        "insumos_que_melhoram": nxt.get("optional_inputs", []),
        "procedimento": PROCEDURE,
    }
    out["acao"] = (f"Executar o item {nxt['id']} pelo procedimento de `{PROCEDURE}` "
                   "(pesquisa obrigatória, especificação, gates, PR draft, CI) e parar no pedido de merge ao proprietário.")
    return out


def compute(root=ROOT) -> dict:
    root = Path(root)
    workflow = json.loads((root / "state/WORKFLOW.json").read_text(encoding="utf-8"))
    return {"ciclo": cycle_status(root, workflow), "fila": queue_status(root, workflow),
            "limite": "Leitura local; confirmar no GitHub autenticado em caso de dúvida (AGENTS.md, regra pós-merge)."}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args(argv)
    try:
        print(json.dumps(compute(Path(args.root)), ensure_ascii=False, indent=2))
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
