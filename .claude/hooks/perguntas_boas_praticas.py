#!/usr/bin/env python3
"""Hook Stop determinístico: ao fim de cada rodada COM ENTREGA, exige AskUserQuestion que prepare a PRÓXIMA rodada.

Entrega = neste turno houve commit, push, criação/atualização/merge de PR ou publicação de arquivos. Sem entrega, não bloqueia
(conversa comum não gera pergunta). O motivo do bloqueio traz o estado real lido de `scripts/next_task.py` (ciclo e próximo item),
para as perguntas saírem da fila e não da memória. Falha ABERTA: qualquer erro permite encerrar. Trava contra laço:
`stop_hook_active` verdadeiro permite encerrar.
"""
import json
import os
import re
import subprocess
import sys

_ASK = re.compile(r'"name"\s*:\s*"AskUserQuestion"')
_GIT = re.compile(r"(?:^|[;&|(]|\n)\s*(?:cd\s+\S+\s*&&\s*)?git\s+(?:commit|push)\b")
_MCP_ENTREGA = frozenset({"create_pull_request", "merge_pull_request", "push_files", "create_or_update_file",
                          "update_pull_request", "delete_file"})


def _entrega_na_linha(linha):
    """True só se a linha tem um bloco tool_use real de entrega (não texto solto que cite 'git push')."""
    try:
        msg = (json.loads(linha).get("message") or {})
    except ValueError:
        return False
    conteudo = msg.get("content")
    if not isinstance(conteudo, list):
        return False
    for b in conteudo:
        if not isinstance(b, dict) or b.get("type") != "tool_use":
            continue
        nome = b.get("name") or ""
        if nome.startswith("mcp__github__") and nome[len("mcp__github__"):] in _MCP_ENTREGA:
            return True
        if nome == "Bash" and _GIT.search(str((b.get("input") or {}).get("command") or "")):
            return True
    return False


def _eh_pedido_do_usuario(entrada):
    if entrada.get("type") != "user" or entrada.get("isSidechain"):
        return False
    conteudo = (entrada.get("message") or {}).get("content")
    if isinstance(conteudo, str):
        return bool(conteudo.strip())
    if isinstance(conteudo, list):
        return any(isinstance(b, dict) and b.get("type") == "text" and (b.get("text") or "").strip() for b in conteudo)
    return False


def trecho_do_turno(caminho):
    linhas = open(caminho, encoding="utf-8").read().splitlines()
    ultimo = -1
    for i, linha in enumerate(linhas):
        try:
            if _eh_pedido_do_usuario(json.loads(linha)):
                ultimo = i
        except ValueError:
            continue
    return linhas[ultimo + 1:]


def estado_da_fila():
    """Resumo do estado real (ciclo e próximo item); vazio se não puder ler."""
    try:
        raiz = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        r = subprocess.run([sys.executable, "scripts/next_task.py"], cwd=raiz, capture_output=True, text=True, timeout=10)
        d = json.loads(r.stdout)
        ciclo, prox = d.get("ciclo", {}), (d.get("fila") or {}).get("proximo") or {}
        return ("Estado lido agora: ciclo da tarefa %s (PR #%s) em '%s'; próximo item da fila: %s — %s."
                % (ciclo.get("tarefa"), ciclo.get("pr"), ciclo.get("estado"), prox.get("id"), prox.get("titulo")))
    except Exception:
        return ""


def motivo():
    return (
        "Fim de rodada com entrega: sem esperar indicação, faça agora as perguntas automatizadas da PRÓXIMA rodada com "
        "AskUserQuestion (1 a 4), na sequência: (1) PENDÊNCIAS da entrega (CI, merge, decisões e atos do proprietário que "
        "bloqueiam o começo); (2) ROADMAP: o próximo item RM e o que o bloqueia; (3) FILA: o próximo item de "
        "state/WORKFLOW.json e as decisões de escopo, insumo e autorização de merge que ele exige. Um lote por vez: micro "
        "tarefas coesas da mesma frente no mesmo PR; se o próximo trabalho for de outra frente, o merge vem antes (AGENTS.md). Cada "
        "pergunta traz a opção recomendada de melhores práticas para o repositório e para o projeto primeiro, marcada "
        "'(Recomendado)', com justificativa; não repita o que já foi respondido. Ao receber as respostas, registre no HANDOFF "
        "(se o fluxo permitir) e comece a próxima rodada dentro do que foi autorizado. " + estado_da_fila()).strip()


def main():
    try:
        dados = json.load(sys.stdin)
        if dados.get("stop_hook_active"):
            return 0
        turno = trecho_do_turno(dados["transcript_path"])
        if any(_ASK.search(l) for l in turno):
            return 0
        if not any(_entrega_na_linha(l) for l in turno):
            return 0
    except Exception:
        return 0
    print(json.dumps({"decision": "block", "reason": motivo()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
