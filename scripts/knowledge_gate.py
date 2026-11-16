#!/usr/bin/env python3
"""Base de conhecimento obrigatória do Tutor e do Coach (RAG determinístico, somente leitura).

O manifesto `config/knowledge_base.json` lista os documentos que os agentes de estudo precisam ler antes de
prescrever caderno, criar material de revisão ou recomendar técnica. Cada entrada traz caminho, SHA-256, papéis e
momentos de uso. Este módulo:
  - valida o manifesto e confere bytes (hash, tamanho, sem symlink, dentro de docs/plataformas/);
  - devolve texto + hash por papel (`load_for_role`), usado pelo broker e pela rota de sessão;
  - `--check` falha se um documento mudou sem atualização do manifesto, ou se um agente deixou de referenciá-los.

Uso: python scripts/knowledge_gate.py --check [--role tutor|coach] [--root DIR]
     python scripts/knowledge_gate.py --update-hashes   (uso do proprietário/engenharia após editar um documento)

Prova bytes, ordem e presença; não prova que um LLM compreendeu os documentos nem que a plataforma segue igual.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "config/knowledge_base.json"
ALLOWED_DIR = "docs/plataformas/"
ROLES = frozenset({"tutor", "coach"})
MAX_BYTES = 64 * 1024
FIELDS = {"id", "path", "sha256", "roles", "plataforma", "aplica_antes_de", "evidencia"}
AGENT_PROFILES = {"tutor": "agents/TUTOR.md", "coach": "agents/COACH.md"}


class KnowledgeError(ValueError):
    """Base de conhecimento ausente, alterada ou malformada."""


def _read(root: Path, rel: str) -> bytes:
    p = root / rel
    if p.is_symlink() or not p.is_file():
        raise KnowledgeError(f"documento ausente ou redirecionado: {rel}")
    if not p.resolve().is_relative_to(root.resolve()):
        raise KnowledgeError(f"caminho fora do repositório: {rel}")
    raw = p.read_bytes()
    if len(raw) > MAX_BYTES:
        raise KnowledgeError(f"documento extenso demais para o contexto automático: {rel}")
    return raw


def load_manifest(root: Path) -> list[dict]:
    try:
        data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeError("manifesto ilegível: " + str(exc)) from exc
    entries = data.get("documentos")
    if not isinstance(entries, list) or not entries:
        raise KnowledgeError("manifesto sem documentos")
    seen_ids, seen_paths = set(), set()
    for e in entries:
        if set(e) != FIELDS:
            raise KnowledgeError(f"entrada com campos inválidos: {e.get('id')}")
        if e["id"] in seen_ids or e["path"] in seen_paths:
            raise KnowledgeError(f"entrada repetida: {e['id']}")
        seen_ids.add(e["id"]); seen_paths.add(e["path"])
        if not e["path"].startswith(ALLOWED_DIR) or ".." in e["path"]:
            raise KnowledgeError(f"{e['id']}: caminho fora de {ALLOWED_DIR}")
        if not set(e["roles"]) or not set(e["roles"]) <= ROLES:
            raise KnowledgeError(f"{e['id']}: papéis inválidos")
        if not e["aplica_antes_de"] or not all(isinstance(x, str) and x for x in e["aplica_antes_de"]):
            raise KnowledgeError(f"{e['id']}: aplica_antes_de vazio")
    return entries


def load_for_role(root: Path, role: str) -> list[dict]:
    """Textos verificados por hash, na ordem do manifesto, para o papel pedido."""
    if role not in ROLES:
        raise KnowledgeError("papel sem base de conhecimento: " + str(role))
    out = []
    for e in load_manifest(root):
        if role not in e["roles"]:
            continue
        raw = _read(root, e["path"])
        digest = hashlib.sha256(raw).hexdigest()
        if digest != e["sha256"]:
            raise KnowledgeError(f"{e['id']}: bytes divergem do manifesto (esperado {e['sha256'][:12]}, atual {digest[:12]})")
        out.append({"id": e["id"], "path": e["path"], "sha256": digest, "plataforma": e["plataforma"],
                    "aplica_antes_de": list(e["aplica_antes_de"]), "text": raw.decode("utf-8")})
    return out


def check(root: Path, roles=None) -> list[str]:
    errs = []
    try:
        entries = load_manifest(root)
        for role in sorted(roles or ROLES):
            docs = load_for_role(root, role)
            if not docs:
                errs.append(f"nenhum documento para o papel {role}")
    except KnowledgeError as exc:
        return [str(exc)]
    for role, rel in AGENT_PROFILES.items():
        if roles and role not in roles:
            continue
        profile = (root / rel).read_text(encoding="utf-8")
        for e in entries:
            if role in e["roles"] and e["path"] not in profile:
                errs.append(f"{rel} não referencia {e['path']}")
        if MANIFEST not in profile:
            errs.append(f"{rel} não referencia {MANIFEST}")
    return errs


def update_hashes(root: Path) -> None:
    path = root / MANIFEST
    data = json.loads(path.read_text(encoding="utf-8"))
    for e in data["documentos"]:
        e["sha256"] = hashlib.sha256(_read(root, e["path"])).hexdigest()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--update-hashes", action="store_true")
    ap.add_argument("--role", choices=sorted(ROLES))
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    if a.update_hashes:
        update_hashes(root)
        print("hashes atualizados")
        return 0
    errs = check(root, {a.role} if a.role else None)
    if errs:
        for e in errs:
            print("FALHA: " + e, file=sys.stderr)
        return 1
    docs = [d for r in ([a.role] if a.role else sorted(ROLES)) for d in load_for_role(root, r)]
    print("OK: base de conhecimento verificada (" + ", ".join(sorted({d["id"] for d in docs})) + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
