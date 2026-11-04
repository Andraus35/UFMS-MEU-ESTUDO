"""Inspeção e limpeza explícita do histórico de lembretes finalizados.

Padrão dry-run. Não faz VACUUM nem elimina backups; verificar política
de retenção e backups criptografados antes do uso em Oracle.
"""
from __future__ import annotations

import argparse
import json
import os
from .gateway import Store, DEFAULT_RETENTION_DAYS


def main():
    parser = argparse.ArgumentParser(description="Retenção segura de lembretes UFMS")
    parser.add_argument("--db", default=os.getenv("UFMS_SQLITE_PATH", "/data/ufms-bridge.sqlite3"))
    parser.add_argument("--days", type=int, default=DEFAULT_RETENTION_DAYS)
    parser.add_argument("--apply", action="store_true", help="Aplica remoção; padrão é dry-run")
    args = parser.parse_args()
    store = Store(args.db)
    report = store.purge_finalized(days=args.days, apply=args.apply)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
