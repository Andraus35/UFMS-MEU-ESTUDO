#!/usr/bin/env python3
"""Conduz uma sessão pelos documentos de governança e persistência, em ordem fixa e sem prompt.

Lê `config/session_routes.json` (dado) e, para o tipo de sessão pedido, devolve a rota: cada documento a ler
com seu SHA-256 atual, o que consultar sob demanda, as verificações a executar e as condições de parada.
Com `--run`, executa as verificações (lista fechada de scripts, sem shell) na ordem e para na primeira falha.

Uso: python scripts/session_route.py --intent {study,engineering,write,governance,persistence} [--run] [--expect SHA]

Prova bytes e ordem das verificações executadas; não prova que um LLM compreendeu os documentos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES_FILE = "config/session_routes.json"
INTENTS = ("study", "engineering", "write", "governance", "persistence")
# Só scripts do próprio repositório, com flags simples; nenhum shell.
COMMAND_RE = re.compile(r"^python (?:scripts|hooks)/[a-z_0-9]+\.py(?: --[a-z-]+(?: [A-Za-z0-9_.-]+)?)*$")
TYPES = {"ler", "consultar_se", "executar", "parar_se", "aviso_se", "manual"}
SITUACOES = {"bloqueada", "requer_aprovacao_humana"}
CONDITIONS = {"gravacao_pessoal_bloqueada", "sempre"}


def load_routes(root: Path) -> dict:
    return json.loads((root / ROUTES_FILE).read_text(encoding="utf-8"))["rotas"]


def _sha(root: Path, rel: str) -> str:
    return hashlib.sha256((root / rel).read_bytes()).hexdigest()


def _condition(root: Path, name: str) -> bool:
    if name == "sempre":
        return True
    if name == "gravacao_pessoal_bloqueada":
        settings = json.loads((root / "settings.json").read_text(encoding="utf-8"))
        return settings.get("storage", {}).get("personal_results_writes_enabled") is not True
    raise ValueError("condição desconhecida: " + name)


def build(root: Path, intent: str) -> dict:
    routes = load_routes(root)
    if intent not in routes:
        raise ValueError("tipo de sessão desconhecido: " + intent)
    steps, blocked = [], None
    for st in routes[intent]["etapas"]:
        kind = st["tipo"]
        if kind not in TYPES:
            raise ValueError(f"etapa {st.get('id')}: tipo inválido")
        item = {"id": st["id"], "tipo": kind}
        if kind in ("ler", "consultar_se"):
            item.update(arquivo=st["arquivo"], sha256=_sha(root, st["arquivo"]))
            item["porque" if kind == "ler" else "quando"] = st.get("porque") or st.get("quando")
        elif kind == "executar":
            if not COMMAND_RE.fullmatch(st["comando"]):
                raise ValueError(f"etapa {st['id']}: comando fora da lista permitida")
            item["comando"] = st["comando"]
        elif kind in ("parar_se", "aviso_se"):
            hit = _condition(root, st["condicao"])
            item.update(condicao=st["condicao"], acionada=hit, mensagem=st["mensagem"])
            if kind == "parar_se":
                sit = st.get("situacao", "bloqueada")
                if sit not in SITUACOES:
                    raise ValueError(f"etapa {st['id']}: situação inválida")
                item["situacao"] = sit
                if hit and blocked is None:
                    blocked = {"etapa": st["id"], "situacao": sit, "motivo": st["mensagem"]}
        else:
            item["texto"] = st["texto"]
        steps.append(item)
    core = {"intent": intent, "etapas": [{k: v for k, v in s.items() if k != "acionada"} for s in steps]}
    route_hash = hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return {"intent": intent, "descricao": routes[intent]["descricao"], "situacao": blocked["situacao"] if blocked else "pronta",
            "bloqueio": blocked, "route_sha256": route_hash, "etapas": steps}


def run_checks(root: Path, route: dict) -> list[dict]:
    results = []
    for st in route["etapas"]:
        if st["tipo"] == "parar_se" and st.get("acionada"):  # aviso_se não interrompe
            break
        if st["tipo"] != "executar":
            continue
        proc = subprocess.run(shlex.split(st["comando"]), cwd=root, capture_output=True, text=True, timeout=300)
        ok = proc.returncode == 0
        tail = (proc.stdout if ok else (proc.stderr or proc.stdout)).strip().splitlines()[-1:] or [""]
        results.append({"id": st["id"], "comando": st["comando"], "ok": ok, "saida": tail[0][:200]})
        if not ok:
            break
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--intent", required=True, choices=INTENTS)
    ap.add_argument("--run", action="store_true", help="executa as verificações da rota na ordem")
    ap.add_argument("--expect", help="SHA da rota citado antes; falha se os documentos mudaram")
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    try:
        route = build(root, a.intent)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        return 1
    if a.expect and a.expect != route["route_sha256"]:
        print(f"FALHA: a rota mudou desde {a.expect[:12]} (atual {route['route_sha256'][:12]}): reler os documentos", file=sys.stderr)
        return 1
    if a.run:
        route["verificacoes"] = run_checks(root, route)
        if not all(v["ok"] for v in route["verificacoes"]):
            print(json.dumps(route, ensure_ascii=False, indent=2))
            return 1
    print(json.dumps(route, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
