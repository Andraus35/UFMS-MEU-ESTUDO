#!/usr/bin/env python3
"""Valida, OFFLINE, o registro de proveniência de um material de revisão (D-23, PR-005, S2-R10).

Papéis (D-23): o Tutor é o autor editorial (escreve o prompt e verifica); o Gemini Notebook só gera RASCUNHO
sob o prompt do Tutor; a Zapia só transporta, por comando assinado; nada de estudo é produzido pelo Claude de
engenharia. O registro guarda só metadados, nunca o texto do material.

Estados: `rascunho` (ainda não confere), `verificado` (o Tutor conferiu fonte e trecho) e `entregue` (ao estudante).
Só `verificado` e `entregue` exigem verificador e fontes com localizador.

Limites: validador textual; não prova quem escreveu de fato (E-04), não obriga agentes externos e não guarda
registros reais (repositório público). Uso: `python scripts/review_provenance.py --file registro.json`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import agent_commands
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import agent_commands

SCHEMA_VERSION = "1.0"
STATUSES = ("rascunho", "verificado", "entregue")
GENERATORS = ("gemini_notebook", "tutor")
TRANSPORTS = ("zapia", "direto")
ALLOWED_KEYS = {"schema_version", "topic", "date", "status", "prompt_author", "generator", "transport",
                "command_id", "verified_by", "sources"}
FORBIDDEN_KEYS = {"texto", "conteudo", "conteúdo", "content", "body", "resposta", "nota", "text", "material"}
COMMAND_ID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
MAX_TOPIC = 120
MAX_REF = 160
MAX_LOCATOR = 80
MAX_SOURCES = 20


def _is_text(value, limit):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit and "\n" not in value


def check(record) -> list[str]:
    """Devolve a lista de códigos de recusa (vazia se o registro é válido)."""
    if not isinstance(record, dict):
        return ["REGISTRO_FORA_DO_FORMATO"]
    errors: list[str] = []
    keys = {k for k in record if isinstance(k, str)}
    if keys & {k for k in FORBIDDEN_KEYS}:
        errors.append("TEXTO_INTEGRAL_PROIBIDO")
    if any(not isinstance(k, str) for k in record) or (keys - ALLOWED_KEYS - FORBIDDEN_KEYS):
        errors.append("CAMPO_DESCONHECIDO")
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("VERSAO_INVALIDA")
    if not _is_text(record.get("topic"), MAX_TOPIC):
        errors.append("ASSUNTO_INVALIDO")
    try:
        date.fromisoformat(record.get("date"))
    except (TypeError, ValueError):
        errors.append("DATA_INVALIDA")
    status = record.get("status")
    if status not in STATUSES:
        errors.append("ESTADO_INVALIDO")
    if record.get("prompt_author") != "tutor":
        errors.append("AUTOR_DO_PROMPT_NAO_E_O_TUTOR")
    if record.get("generator") not in GENERATORS:
        errors.append("GERADOR_INVALIDO")
    transport = record.get("transport")
    if transport not in TRANSPORTS:
        errors.append("TRANSPORTE_INVALIDO")
    elif transport == "zapia" and not (isinstance(record.get("command_id"), str) and COMMAND_ID.match(record["command_id"])):
        errors.append("TRANSPORTE_SEM_COMANDO")
    if status in ("verificado", "entregue"):
        if record.get("verified_by") != "tutor":
            errors.append("SEM_VERIFICACAO_DO_TUTOR")
        sources = record.get("sources")
        valid_sources = (isinstance(sources, list) and 0 < len(sources) <= MAX_SOURCES and all(
            isinstance(s, dict) and set(s) == {"ref", "locator"} and _is_text(s["ref"], MAX_REF)
            and _is_text(s["locator"], MAX_LOCATOR) for s in sources))
        if not valid_sources:
            errors.append("FONTE_SEM_LOCALIZADOR")
    elif record.get("verified_by") not in (None, "tutor"):
        errors.append("VERIFICADOR_INVALIDO")
    if not errors:
        texts = [record["topic"], record.get("command_id") or ""]
        texts += [part for s in record.get("sources") or [] for part in (s["ref"], s["locator"])]
        for text in texts:
            reason = agent_commands.scan_text(text)
            if reason:
                errors.append("DADO_SENSIVEL:" + reason)
                break
    return errors


def validate(record) -> None:
    errors = check(record)
    if errors:
        raise ValueError(", ".join(errors))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", required=True)
    args = parser.parse_args(argv)
    try:
        record = json.loads(Path(args.file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        return 1
    errors = check(record)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
