#!/usr/bin/env python3
"""Registra no repositório as respostas do proprietário às perguntas de fim de rodada (E53, opção B).

Grava/atualiza `memory/PERGUNTAS.json` com o estado lido agora (`scripts/next_task.py`) e as respostas, para o hook
`.claude/hooks/perguntas_boas_praticas.py` (que só lê) não repetir, em sessão nova, a pergunta de um estado já respondido.
O arquivo é público: recusa e-mail, sequência longa de dígitos e prefixos de token. Guarda as últimas 10 entradas.
Uso: python scripts/registrar_perguntas.py --resposta "pergunta: resposta" [--resposta ...] [--root DIR] [--estado TEXTO]
Não faz commit nem push: o motivo do hook manda comitar junto da próxima entrega.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

PREFIXO = "Estado lido agora: "
MAX_ENTRADAS, MAX_RESPOSTAS, MAX_CHARS = 10, 8, 300
_PROIBIDO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\d{9,}|ghp_|github_pat_|gho_|sk-[A-Za-z0-9]{8,}|https?://\S*[?&]token", re.I)


def estado_atual(raiz):
    r = subprocess.run([sys.executable, "scripts/next_task.py"], cwd=raiz, capture_output=True, text=True, timeout=10)
    d = json.loads(r.stdout)
    c, p = d.get("ciclo", {}), (d.get("fila") or {}).get("proximo") or {}
    return "%sciclo da tarefa %s (PR #%s) em '%s'; próximo item da fila: %s — %s." % (
        PREFIXO, c.get("tarefa"), c.get("pr"), c.get("estado"), p.get("id"), p.get("titulo"))


def validar(estado, respostas):
    if not estado.startswith(PREFIXO):
        raise ValueError("estado deve começar com %r" % PREFIXO)
    if not 1 <= len(respostas) <= MAX_RESPOSTAS:
        raise ValueError("informe de 1 a %d respostas" % MAX_RESPOSTAS)
    for t in respostas:
        if not t.strip() or len(t) > MAX_CHARS:
            raise ValueError("resposta vazia ou acima de %d caracteres" % MAX_CHARS)
        if _PROIBIDO.search(t):
            raise ValueError("resposta com dado pessoal ou credencial: o repositório é público")


def registrar(raiz, respostas, estado=None, agora=None):
    raiz = Path(raiz)
    estado = estado or estado_atual(raiz)
    validar(estado, respostas)
    arq = raiz / "memory" / "PERGUNTAS.json"
    try:
        entradas = json.loads(arq.read_text(encoding="utf-8")).get("entradas") or []
    except (OSError, ValueError):
        entradas = []
    entradas.append({"registrado_em": agora or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                     "estado": estado, "respostas": [t.strip() for t in respostas]})
    arq.parent.mkdir(parents=True, exist_ok=True)
    arq.write_text(json.dumps({"versao": 1, "entradas": entradas[-MAX_ENTRADAS:]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return arq


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--estado")
    ap.add_argument("--resposta", action="append", default=[])
    a = ap.parse_args(argv)
    try:
        print("registrado em", registrar(a.root, a.resposta, a.estado))
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        print("recusado:", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
