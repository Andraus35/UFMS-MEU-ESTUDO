"""Ponto de entrada SOMENTE LEITURA para futuros agentes UFMS.

START verificável local, na revisão Git informada por ambiente externo.
Não instala runtime de Tutor/Coach nem intercepta GitHub/Zapia/Calendar.
Quem tiver acesso direto às credenciais pode contornar este ponto de entrada.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from bootstrap import run as bootstrap_run
except ModuleNotFoundError:
    from scripts.bootstrap import run as bootstrap_run

ROLES = frozenset({"tutor", "coach", "engineer", "auditor"})
ROLE_MODE = {"tutor": "study", "coach": "study",
             "engineer": "engineering", "auditor": "engineering"}
READ_ACTIONS = frozenset({"start", "inspect"})
SHA40 = re.compile(r"^[0-9a-f]{40}$")


class StartBlocked(ValueError):
    """O START obrigatório do ponto de entrada controlado não foi satisfeito."""


def _git_command(root, *arguments):
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *arguments],
            capture_output=True, text=True, check=False, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StartBlocked("Git indisponível para conferir o checkout") from exc
    if proc.returncode != 0:
        raise StartBlocked("Checkout Git não verificável")
    return proc.stdout.strip()


def _git_head(root):
    return _git_command(root, "rev-parse", "HEAD")


def _git_clean(root):
    if _git_command(root, "status", "--porcelain", "--untracked-files=all"):
        raise StartBlocked("Checkout alterado; START requer árvore limpa")


def verify_start(root, trusted_head, mode):
    """Lê bytes e checks locais; SHA de confiança deve vir do orquestrador."""
    if not isinstance(trusted_head, str) or not SHA40.fullmatch(trusted_head):
        raise StartBlocked("SHA de confiança ausente ou inválido")
    if mode not in ("study", "engineering"):
        raise StartBlocked("Modo de entrada inválido")
    root = Path(root).resolve()
    if _git_head(root) != trusted_head:
        raise StartBlocked("HEAD do checkout diverge do SHA confiável")
    _git_clean(root)
    try:
        receipt = bootstrap_run(root, mode=mode)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        raise StartBlocked("START local não aprovado: " + str(exc)) from exc
    return {
        "head": trusted_head,
        "mode": mode,
        "files": tuple(receipt["obrigatorios"]),
        "hashes": dict(receipt["sha256_dos_arquivos"]),
        "task": receipt.get("tarefa_ativa"),
        "pr": receipt.get("pr_ativo"),
        "branch": receipt.get("branch_ativa"),
        "next_after_merge": receipt.get("proxima_apos_merge"),
    }


class ReadOnlyAgentBroker:
    """Só oferece START e leitura de contexto. Não expõe ferramentas de escrita."""
    def __init__(self, root, trusted_head, role):
        if role not in ROLES:
            raise StartBlocked("Papel de agente não permitido")
        self._root = Path(root).resolve()
        self._trusted_head = trusted_head
        self._role = role
        self._mode = ROLE_MODE[role]
        self._snapshot = verify_start(self._root, trusted_head, self._mode)

    def _refresh(self):
        fresh = verify_start(self._root, self._trusted_head, self._mode)
        if fresh["hashes"] != self._snapshot["hashes"]:
            raise StartBlocked("Arquivos mudaram após START; criar nova sessão")
        return fresh

    def request(self, action):
        if action not in READ_ACTIONS:
            raise StartBlocked("Operações externas não habilitadas neste broker")
        current = self._refresh()
        return {
            "status": "start_verified",
            "scope": "local_read_only",
            "role": self._role,
            "action": action,
            "head": self._trusted_head,
            "mode": self._mode,
            "mandatory": list(current["files"]),
            "sha256": dict(current["hashes"]),
            "task": current["task"],
            "pr": current["pr"],
            "external_effects_enabled": False,
        }

    def model_context(self):
        """Entregar o texto lido à futura chamada ao modelo; sem afirmar compreensão."""
        current = self._refresh()
        permitted = ("AGENTS.md", "ROADMAP.md", "PRODUCT.md", "memory/HANDOFF.md",
                     "state/CURRENT.json", "state/WORKFLOW.json")
        context = {}
        for name in current["files"]:
            if name not in permitted:
                raise StartBlocked("Documento não permitido no contexto do modelo")
            candidate = self._root / name
            if candidate.is_symlink() or not candidate.resolve().is_relative_to(self._root):
                raise StartBlocked("Caminho obrigatório redirecionado")
            raw = candidate.read_bytes()
            if len(raw) > 64 * 1024:
                raise StartBlocked("Documento extenso demais para START automático")
            if hashlib.sha256(raw).hexdigest() != current["hashes"][name]:
                raise StartBlocked("Documento mudou entre validação e entrega")
            context[name] = raw.decode("utf-8")
        return {"head": self._trusted_head, "role": self._role,
                "mode": self._mode, "documents": context,
                "sha256": dict(current["hashes"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=sorted(ROLES), required=True)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    try:
        broker = ReadOnlyAgentBroker(
            args.root, os.environ.get("UFMS_TRUSTED_HEAD_SHA", ""), args.role)
        print(json.dumps(broker.request("start"), ensure_ascii=False, sort_keys=True))
    except (StartBlocked, OSError, UnicodeError) as exc:
        print("BLOQUEADO: " + str(exc), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
