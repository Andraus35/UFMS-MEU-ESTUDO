"""Contrato determinístico local de bootstrap e interfaces de hooks.

Verifica bytes e interfaces, nao comprova que agente externo leu arquivos,
nem registra hooks nativos no GitHub ou na ferramenta de IA.
"""
import ast
import hashlib
from pathlib import Path

try:
    from core import ROOT, load_json
except ModuleNotFoundError:
    from scripts.core import ROOT, load_json

BOOTSTRAP_FILES = (
    "AGENTS.md", "settings.json", "rules/CORE.md",
    "guardrails/CORE.md", "memory/INDEX.md", "memory/HANDOFF.md",
    "state/CURRENT.json", "EDITAL_UFMS_152_2026.md", "edital/INDEX.md",
)
HOOK_FILES = {
    "before_write": "hooks/before_write.py",
    "after_write": "hooks/after_write.py",
    "checkpoint": "hooks/checkpoint.py",
}


def _contained_file(root, relative):
    if not isinstance(relative, str) or relative.startswith("/") or "\\" in relative:
        raise ValueError("Caminho de gate inválido")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Caminho de gate inseguro")
    resolved_root = Path(root).resolve()
    path = resolved_root / candidate
    if path.is_symlink() or not path.resolve().is_relative_to(resolved_root):
        raise ValueError("Gate fora do repositório ou symlink")
    if not path.is_file():
        raise ValueError("Arquivo de gate ausente: " + relative)
    return path


def check_bootstrap(root=ROOT):
    settings = load_json(Path(root) / "settings.json")
    mandatory = settings.get("bootstrap", {}).get("mandatory")
    if mandatory != list(BOOTSTRAP_FILES):
        raise ValueError("Conjunto e ordem do bootstrap divergentes do contrato")
    hashes = {}
    for name in BOOTSTRAP_FILES:
        raw = _contained_file(root, name).read_bytes()
        if not raw.strip():
            raise ValueError("Arquivo obrigatório vazio: " + name)
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Bootstrap não UTF-8: " + name) from exc
        hashes[name] = hashlib.sha256(raw).hexdigest()
    return hashes


def check_hook_contract(root=ROOT):
    settings = load_json(Path(root) / "settings.json")
    cfg = settings.get("hooks")
    if not isinstance(cfg, dict) or cfg.get("native_registration_required") is not True:
        raise ValueError("Registro nativo de hooks deve permanecer explicitamente requerido")
    for name, path in HOOK_FILES.items():
        if cfg.get(name) != path:
            raise ValueError("Hook obrigatório divergente: " + name)
        source = _contained_file(root, path).read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as exc:
            raise ValueError("Sintaxe de hook inválida: " + name) from exc
        if not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "run"
                   for n in tree.body):
            raise ValueError("Hook sem interface run: " + name)
    return tuple(HOOK_FILES)
