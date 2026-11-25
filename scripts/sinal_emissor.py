"""Emissor pelo fluxo (ZAPIA-EMISSOR, E34): abre a issue-campainha DEPOIS que a caixa promoveu comando.

Duas funções, as duas sem decisão de modelo:
- `--contar RESUMO.json`: conta os itens promovidos no resumo que o `command_box_runner` imprimiu e escreve `promovidos=N`
  (para `$GITHUB_OUTPUT`). Resumo ilegível, flag desligada, falhas de registro ou qualquer dúvida valem 0 (nada de campainha).
- `--emitir`: cria UMA issue em `entrada` com título FIXO `SINAL comando-promovido` e corpo VAZIO. Nenhum texto de comando,
  de fila, de nome de arquivo ou de resumo entra no título ou no corpo; o título não tem entrada variável.

Limites: a campainha só avisa que houve promoção; quem lê é o hook de Gmail, que vê remetente, assunto e hora (E30, E31). Não prova
entrega do e-mail nem que a Zapia reaja; o fluxo hoje não promove (flag falsa), então a prova ponta a ponta é do lote 3.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import promotion_runner as pr
except ModuleNotFoundError:  # uso como pacote
    from scripts import promotion_runner as pr

TITULO = "SINAL comando-promovido"
CORPO = ""
STATUS_PROMOVIDO = "PROMOVER"
MAX_RESUMO = 1_000_000


def contar(texto):
    """Itens com status `PROMOVER` num resumo com `estado` `PROCESSADO`, flag verdadeira e zero falhas de registro; senão 0."""
    try:
        resumo = json.loads(texto)
        if resumo["estado"] != "PROCESSADO" or resumo["flag"] is not True or resumo["falhas_de_registro"] != 0:
            return 0
        return sum(1 for i in resumo["itens"] if isinstance(i, dict) and i.get("status") == STATUS_PROMOVIDO)
    except Exception:
        return 0


def emitir(entrada_repo, token, transporte, flag):
    """Abre a issue-campainha. Sem a flag verdadeira não há rede nem token; devolve o estado (sem eco de texto externo)."""
    if flag is not True:
        return {"estado": "FLAG_DESLIGADA"}
    if not pr._REPO.fullmatch(entrada_repo or ""):
        return {"estado": "ERRO", "codigo": "ENTRADA_REPO_INVALIDO"}
    try:
        api = pr.GitHubApi(token, transporte, rotulo="entrada")
        status, _ = api.chamar("POST", f"/repos/{entrada_repo}/issues", {"title": TITULO, "body": CORPO})
    except Exception as erro:  # só a classe, nunca a mensagem
        return {"estado": "ERRO", "codigo": type(erro).__name__}
    return {"estado": "EMITIDO", "http": status}


def main(argv=None, transporte=None, ambiente=None):
    p = argparse.ArgumentParser(description="Emissor da campainha (E34).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--contar")
    g.add_argument("--emitir", action="store_true")
    p.add_argument("--entrada-repo")
    p.add_argument("--validador-dir", default=str(pr.ROOT))
    a = p.parse_args(argv)
    ambiente = os.environ if ambiente is None else ambiente
    if a.contar:
        arq = Path(a.contar)
        texto = arq.read_text(encoding="utf-8") if arq.is_file() and arq.stat().st_size <= MAX_RESUMO else ""
        print(f"promovidos={contar(texto)}")
        return 0
    flag = pr.ler_flag((Path(a.validador_dir) / "settings.json").read_text(encoding="utf-8"))
    resultado = emitir(a.entrada_repo, ambiente.get("GH_TOKEN", "") if flag else "", transporte or pr.transporte_urllib, flag)
    print(json.dumps(resultado))
    return 0 if resultado["estado"] in ("EMITIDO", "FLAG_DESLIGADA") else 1


if __name__ == "__main__":
    sys.exit(main())
