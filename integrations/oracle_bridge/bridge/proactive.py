"""Fila de alertas iniciados por Tutor/Coach, com autorização e segurança por padrão.

Nenhum modelo de IA é executado aqui. Um futuro produtor confiável deve fornecer
evidência (source_ref), categoria, destino autorizado e chave idempotente.
Após tentativa de envio com confirmação ambígua, o item fica 'uncertain',
e NÃO há reenvio automático; a reconciliação exige intervenção do operador.
"""
from __future__ import annotations

import re
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
LOCAL = ZoneInfo("America/Campo_Grande")
BOTS = frozenset(("tutor", "coach"))
CATEGORIES = frozenset(("review", "checkin", "deadline", "strategy"))
DAILY_CAP = 4
COOLDOWN = timedelta(minutes=60)
START_HOUR = 7
END_HOUR = 22


class ProactiveOutbox:
    def __init__(self, store, allowed_user_id: int):
        if type(allowed_user_id) is not int or allowed_user_id <= 0:
            raise ValueError("ID Telegram autorizado deve ser inteiro positivo")
        self.store = store
        self.allowed_user_id = allowed_user_id
        with store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS proactive_notifications(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot TEXT NOT NULL CHECK (bot IN ('tutor','coach')),
                chat_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                due_utc TEXT NOT NULL,
                body TEXT NOT NULL,
                reason TEXT NOT NULL,
                source_ref TEXT NOT NULL,
                request_key TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                claimed_utc TEXT,
                sent_utc TEXT
            )""")
            db.execute("""CREATE INDEX IF NOT EXISTS idx_proactive_due
                ON proactive_notifications(status,due_utc)""")

    def enabled(self) -> bool:
        with self.store.connect() as db:
            row = db.execute(
                "SELECT value FROM settings WHERE key='proactive_enabled'"
            ).fetchone()
            return bool(row and row["value"] == "1")

    def set_enabled(self, enabled: bool) -> None:
        with self.store.connect() as db:
            db.execute("""INSERT INTO settings(key,value)
                VALUES('proactive_enabled',?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                ("1" if enabled else "0",))

    def enqueue(self, *, bot: str, user_id: int, category: str,
                due: datetime, body: str, reason: str,
                source_ref: str, request_key: str,
                now: datetime | None = None) -> int:
        if bot not in BOTS or user_id != self.allowed_user_id:
            raise PermissionError("Papel ou destinatário não autorizado")
        if category not in CATEGORIES:
            raise ValueError("Categoria de alerta não permitida")
        if due.tzinfo is None or due.utcoffset() is None:
            raise ValueError("Data sem fuso")
        now = now or datetime.now(UTC)
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Relógio sem fuso")
        if not now - timedelta(minutes=5) <= due <= now + timedelta(days=366):
            raise ValueError("Data fora da janela permitida")
        if not isinstance(body, str) or not (1 <= len(body.strip()) <= 1000):
            raise ValueError("Mensagem inválida")
        if not isinstance(reason, str) or not (3 <= len(reason.strip()) <= 240):
            raise ValueError("Justificativa obrigatória")
        if not isinstance(source_ref, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_./:@-]{2,160}", source_ref):
            raise ValueError("Referência verificável obrigatória")
        if not isinstance(request_key, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_./:@-]{3,160}", request_key):
            raise ValueError("Chave idempotente obrigatória")
        with self.store.connect() as db:
            db.execute("""INSERT OR IGNORE INTO proactive_notifications(
                bot,chat_id,category,due_utc,body,reason,source_ref,request_key
            ) VALUES(?,?,?,?,?,?,?,?)""", (
                bot, user_id, category, due.astimezone(UTC).isoformat(),
                body.strip(), reason.strip(), source_ref, request_key
            ))
            row = db.execute(
                "SELECT id,bot,chat_id,category,body,source_ref FROM proactive_notifications WHERE request_key=?",
                (request_key,)
            ).fetchone()
            if (row["bot"], row["chat_id"], row["category"], row["body"], row["source_ref"]) != (
                bot, user_id, category, body.strip(), source_ref
            ):
                raise ValueError("Chave já usada para conteúdo incompatível")
            return int(row["id"])

    def claim_next(self, now: datetime | None = None) -> dict | None:
        now = (now or datetime.now(UTC)).astimezone(UTC)
        local = now.astimezone(LOCAL)
        if not START_HOUR <= local.hour < END_HOUR:
            return None
        local_midnight = datetime.combine(local.date(), time.min, tzinfo=LOCAL)
        day_start = local_midnight.astimezone(UTC).isoformat()
        day_end = (local_midnight + timedelta(days=1)).astimezone(UTC).isoformat()
        # BEGIN IMMEDIATE garante que duas réplicas não reivindiquem a mesma linha.
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if self.store.paused():  # Leitura simples, sem mutação; consentimento abaixo.
                return None
            enabled = db.execute(
                "SELECT value FROM settings WHERE key='proactive_enabled'"
            ).fetchone()
            if not enabled or enabled["value"] != "1":
                return None
            used = db.execute("""SELECT COUNT(*) AS total FROM proactive_notifications
              WHERE claimed_utc>=? AND claimed_utc<? AND status IN ('sending','sent','uncertain')""",
              (day_start, day_end)).fetchone()["total"]
            if used >= DAILY_CAP:
                return None
            prior = db.execute("""SELECT MAX(claimed_utc) AS last FROM proactive_notifications
              WHERE status IN ('sending','sent','uncertain')""").fetchone()["last"]
            if prior and now - datetime.fromisoformat(prior) < COOLDOWN:
                return None
            row = db.execute("""SELECT * FROM proactive_notifications
                WHERE status='pending' AND due_utc<=?
                ORDER BY due_utc,id LIMIT 1""", (now.isoformat(),)).fetchone()
            if row is None:
                return None
            changed = db.execute("""UPDATE proactive_notifications
                SET status='sending',claimed_utc=?
                WHERE id=? AND status='pending'""", (now.isoformat(), row["id"]))
            if changed.rowcount != 1:
                return None
            return dict(row)

    def mark_sent(self, item_id: int, now: datetime | None = None) -> None:
        at = (now or datetime.now(UTC)).astimezone(UTC).isoformat()
        with self.store.connect() as db:
            db.execute("""UPDATE proactive_notifications SET status='sent',sent_utc=?
                WHERE id=? AND status='sending'""", (at, item_id))

    def mark_uncertain(self, item_id: int) -> None:
        with self.store.connect() as db:
            db.execute("""UPDATE proactive_notifications SET status='uncertain'
                WHERE id=? AND status='sending'""", (item_id,))

    def status(self, item_id: int) -> str | None:
        with self.store.connect() as db:
            row = db.execute(
                "SELECT status FROM proactive_notifications WHERE id=?", (item_id,)
            ).fetchone()
            return row["status"] if row else None

    def unresolved_counts(self) -> dict:
        with self.store.connect() as db:
            return {row["status"]: row["total"] for row in db.execute(
                """SELECT status, COUNT(*) AS total FROM proactive_notifications
                GROUP BY status"""
            )}


def dispatch_proactive(outbox: ProactiveOutbox, clients: dict,
                       now: datetime | None = None) -> int:
    """No máximo uma tentativa por chamada. Incertos nunca são reenviados automaticamente."""
    item = outbox.claim_next(now)
    if item is None:
        return 0
    try:
        clients[item["bot"]].send(item["chat_id"], item["body"])
    except Exception:
        # timeout pode ocorrer após aceitação pelo Telegram. Não retry cego.
        outbox.mark_uncertain(item["id"])
        return 0
    outbox.mark_sent(item["id"], now)
    return 1
