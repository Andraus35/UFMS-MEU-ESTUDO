#!/usr/bin/env python3
"""Monta e valida, OFFLINE, a requisição para a Zapia criar uma issue ou um comentário neste repositório (S5-R12).

Não faz rede nem lê credencial: devolve {"method", "url", "json"} para o chamador enviar (por exemplo
`requests.post(url, json=req["json"])`). Existe porque a primeira escrita ad hoc da Zapia falhou com 422
("links/0/schema, nil is not an object"), sintoma de corpo que não chegou como OBJETO JSON.

Garante: repositório e caminhos fechados; corpo da requisição é dicionário com só os campos permitidos
(issue: title e body; comentário: body); título de uma linha; corpo dentro do limite; texto sem segredo nem
dado pessoal heurístico; divisão de corpos longos em comentários numerados. Não prova que a API aceite.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import agent_commands
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import agent_commands

REPO = "Andraus35/UFMS-MEU-ESTUDO"
API = "https://api.github.com"
MAX_TITLE = 200
MAX_BODY = 60000       # o GitHub aceita até 65 536 caracteres
CHUNK = 40000


def _check_text(text, label, *, limit):
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{label} deve ser texto não vazio")
    if len(text) > limit:
        raise ValueError(f"{label} excede {limit} caracteres")
    reason = agent_commands.scan_text(text)
    if reason:
        raise ValueError(f"{label} recusado pelo filtro de segurança ({reason})")


def build_issue(title: str, body: str, *, repo: str = REPO) -> dict:
    if repo != REPO:
        raise ValueError("repositório fora da lista permitida")
    _check_text(title, "título", limit=MAX_TITLE)
    if "\n" in title or "\r" in title:
        raise ValueError("título deve ter uma linha")
    _check_text(body, "corpo", limit=MAX_BODY)
    return {"method": "POST", "url": f"{API}/repos/{repo}/issues", "json": {"title": title, "body": body}}


def build_comment(issue_number: int, body: str, *, repo: str = REPO) -> dict:
    if repo != REPO:
        raise ValueError("repositório fora da lista permitida")
    if isinstance(issue_number, bool) or not isinstance(issue_number, int) or issue_number < 1:
        raise ValueError("número de issue inválido")
    _check_text(body, "corpo", limit=MAX_BODY)
    return {"method": "POST", "url": f"{API}/repos/{repo}/issues/{issue_number}/comments", "json": {"body": body}}


def split_body(body: str, *, chunk: int = CHUNK) -> list[str]:
    """Divide em partes com prefixo "parte i/N", cada uma com no máximo `chunk` caracteres (prefixo incluso)."""
    if not isinstance(body, str) or not body.strip():
        raise ValueError("corpo deve ser texto não vazio")
    if chunk < 100:
        raise ValueError("tamanho de parte pequeno demais")
    size = chunk - 30
    n = max(1, -(-len(body) // size))
    return [f"parte {i + 1}/{n}\n\n" + body[i * size:(i + 1) * size] for i in range(n)]


def build_comments(issue_number: int, body: str, *, repo: str = REPO, chunk: int = CHUNK) -> list[dict]:
    return [build_comment(issue_number, part, repo=repo) for part in split_body(body, chunk=chunk)]


def validate_request(request: dict) -> None:
    """Confere uma requisição já montada (por exemplo, antes de enviar): forma, URL e campos."""
    if not isinstance(request, dict) or set(request) != {"method", "url", "json"}:
        raise ValueError("requisição fora do formato")
    payload = request["json"]
    if not isinstance(payload, dict):  # a causa do 422 observado
        raise ValueError("o corpo da requisição deve ser um objeto JSON (dicionário), não texto nem lista")
    if request["method"] != "POST":
        raise ValueError("método fora da lista permitida")
    prefix = f"{API}/repos/{REPO}/issues"
    url = request["url"]
    if url == prefix:
        if set(payload) != {"title", "body"}:
            raise ValueError("issue aceita somente title e body")
        _check_text(payload["title"], "título", limit=MAX_TITLE)
        _check_text(payload["body"], "corpo", limit=MAX_BODY)
    elif url.startswith(prefix + "/") and url.endswith("/comments") and url[len(prefix) + 1:-9].isdigit():
        if set(payload) != {"body"}:
            raise ValueError("comentário aceita somente body")
        _check_text(payload["body"], "corpo", limit=MAX_BODY)
    else:
        raise ValueError("URL fora da lista permitida")
    json.dumps(payload)  # tem de ser serializável


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    issue = sub.add_parser("issue")
    issue.add_argument("--title", required=True)
    issue.add_argument("--body-file", required=True)
    comment = sub.add_parser("comment")
    comment.add_argument("--number", type=int, required=True)
    comment.add_argument("--body-file", required=True)
    args = parser.parse_args(argv)
    body = Path(args.body_file).read_text(encoding="utf-8")
    try:
        if args.cmd == "issue":
            result = [build_issue(args.title, body)]
        else:
            result = build_comments(args.number, body)
    except ValueError as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
