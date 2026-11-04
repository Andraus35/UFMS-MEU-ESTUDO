"""Linux single-instance lock shared by the Oracle gateway and offline recovery.

The lock file must never be unlinked while in use. A restore requires exclusive
ownership of exactly the same lock as the live gateway.
"""
from __future__ import annotations

import fcntl
import os
from pathlib import Path


def acquire_runtime_lock(db_path: str) -> int:
    lock = Path(str(db_path) + ".runtime.lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(lock, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError):
            raise RuntimeError("Banco em uso: pare a ponte UFMS antes de restaurar") from None
        return fd
    except Exception:
        os.close(fd)
        raise
