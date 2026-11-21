"""Orientação do hook de passagem em branch PROTEGIDA ou DESTACADA com merge sem recibo (HOOKR2).

Achado de 21/11/2026: aos 50% o hook mandou "não comite na branch protegida" e, com o lote "finalizado", mandou só encerrar. Faltou dizer como
deixar o repositório pronto: o merge do PR registrado em `state/WORKFLOW.json` ficava SEM recibo, a P9 e o HANDOFF desatualizados, até o
proprietário pedir. Aqui: detectar o merge pendente (só leitura: git e WORKFLOW) e devolver a orientação (abrir a branch do próximo lote,
registrar o recibo, atualizar o HANDOFF). Falha aberta: qualquer dúvida devolve None e o comportamento anterior continua. Sem efeito externo.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def merge_pendente_de_recibo(cwd) -> dict | None:
    """{"pr": N, "sha": ...} se o PR ativo de `state/WORKFLOW.json` já aparece mesclado (`(#N)`) na linha principal do histórico; senão None."""
    try:
        raiz = (_git(cwd, "rev-parse", "--show-toplevel") or "").strip()
        if not raiz:
            return None
        ativo = json.loads((Path(raiz) / "state" / "WORKFLOW.json").read_text(encoding="utf-8")).get("active", {})
        pr = ativo.get("pr_number")
        if not isinstance(pr, int):
            return None
        log = _git(cwd, "log", "--first-parent", "-n", "60", "--format=%H%x09%s")
        for linha in (log or "").splitlines():
            sha, _, assunto = linha.partition("\t")
            if assunto.rstrip().endswith(f"(#{pr})"):
                return {"pr": pr, "sha": sha}
    except (OSError, ValueError, AttributeError):
        return None
    return None


def orientacao(merge: dict, caminho_do_prompt) -> str:
    return (
        f"[context-guard] Contexto acima do limite e prompt de start JÁ SELADO ({caminho_do_prompt}), mas esta é uma branch PROTEGIDA ou destacada e o PR "
        f"#{merge['pr']} já foi mesclado (merge {merge['sha'][:7]}) SEM recibo no estado do projeto. NÃO comite nesta branch. Para deixar o repositório "
        "pronto para a próxima sessão, sem pedir permissão: (1) confirme no GitHub que o PR foi mesclado e a CI; (2) crie a branch do próximo lote a partir "
        "de origin/main; (3) registre o recibo no primeiro commit com `python scripts/record_merge_receipt.py` (veja --help); (4) atualize o "
        "memory/HANDOFF.md (ponto de retomada, abaixo de 60 KiB) e o que o proprietário tiver confirmado; (5) rode os gates do projeto; (6) commit e push "
        "nessa branch e abra o PR draft; (7) sele o prompt de novo. Nunca force push, nunca merge, nunca arquivo de contrato sem aprovação já dada; "
        "se algum limite impedir, registre a pendência no prompt."
    )
