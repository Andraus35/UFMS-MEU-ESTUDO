#!/usr/bin/env python3
"""Chaves Ed25519 e assinatura LOCAL dos comandos de Tutor e Coach (S4: assinatura fora do modelo).

Roda no computador do proprietário (ou onde o agente roda), nunca dentro do modelo. Comandos:
  generate  cria um par de chaves; a PRIVADA vai para um arquivo FORA do repositório (modo 0600, sem
            sobrescrever) e a PÚBLICA é impressa para ser registrada em config/agent_public_keys.json por PR.
  sign      lê um comando JSON, preenche `signature` com a chave privada e imprime o comando assinado.
  check     confere um comando assinado contra config/agent_public_keys.json (sem rede).
  verify-key confere a guarda do arquivo da chave privada (fora do repositório, não symlink, dono, modo 0600,
            diretório não gravável por terceiros) e se ela corresponde à pública registrada; nunca imprime a privada.

Limites: a assinatura em Python puro não resiste a ataques de temporização (uso local, uma chave do dono);
a proteção do arquivo da chave privada é do sistema de arquivos; este código não prova onde o agente roda
nem que a Zapia verifica (OPEN-09). Nunca imprime a chave privada.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import agent_commands
    import ed25519_pure
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import agent_commands, ed25519_pure

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_KEYS = ROOT / "config" / "agent_public_keys.json"


def load_public_keys(path: Path = PUBLIC_KEYS) -> dict:
    """{origem: ("ed25519", chave_pública_32_bytes)} só para as origens registradas; erro se malformado."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    keys = data.get("keys")
    if not isinstance(keys, dict):
        raise ValueError("arquivo de chaves públicas sem o objeto 'keys'")
    out = {}
    for origin, value in keys.items():
        if origin not in agent_commands.OPERATIONS:
            raise ValueError(f"origem desconhecida: {origin}")
        if value is None:
            continue
        try:
            raw = bytes.fromhex(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"chave pública inválida para {origin}") from exc
        if len(raw) != 32:
            raise ValueError(f"chave pública de {origin} deve ter 32 bytes")
        out[origin] = ("ed25519", raw)
    return out


def _inside(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def generate(private_path, *, repo_root: Path = ROOT) -> str:
    """Grava a chave privada (hex) em `private_path` e devolve a pública em hex."""
    target = Path(private_path).expanduser()
    if _inside(target.parent if not target.exists() else target, repo_root):
        raise ValueError("a chave privada não pode ficar dentro do repositório")
    parent_mode = target.parent.resolve().stat().st_mode
    if parent_mode & 0o022:
        raise ValueError("diretório de destino gravável por grupo ou outros (use um diretório só seu, modo 0700)")
    secret = secrets.token_bytes(32)
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)  # falha se já existir
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(secret.hex() + "\n")
    return ed25519_pure.public_key(secret).hex()


def check_key_guard(path, *, repo_root: Path = ROOT) -> Path:
    """Guarda do arquivo da chave privada (D-18). Levanta ValueError no primeiro problema; devolve o caminho real.

    Exige: existir como arquivo regular, não ser symlink, ficar FORA do repositório, pertencer ao usuário atual,
    ter modo sem acesso de grupo/outros e estar em diretório que grupo/outros não possam alterar.
    Limite: confere o sistema de arquivos local; não protege contra processo do mesmo usuário nem contra root.
    """
    target = Path(path).expanduser()
    try:
        info = target.lstat()
    except FileNotFoundError as exc:
        raise ValueError("arquivo da chave privada não encontrado") from exc
    if stat.S_ISLNK(info.st_mode):
        raise ValueError("a chave privada não pode ser um link simbólico")
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("a chave privada deve ser um arquivo regular")
    if _inside(target, repo_root):
        raise ValueError("a chave privada não pode ficar dentro do repositório")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise ValueError("a chave privada pertence a outro usuário")
    if info.st_mode & 0o077:
        raise ValueError("arquivo da chave privada com permissões abertas (use modo 0600)")
    parent = target.resolve().parent
    parent_mode = parent.stat().st_mode
    if parent_mode & 0o022:
        raise ValueError("diretório da chave privada gravável por grupo ou outros (use um diretório só seu, modo 0700)")
    return target.resolve()


def _read_secret(path, *, repo_root: Path = ROOT) -> bytes:
    target = check_key_guard(path, repo_root=repo_root)
    try:
        raw = bytes.fromhex(target.read_text(encoding="utf-8").strip())
    except ValueError as exc:
        raise ValueError("chave privada malformada (esperado hexadecimal)") from exc
    if len(raw) != 32:
        raise ValueError("chave privada deve ter 32 bytes")
    return raw


def verify_key(path, role: str | None = None, *, repo_root: Path = ROOT, public_keys_path: Path = PUBLIC_KEYS) -> dict:
    """Relatório sem segredo: guarda OK, chave pública derivada e, se houver `role`, se coincide com a registrada."""
    secret = _read_secret(path, repo_root=repo_root)
    public = ed25519_pure.public_key(secret).hex()
    report = {"guard": "ok", "public_key": public}
    if role is not None:
        if role not in agent_commands.OPERATIONS:
            raise ValueError(f"origem desconhecida: {role}")
        registered = load_public_keys(public_keys_path).get(role)
        report["role"] = role
        report["registered"] = registered is not None
        report["matches_registered"] = bool(registered) and registered[1].hex() == public
    return report


def sign_command(command: dict, private_path, *, auto: bool = False, repo_root: Path = ROOT) -> dict:
    command = dict(command)
    if auto:
        command["issued_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        command["nonce"] = "n-" + secrets.token_hex(12)
    command["signature"] = ""
    command["signature"] = agent_commands.sign_ed25519(command, _read_secret(private_path, repo_root=repo_root))
    return command


def main(argv=None, *, repo_root: Path = ROOT, public_keys_path: Path = PUBLIC_KEYS) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--private-out", required=True)
    s = sub.add_parser("sign")
    s.add_argument("--key", required=True)
    s.add_argument("--command-file", required=True)
    s.add_argument("--auto", action="store_true", help="preenche issued_at e nonce")
    v = sub.add_parser("verify-key")
    v.add_argument("--key", required=True)
    v.add_argument("--role", choices=sorted(agent_commands.OPERATIONS), help="compara com a pública registrada")
    c = sub.add_parser("check")
    c.add_argument("--command-file", required=True)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "generate":
            print(json.dumps({"public_key": generate(args.private_out, repo_root=repo_root)}))
        elif args.cmd == "sign":
            command = json.loads(Path(args.command_file).read_text(encoding="utf-8"))
            print(json.dumps(sign_command(command, args.key, auto=args.auto, repo_root=repo_root), ensure_ascii=False))
        elif args.cmd == "verify-key":
            report = verify_key(args.key, args.role, repo_root=repo_root, public_keys_path=public_keys_path)
            print(json.dumps(report))
            return 0 if report.get("matches_registered", True) else 1
        else:
            command = json.loads(Path(args.command_file).read_text(encoding="utf-8"))
            result = agent_commands.validate_command(command, keys=load_public_keys(public_keys_path),
                                                     now=datetime.now(timezone.utc), ledger=agent_commands.CommandLedger())
            print(json.dumps(result))
            return 0 if result["decision"] == agent_commands.ACCEPTED else 1
    except (OSError, ValueError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
