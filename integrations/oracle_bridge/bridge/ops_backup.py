"""Encrypted, operator-initiated SQLite backup and OFFLINE restore.

- sqlite3.Connection.backup() for a transactionally consistent snapshot.
- age recipient (PUBLIC) encrypts; the identity (PRIVATE) is needed only to restore.
- Snapshot lives on a tmpfs directory when deployed as documented.
- Restore validates integrity, acquires the same exclusive lock as the gateway,
  and fails closed for active clients or auxiliary WAL files.
- Output is never automatically uploaded or deleted. Operator controls retention.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sqlite3
import stat
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote

from .runtime_lock import acquire_runtime_lock

_REQUIRED = frozenset(("reminders", "settings", "bot_offsets"))
_AGE_PUBLIC = re.compile(r"age1[a-z0-9]{20,4000}\Z")


def _regular_file(path: Path, *, private: bool = False) -> None:
    info = path.lstat()  # Reject symlinks, including broken symlinks.
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Arquivo regular obrigatório")
    if private and info.st_mode & 0o077:
        raise PermissionError("Chave privada precisa de permissões 0600 ou mais restritas")


def _private_directory(path: Path) -> None:
    info = path.stat()
    if path.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077:
        raise PermissionError("Diretório de backups deve existir com permissões 0700")


def _scratch_directory(path: Path) -> None:
    """Require a private directory or a sticky 1777 tmpfs (as in /tmp)."""
    info = path.stat()
    mode = stat.S_IMODE(info.st_mode)
    private = mode & 0o077 == 0
    sticky_tmp = mode == 0o1777
    if path.is_symlink() or not stat.S_ISDIR(info.st_mode) or not (private or sticky_tmp):
        raise PermissionError("Scratch deve ser diretório privado ou tmpfs /tmp com sticky bit")


def _check_database(path: Path) -> None:
    _regular_file(path)
    # Read-only URI prevents sqlite3 from silently creating a damaged/empty file.
    uri = "file:" + quote(str(path.resolve()), safe="/") + "?mode=ro"
    with contextlib.closing(sqlite3.connect(uri, uri=True, timeout=5)) as db:
        result = db.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise ValueError("SQLite não passou na verificação de integridade")
        table_names = {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        if not _REQUIRED.issubset(table_names):
            raise ValueError("Estrutura da ponte UFMS incompleta")
        if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise ValueError("SQLite contém referência estrangeira inválida")


def _age(args: list[str]) -> None:
    # Never print command, output, stderr, key path or original exception/URL.
    try:
        subprocess.run(["age", *args], stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=120, check=True)
    except (OSError, subprocess.SubprocessError):
        raise RuntimeError("Operação criptográfica não confirmada") from None


def _flush_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _temp_file(directory: Path, prefix: str, suffix: str) -> Path:
    fd, name = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=directory)
    os.fchmod(fd, 0o600)
    os.close(fd)
    return Path(name)


def _snapshot(db_path: Path, destination: Path) -> None:
    _regular_file(db_path)
    source_uri = "file:" + quote(str(db_path.resolve()), safe="/") + "?mode=ro"
    with contextlib.closing(sqlite3.connect(source_uri, uri=True, timeout=20)) as source:
        with contextlib.closing(sqlite3.connect(destination)) as target:
            source.backup(target)
    _check_database(destination)


def backup_database(db_path: str, output_path: str, recipient: str,
                    *, scratch_dir: str = "/tmp") -> dict:
    """Never overwrite a backup; never publish incomplete ciphertext."""
    if not isinstance(recipient, str) or not _AGE_PUBLIC.fullmatch(recipient):
        raise ValueError("Recipient público age inválido")
    source = Path(db_path)
    output = Path(output_path)
    _regular_file(source)
    _private_directory(output.parent)
    if output.suffix != ".age":
        raise ValueError("Backup deve ter extensão .age")
    if os.path.lexists(output):
        raise FileExistsError("Backup com esse nome já existe")
    scratch = Path(scratch_dir)
    _scratch_directory(scratch)
    plaintext = _temp_file(scratch, ".ufms-snapshot-", ".sqlite3")
    encrypted = _temp_file(output.parent, ".ufms-incomplete-", ".age")
    try:
        _snapshot(source, plaintext)
        _age(["-e", "-r", recipient, "-o", str(encrypted), str(plaintext)])
        _regular_file(encrypted)
        if encrypted.stat().st_size < 100:
            raise RuntimeError("Criptografia não produziu arquivo válido")
        # Hardlink is atomic and refuses overwrite. Then unlink partial.
        os.link(encrypted, output, follow_symlinks=False)
        _flush_directory(output.parent)
        return {"created": True, "file": output.name,
                "encrypted_bytes": output.stat().st_size}
    finally:
        plaintext.unlink(missing_ok=True)
        encrypted.unlink(missing_ok=True)


def _decrypt_and_check(ciphertext: Path, identity: Path, destination: Path):
    _age(["-d", "-i", str(identity), "-o", str(destination), str(ciphertext)])
    _check_database(destination)


def verify_backup(encrypted_path: str, identity_path: str,
                  *, scratch_dir: str = "/tmp") -> dict:
    archive = Path(encrypted_path)
    identity = Path(identity_path)
    _regular_file(archive)
    _regular_file(identity, private=True)
    scratch = Path(scratch_dir)
    _scratch_directory(scratch)
    temporary = _temp_file(scratch, ".ufms-verify-", ".sqlite3")
    try:
        _decrypt_and_check(archive, identity, temporary)
        return {"verified": True, "file": archive.name}
    finally:
        temporary.unlink(missing_ok=True)


def restore_database(encrypted_path: str, db_path: str, identity_path: str,
                     *, confirm: bool = False, replace_existing: bool = False) -> dict:
    if not confirm:
        raise PermissionError("Restauração exige --confirm-restore")
    archive = Path(encrypted_path)
    identity = Path(identity_path)
    target = Path(db_path)
    _regular_file(archive)
    _regular_file(identity, private=True)
    if target.exists() or target.is_symlink():
        _regular_file(target)
        if not replace_existing:
            raise PermissionError("Banco já existe; --replace-existing é obrigatório")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.parent.is_symlink():
        raise PermissionError("Diretório do banco não pode ser link simbólico")
    lock_fd = acquire_runtime_lock(str(target))
    temporary = None
    try:
        # Never replace database files alongside active or stale WAL sidecars.
        if Path(str(target) + "-wal").exists() or Path(str(target) + "-shm").exists():
            raise RuntimeError("Arquivos WAL/SHM presentes; reconcilie offline antes")
        temporary = _temp_file(target.parent, ".ufms-restore-", ".sqlite3")
        _decrypt_and_check(archive, identity, temporary)
        with temporary.open("rb") as file:
            os.fsync(file.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
        temporary = None
        _flush_directory(target.parent)
        return {"restored": True, "file": target.name}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        os.close(lock_fd)


def main():
    parser = argparse.ArgumentParser(description="Backup criptografado e restauração offline")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("backup")
    create.add_argument("--db", required=True)
    create.add_argument("--output", required=True)
    create.add_argument("--recipient", required=True)
    create.add_argument("--scratch", default="/tmp")
    verify = sub.add_parser("verify")
    verify.add_argument("--input", required=True)
    verify.add_argument("--identity", required=True)
    verify.add_argument("--scratch", default="/tmp")
    restore = sub.add_parser("restore")
    restore.add_argument("--db", required=True)
    restore.add_argument("--input", required=True)
    restore.add_argument("--identity", required=True)
    restore.add_argument("--confirm-restore", action="store_true")
    restore.add_argument("--replace-existing", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "backup":
            result = backup_database(args.db, args.output, args.recipient,
                                     scratch_dir=args.scratch)
        elif args.command == "verify":
            result = verify_backup(args.input, args.identity, scratch_dir=args.scratch)
        else:
            result = restore_database(args.input, args.db, args.identity,
                                      confirm=args.confirm_restore,
                                      replace_existing=args.replace_existing)
    except Exception:
        # No original exceptions, paths, key material, DB contents in stdout/stderr.
        parser.exit(1, "Operação não concluída; consulte o procedimento OPS-01.\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
