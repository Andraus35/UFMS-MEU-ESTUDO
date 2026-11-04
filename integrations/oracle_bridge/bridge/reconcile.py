"""Reconciliação LOCAL de notificações com ACK incerto, sem expor conteúdo.

Operador deve conferir no Telegram se chegou; não use este comando para
reenviar automaticamente uma mensagem.
"""
from __future__ import annotations

import argparse
import json
import os

from .gateway import Store
from .proactive import ProactiveOutbox


def main():
    parser = argparse.ArgumentParser(description="Auditoria de entregas incertas")
    parser.add_argument("action", choices=("list", "mark-delivered", "cancel"))
    parser.add_argument("kind", choices=("reminder", "proactive"), nargs="?")
    parser.add_argument("id", type=int, nargs="?")
    parser.add_argument("--db", default=os.getenv("UFMS_SQLITE_PATH", "/data/ufms-bridge.sqlite3"))
    args = parser.parse_args()
    if args.action != "list" and (args.kind is None or args.id is None or args.id <= 0):
        parser.error("Operação exige tipo e ID")
    store = Store(args.db)
    if args.action == "list":
        payload = {"reminders": store.unresolved()}
        if os.getenv("UFMS_ALLOWED_TELEGRAM_USER_ID", "").isdecimal():
            queue = ProactiveOutbox(store, int(os.environ["UFMS_ALLOWED_TELEGRAM_USER_ID"]))
            payload["proactive"] = queue.unresolved()
        print(json.dumps(payload, ensure_ascii=False))
        return
    if args.kind == "reminder":
        change = store.resolve_uncertain
    else:
        allowed = os.getenv("UFMS_ALLOWED_TELEGRAM_USER_ID", "")
        if not allowed.isdecimal() or int(allowed) <= 0:
            parser.error("ID autorizado necessário para notificações proativas")
        change = ProactiveOutbox(store, int(allowed)).resolve_uncertain
    ok = change(args.id, "delivered" if args.action == "mark-delivered" else "cancelled")
    print("Reconciliação registrada" if ok else "Item não encontrado ou não está incerto")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
