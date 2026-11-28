#!/usr/bin/env python3
"""Hook Stop determinístico: ao fim de cada rodada COM ENTREGA, exige AskUserQuestion que prepare a PRÓXIMA rodada.

Entrega = neste turno houve commit, push, criação/atualização/merge de PR ou publicação de arquivos. Sem entrega, não bloqueia
(conversa comum não gera pergunta). O motivo do bloqueio traz o estado real lido de `scripts/next_task.py` (ciclo e próximo item),
para as perguntas saírem da fila e não da memória. Falha ABERTA: qualquer erro permite encerrar. Trava contra laço:
`stop_hook_active` verdadeiro permite encerrar.

SÓ O QUE MUDOU (E13, decisão do proprietário de 21/11/2026): o hook continua SÓ LENDO (não grava estado). Lê o próprio transcript: se o
último "Estado lido agora: ..." que ele mesmo emitiu é IGUAL ao estado atual e já houve AskUserQuestion depois dele, a pergunta
daquele estado já foi feita e o hook NÃO bloqueia de novo. Se o estado mudou (ciclo, PR ou próximo item), bloqueia e mostra o que mudou.
Sem estado legível ou sem pergunta depois do último aviso, bloqueia como antes (na dúvida, pergunta).

PRIORIDADE DO HOOK DE PASSAGEM (E13, correção de 21/11/2026): se o hook geral `claude_context_guard` já foi acionado nesta sessão (contexto
acima do limite, `armed_at` no estado dele), este hook CEDE e não bloqueia: as perguntas de continuidade não prevalecem sobre a passagem para
a próxima sessão. Lote pendente também cede: nesse caso é o hook geral que obriga a verificar o fim do lote, concluir o ponto de corte e
persistir (commit e push) SEM pedir permissão. Leitura apenas do estado do guard (`~/.claude/context-guard/state/<sessão>.json`); estado
ausente ou ilegível: não cede.

PERSISTÊNCIA ENTRE SESSÕES (E53, opção B do proprietário de 28/11/2026): o hook continua SÓ LENDO, mas agora também lê
`memory/PERGUNTAS.json`, gravado no repositório por `scripts/registrar_perguntas.py` DEPOIS das respostas (o motivo do bloqueio manda
rodá-lo e comitar). Se o último estado registrado é IGUAL ao atual, não bloqueia, mesmo em sessão nova; se difere, mostra o que mudou.
Arquivo ausente, ilegível ou sem entradas: cai no transcript (E13) e, na dúvida, pergunta.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

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


_ESTADO = re.compile(r"(Estado lido agora: ciclo da tarefa [^\n]+)")  # só o aviso real do hook; uma citação solta de "Estado lido agora:" não vale (28/11/2026)


def _textos(entrada):
    c = (entrada.get("message") or {}).get("content")
    if isinstance(c, str):
        yield c
    elif isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and isinstance(b.get("text"), str):
                yield b["text"]


def estado_anterior(linhas):
    """(último estado que este hook emitiu, se houve AskUserQuestion depois dele) lidos do transcript inteiro; (None, False) se não houver."""
    ultimo, onde = None, -1
    for i, linha in enumerate(linhas):
        try:
            entrada = json.loads(linha)
        except ValueError:
            continue
        for t in _textos(entrada):
            for m in _ESTADO.finditer(t):
                ultimo, onde = m.group(1).strip(), i
    if ultimo is None:
        return None, False
    return ultimo, any(_ASK.search(l) for l in linhas[onde + 1:])


def cede_ao_hook_de_passagem(dados):
    """True se a sessão já passou do limite de contexto (hook geral). Só lê; qualquer dúvida: False."""
    try:
        sessao = re.sub(r"[^A-Za-z0-9_-]", "_", str(dados.get("session_id") or ""))[:80]
        if not sessao:
            return False
        base = Path(os.environ.get("CONTEXT_GUARD_HOME") or Path.home())
        st = json.loads((base / ".claude" / "context-guard" / "state" / (sessao + ".json")).read_text(encoding="utf-8"))
        return bool(st.get("armed_at"))
    except Exception:
        return False


def estado_persistido():
    """Último estado registrado no repositório por `registrar_perguntas.py` (só lê); None se ausente, ilegível ou vazio."""
    try:
        raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
        d = json.loads((raiz / "memory" / "PERGUNTAS.json").read_text(encoding="utf-8"))
        e = (d.get("entradas") or [])[-1]["estado"]
        return e.strip() if isinstance(e, str) and e.startswith("Estado lido agora: ") else None
    except Exception:
        return None


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


def motivo(estado=None, anterior=None):
    mudou = ("O que mudou desde a última pergunta: antes — %s; agora — %s. Pergunte só sobre o que mudou. "
             % (anterior.replace("Estado lido agora: ", ""), estado.replace("Estado lido agora: ", ""))) if anterior and estado else ""
    return mudou + (
        "Fim de rodada com entrega: sem esperar indicação, faça agora as perguntas automatizadas da PRÓXIMA rodada com "
        "AskUserQuestion (1 a 4), na sequência: (1) PENDÊNCIAS da entrega (CI, merge, decisões e atos do proprietário que "
        "bloqueiam o começo); (2) ROADMAP: o próximo item RM e o que o bloqueia; (3) FILA: o próximo item de "
        "state/WORKFLOW.json e as decisões de escopo, insumo e autorização de merge que ele exige. Um lote por vez: micro "
        "tarefas coesas da mesma frente no mesmo PR; se o próximo trabalho for de outra frente, o merge vem antes (AGENTS.md). Cada "
        "pergunta traz a opção recomendada de melhores práticas para o repositório e para o projeto primeiro, marcada "
        "'(Recomendado)', com justificativa; não repita o que já foi respondido. Ao receber as respostas, registre no HANDOFF "
        "(se o fluxo permitir) e comece a próxima rodada dentro do que foi autorizado. Depois das respostas, REGISTRE-AS no "
        "repositório: `python scripts/registrar_perguntas.py --resposta \"<pergunta: resposta>\"` (uma opção por resposta) e inclua "
        "memory/PERGUNTAS.json no próximo commit da branch de trabalho; sem isso a próxima sessão repete as perguntas. " + (estado if estado is not None else estado_da_fila())).strip()


def main():
    try:
        dados = json.load(sys.stdin)
        if dados.get("stop_hook_active"):
            return 0
        if cede_ao_hook_de_passagem(dados):
            return 0
        turno = trecho_do_turno(dados["transcript_path"])
        if any(_ASK.search(l) for l in turno):
            return 0
        if not any(_entrega_na_linha(l) for l in turno):
            return 0
        estado = estado_da_fila()
        anterior, perguntou = estado_anterior(open(dados["transcript_path"], encoding="utf-8").read().splitlines())
        persistido = estado_persistido()
        if persistido:  # o repositório vale mais que o transcript: ele atravessa sessões
            anterior, perguntou = persistido, True
        if estado and anterior == estado and perguntou:
            return 0  # mesmo estado, pergunta já feita: não repete
    except Exception:
        return 0
    print(json.dumps({"decision": "block", "reason": motivo(estado, anterior)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
