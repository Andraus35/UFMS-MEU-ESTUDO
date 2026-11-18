#!/usr/bin/env python3
"""Hook Stop determinístico de ENTREGA FINAL, ativo até 20/11/2026 (decisão do proprietário, 18/11/2026).

Ao fim de cada rodada COM ENTREGA (mesma detecção do hook de perguntas: commit, push ou operação de PR neste turno), confere se o
que foi entregue está de pé: árvore limpa, HEAD enviado ao remoto, gates do repositório e a suíte de testes completa. Se algo estiver
vermelho, BLOQUEIA o fim da rodada e diz o que falhou; se estiver tudo verde, deixa encerrar e mostra a contagem regressiva até
20/11 e os desbloqueios pendentes do proprietário (`owner_priorities`). Depois de 20/11 não faz nada.

Só LÊ e AVISA: não faz merge, não grava, não usa rede nem credencial, não altera estado. Falha ABERTA: erro interno, comando ausente
ou tempo esgotado permitem encerrar (com aviso). Trava contra laço: se o hook já bloqueou nesta rodada (`stop_hook_active`), roda a
conferência de novo mas, se ainda estiver vermelha, deixa encerrar com aviso em vez de bloquear para sempre.

Limites: prova o que o repositório mostra (testes e gates locais, HEAD local igual ao remoto conhecido); NÃO prova a CI do GitHub
no head (isso exige leitura autenticada) nem a eficácia pedagógica; depende de `python3` e de `git` no ambiente.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

PRAZO = date(2026, 11, 20)
FUSO = timezone(timedelta(hours=-4))  # horário de Mato Grosso do Sul
ORCAMENTO_S = 165  # o hook inteiro cabe no timeout do settings.json (180 s)
TAIL = 500

# (rótulo, argv) em ordem fixa; a suíte completa vem por último porque é a mais lenta.
CHECAGENS = (
    ("coesão documental", ["python3", "scripts/doc_cohesion.py", "--check"]),
    ("sincronia da governança", ["python3", "scripts/governance_sync_gate.py"]),
    ("tarefa única", ["python3", "scripts/single_flow_gate.py", "--check"]),
    ("roadmap", ["python3", "scripts/roadmap_gate.py", "--check"]),
    ("PRODUCT.md", ["python3", "scripts/product_gate.py", "--check"]),
    ("estrutura e dados", ["python3", "scripts/validate.py"]),
    ("suíte de testes", ["python3", "-m", "unittest", "discover", "-s", "tests", "-q"]),
)


def _carrega_hook_de_perguntas():
    caminho = Path(__file__).with_name("perguntas_boas_praticas.py")
    spec = importlib.util.spec_from_file_location("perguntas_boas_praticas", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def rodar(argv, cwd, timeout):
    """Executa um comando e devolve (código, saída). Código None = não executou (tempo esgotado ou comando ausente)."""
    try:
        r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=max(1, int(timeout)))
        return r.returncode, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired:
        return None, "tempo esgotado"
    except OSError as erro:
        return None, "não executou: %s" % type(erro).__name__


def dias_restantes(hoje):
    return (PRAZO - hoje).days


def dentro_do_prazo(hoje):
    return hoje <= PRAZO


def _cauda(texto):
    texto = (texto or "").strip()
    return texto[-TAIL:] if len(texto) > TAIL else texto


def conferir_git(raiz, executar):
    """Árvore limpa e HEAD igual ao do remoto de acompanhamento. Devolve lista de problemas (vazia se está tudo certo)."""
    problemas = []
    rc, saida = executar(["git", "status", "--porcelain"], raiz, 20)
    if rc is None:
        return ["não consegui ler o estado do git (%s)" % saida]
    if saida.strip():
        n = len([l for l in saida.splitlines() if l.strip()])
        problemas.append("há %d arquivo(s) com alteração não commitada" % n)
    rc1, local = executar(["git", "rev-parse", "HEAD"], raiz, 20)
    rc2, remoto = executar(["git", "rev-parse", "@{u}"], raiz, 20)
    if rc1 == 0 and rc2 == 0:
        if local.strip() != remoto.strip():
            problemas.append("o HEAD local não é o que está no remoto (falta enviar ou há commit novo)")
    elif rc2 not in (None, 0):
        problemas.append("a branch não tem remoto de acompanhamento (nada foi enviado)")
    return problemas


def conferir_checagens(raiz, executar, relogio=time.monotonic, orcamento=ORCAMENTO_S, checagens=CHECAGENS):
    """Roda os gates e a suíte. Devolve (falhas, nao_concluidas): falha = código diferente de zero; não concluída = sem veredito."""
    falhas, nao_concluidas = [], []
    inicio = relogio()
    for rotulo, argv in checagens:
        restante = orcamento - (relogio() - inicio)
        if restante < 5:
            nao_concluidas.append((rotulo, "sem tempo restante"))
            continue
        rc, saida = executar(argv, raiz, restante)
        if rc is None:
            nao_concluidas.append((rotulo, saida))
        elif rc != 0:
            falhas.append((rotulo, _cauda(saida)))
    return falhas, nao_concluidas


def pendencias_do_proprietario(raiz, executar):
    """Lista curta dos desbloqueios pendentes (state/WORKFLOW.json, owner_priorities), pelo next_task.py; vazia se não puder ler."""
    rc, saida = executar(["python3", "scripts/next_task.py"], raiz, 15)
    if rc != 0:
        return []
    try:
        itens = json.loads(saida).get("desbloqueios_do_proprietario") or []
        return ["%s %s" % (i.get("id"), (i.get("ato") or "")[:90]) for i in itens[:6]]
    except (ValueError, AttributeError):
        return []


def contagem(hoje):
    d = dias_restantes(hoje)
    if d > 1:
        return "faltam %d dias para 20/11" % d
    if d == 1:
        return "falta 1 dia para 20/11"
    return "hoje é 20/11, o prazo"


def mensagem_verde(hoje, pendencias, nao_concluidas, aviso_laco=False):
    partes = ["Entrega final: git limpo e enviado, gates e testes verdes (%s)." % contagem(hoje)]
    if nao_concluidas:
        partes.append("Não consegui concluir: " + "; ".join("%s (%s)" % x for x in nao_concluidas) + ". Rode à mão.")
    partes.append("Isto NÃO prova a CI do GitHub no head (confira as duas validate) nem o merge, que é seu.")
    if pendencias:
        partes.append("Desbloqueios seus pendentes: " + " | ".join(pendencias))
    return " ".join(partes)


def motivo_vermelho(hoje, problemas_git, falhas, nao_concluidas, pendencias):
    linhas = ["Entrega final NÃO está de pé (%s). Corrija antes de encerrar a rodada:" % contagem(hoje)]
    linhas += ["- git: " + p for p in problemas_git]
    for rotulo, cauda in falhas:
        linhas.append("- %s falhou: %s" % (rotulo, cauda.replace("\n", " / ") if cauda else "sem saída"))
    if nao_concluidas:
        linhas.append("- sem veredito: " + "; ".join("%s (%s)" % x for x in nao_concluidas))
    linhas.append("Rode a suíte e os gates, commit e push só com tudo verde; depois peça a reconfirmação do merge com PR e head exato.")
    if pendencias:
        linhas.append("Desbloqueios seus pendentes: " + " | ".join(pendencias))
    return "\n".join(linhas)


def decidir(dados, hoje, raiz, executar=rodar, perguntas=None, relogio=time.monotonic, checagens=CHECAGENS):
    """Núcleo puro: devolve o dicionário de saída do hook ({} para permitir sem mensagem)."""
    if not dentro_do_prazo(hoje):
        return {}
    perguntas = perguntas or _carrega_hook_de_perguntas()
    turno = perguntas.trecho_do_turno(dados["transcript_path"])
    if not any(perguntas._entrega_na_linha(l) for l in turno):
        return {}  # conversa comum e leitura não disparam
    ativo = bool(dados.get("stop_hook_active"))
    problemas_git = conferir_git(raiz, executar)
    falhas, nao_concluidas = conferir_checagens(raiz, executar, relogio=relogio, checagens=checagens)
    pendencias = pendencias_do_proprietario(raiz, executar)
    if problemas_git or falhas:
        if ativo:  # trava contra laço: já bloqueou uma vez nesta rodada
            return {"systemMessage": "Entrega final AINDA vermelha, mas deixo encerrar para não travar a sessão. "
                    + motivo_vermelho(hoje, problemas_git, falhas, nao_concluidas, pendencias).replace("\n", " ")}
        return {"decision": "block", "reason": motivo_vermelho(hoje, problemas_git, falhas, nao_concluidas, pendencias)}
    return {"systemMessage": mensagem_verde(hoje, pendencias, nao_concluidas)}


def main():
    try:
        dados = json.load(sys.stdin)
        raiz = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        hoje = datetime.now(FUSO).date()
        saida = decidir(dados, hoje, raiz)
    except Exception:
        return 0  # falha aberta
    if saida:
        print(json.dumps(saida, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
