"""Gateway de comandos: dois bots privados, lembretes persistidos e agenda opcional.

Não implementa um tutor LLM. As mensagens espontâneas vêm de lembretes
autorizados ou de eventos explicitamente enfileirados por um serviço futuro.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from .proactive import ProactiveOutbox, dispatch_proactive
from .agents import configured_agent
from .checkins import generate_generic_checkins
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import error, request

UTC = timezone.utc
BOTS = ("tutor", "coach")
# Proteções conservadoras contra filas infinitas e consumo de disco.
MAX_ACTIVE_REMINDERS_PER_USER = 30
MAX_NEW_REMINDERS_PER_24H = 20
DEFAULT_RETENTION_DAYS = 30


def parse_time(raw: str, now: datetime | None = None) -> datetime:
    try:
        value = datetime.fromisoformat(raw.strip())
    except ValueError as exc:
        raise ValueError("Data inválida; use AAAA-MM-DDTHH:MM-04:00") from exc
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Informe o fuso UTC, por exemplo -04:00")
    now = now or datetime.now(UTC)
    instant = value.astimezone(UTC)
    if not now < instant < now + timedelta(days=366):
        raise ValueError("O horário deve estar no futuro e em até 366 dias")
    return instant


class Store:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS reminders(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              bot TEXT NOT NULL CHECK(bot IN ('tutor','coach')),
              chat_id INTEGER NOT NULL, due_utc TEXT NOT NULL,
              body TEXT NOT NULL, request_key TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL DEFAULT 'pending',
              created_utc TEXT NOT NULL, sent_utc TEXT,
              claimed_utc TEXT, finalized_utc TEXT
            )""")
            # Migração não destrutiva do SQLite criado no MVP anterior.
            cols = {row["name"] for row in db.execute("PRAGMA table_info(reminders)")}
            if "claimed_utc" not in cols:
                db.execute("ALTER TABLE reminders ADD COLUMN claimed_utc TEXT")
            if "finalized_utc" not in cols:
                db.execute("ALTER TABLE reminders ADD COLUMN finalized_utc TEXT")
            db.execute("""CREATE INDEX IF NOT EXISTS idx_reminders_chat_status
              ON reminders(chat_id,status)""")
            db.execute("""CREATE INDEX IF NOT EXISTS idx_reminders_created
              ON reminders(chat_id,created_utc)""")
            db.execute("""CREATE TABLE IF NOT EXISTS bot_offsets(
              bot TEXT PRIMARY KEY, next_offset INTEGER NOT NULL DEFAULT 0
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS settings(
              key TEXT PRIMARY KEY, value TEXT NOT NULL
            )""")

    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=15000")
        return db

    def offset(self, bot: str) -> int:
        with self.connect() as db:
            row = db.execute("SELECT next_offset FROM bot_offsets WHERE bot=?", (bot,)).fetchone()
            return int(row["next_offset"]) if row else 0

    def advance(self, bot: str, update_id: int):
        with self.connect() as db:
            db.execute("""INSERT INTO bot_offsets(bot,next_offset) VALUES(?,?)
              ON CONFLICT(bot) DO UPDATE SET next_offset=max(next_offset, excluded.next_offset)""",
              (bot, update_id + 1))

    def schedule(self, bot: str, chat_id: int, due: datetime, body: str,
                 key: str, now: datetime | None = None) -> int:
        """Transação atômica: idempotência exata, cota diária e fila compartilhada."""
        if bot not in BOTS or type(chat_id) is not int or chat_id <= 0:
            raise ValueError("Identificação de lembrete inválida")
        if not isinstance(due, datetime) or due.tzinfo is None or due.utcoffset() is None:
            raise ValueError("Lembrete exige data com fuso")
        if not isinstance(body, str) or not 1 <= len(body.strip()) <= 500:
            raise ValueError("Mensagem deve ter entre 1 e 500 caracteres")
        if not isinstance(key, str) or not 1 <= len(key) <= 160:
            raise ValueError("Chave idempotente inválida")
        at = now or datetime.now(UTC)
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("Relógio de referência exige fuso")
        iso_now = at.astimezone(UTC).isoformat()
        iso_due = due.astimezone(UTC).isoformat()
        last_24h = (at.astimezone(UTC) - timedelta(hours=24)).isoformat()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("""SELECT id,bot,chat_id,due_utc,body
                FROM reminders WHERE request_key=?""", (key,)).fetchone()
            if existing is not None:
                if (existing["bot"], existing["chat_id"], existing["due_utc"],
                        existing["body"]) != (bot, chat_id, iso_due, body.strip()):
                    raise ValueError("Chave reutilizada com conteúdo diferente")
                return int(existing["id"])
            active = db.execute("""SELECT COUNT(*) AS n FROM reminders
                WHERE chat_id=? AND status IN ('pending','sending','uncertain')""",
                (chat_id,)).fetchone()["n"]
            if active >= MAX_ACTIVE_REMINDERS_PER_USER:
                raise ValueError("Limite de lembretes ativos atingido; cancele ou conclua algum")
            recent = db.execute("""SELECT COUNT(*) AS n FROM reminders
                WHERE chat_id=? AND created_utc>? AND created_utc<=?""",
                (chat_id, last_24h, iso_now)).fetchone()["n"]
            if recent >= MAX_NEW_REMINDERS_PER_24H:
                raise ValueError("Limite de novos lembretes nas últimas 24 horas atingido")
            cursor = db.execute("""INSERT INTO reminders
                (bot,chat_id,due_utc,body,request_key,created_utc)
                VALUES(?,?,?,?,?,?)""",
                (bot,chat_id,iso_due,body.strip(),key,iso_now))
            return int(cursor.lastrowid)

    def due(self, now: datetime, limit: int = 15):
        with self.connect() as db:
            return [dict(row) for row in db.execute(
                """SELECT * FROM reminders WHERE status='pending' AND due_utc<=?
                   ORDER BY due_utc,id LIMIT ?""", (now.isoformat(), limit))]

    def claim_due(self, now: datetime) -> dict | None:
        """Reivindica um único lembrete de forma transacional; status evita replay."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""SELECT * FROM reminders
              WHERE status='pending' AND due_utc<=?
              ORDER BY due_utc,id LIMIT 1""", (now.astimezone(UTC).isoformat(),)).fetchone()
            if row is None:
                return None
            changed = db.execute("""UPDATE reminders
              SET status='sending',claimed_utc=? WHERE id=? AND status='pending'""",
              (now.astimezone(UTC).isoformat(), row["id"]))
            if changed.rowcount != 1:
                return None
            return dict(row)

    def mark_sent(self, reminder_id: int):
        at = datetime.now(UTC).isoformat()
        with self.connect() as db:
            db.execute("""UPDATE reminders SET status='sent',sent_utc=?,finalized_utc=?
                WHERE id=? AND status='sending'""", (at, at, reminder_id))

    def mark_uncertain(self, reminder_id: int):
        with self.connect() as db:
            db.execute("UPDATE reminders SET status='uncertain' WHERE id=? AND status='sending'",
                       (reminder_id,))

    def unresolved(self) -> list[dict]:
        """Relatório SEM conteúdo, chat_id ou segredo."""
        with self.connect() as db:
            return [dict(row) for row in db.execute("""SELECT id,bot,status
                FROM reminders WHERE status IN ('sending','uncertain') ORDER BY id""")]

    def resolve_uncertain(self, reminder_id: int, decision: str) -> bool:
        """Somente operador após conferir entrega no Telegram."""
        if decision not in ("delivered", "cancelled"):
            raise ValueError("Decisão inválida")
        status = "sent" if decision == "delivered" else "cancelled"
        with self.connect() as db:
            updated = db.execute("""UPDATE reminders SET status=?,finalized_utc=?
                WHERE id=? AND status IN ('sending','uncertain')""",
                (status, datetime.now(UTC).isoformat(), reminder_id))
            return updated.rowcount == 1

    def cancel(self, reminder_id: int, bot: str, chat_id: int) -> bool:
        with self.connect() as db:
            result = db.execute("""UPDATE reminders SET status='cancelled',finalized_utc=?
              WHERE id=? AND bot=? AND chat_id=? AND status='pending'""",
              (datetime.now(UTC).isoformat(), reminder_id, bot, chat_id))
            return result.rowcount == 1

    def retention_report(self, now: datetime | None = None,
                         days: int = DEFAULT_RETENTION_DAYS) -> dict:
        """Contagens agregadas; não expõe chat_id, token, assunto ou mensagem."""
        if not 7 <= days <= 365:
            raise ValueError("Retenção exige prazo entre 7 e 365 dias")
        at = now or datetime.now(UTC)
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("Relógio sem fuso")
        cutoff = (at.astimezone(UTC) - timedelta(days=days)).isoformat()
        with self.connect() as db:
            eligible = db.execute("""SELECT COUNT(*) FROM reminders
                WHERE status IN ('sent','cancelled')
                AND COALESCE(finalized_utc,CASE WHEN status='sent' THEN sent_utc END)<?""",
                (cutoff,)).fetchone()[0]
            unresolved = db.execute("""SELECT COUNT(*) FROM reminders
                WHERE status IN ('sending','uncertain')""").fetchone()[0]
            pending = db.execute("""SELECT COUNT(*) FROM reminders
                WHERE status='pending'""").fetchone()[0]
        return {"eligible_finalized":eligible, "pending":pending,
                "unresolved":unresolved, "retention_days":days}

    def purge_finalized(self, *, now: datetime | None = None,
                        days: int = DEFAULT_RETENTION_DAYS,
                        apply: bool = False) -> dict:
        """Purge explícito apenas de finalizados envelhecidos; sem autoexecução."""
        stats = self.retention_report(now=now, days=days)
        if not apply:
            return {**stats, "deleted":0, "dry_run":True}
        at = now or datetime.now(UTC)
        cutoff = (at.astimezone(UTC) - timedelta(days=days)).isoformat()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            count = db.execute("""DELETE FROM reminders
                WHERE status IN ('sent','cancelled')
                AND COALESCE(finalized_utc,CASE WHEN status='sent' THEN sent_utc END)<?""",
                (cutoff,)).rowcount
        return {**stats, "deleted":count, "dry_run":False}

    def pending(self, bot: str, chat_id: int) -> int:
        with self.connect() as db:
            row = db.execute("""SELECT count(*) AS n FROM reminders
              WHERE bot=? AND chat_id=? AND status='pending'""", (bot, chat_id)).fetchone()
            return row["n"]

    def llm_consent(self) -> bool:
        """Consentimento para encaminhar texto do Telegram ao provedor de IA."""
        with self.connect() as db:
            item = db.execute("SELECT value FROM settings WHERE key='llm_consent'").fetchone()
            return bool(item and item["value"] == "1")

    def set_llm_consent(self, enabled: bool) -> None:
        """Revogação limpa metadados de chamadas já registrados, se existentes."""
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("""INSERT INTO settings(key,value) VALUES('llm_consent',?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                ("1" if enabled else "0",))
            if not enabled and db.execute("""SELECT 1 FROM sqlite_master
                WHERE type='table' AND name='llm_requests'""").fetchone():
                db.execute("DELETE FROM llm_requests")

    def paused(self) -> bool:
        with self.connect() as db:
            row = db.execute("SELECT value FROM settings WHERE key='paused'").fetchone()
            return row is not None and row["value"] == "1"

    def set_paused(self, paused: bool):
        with self.connect() as db:
            db.execute("""INSERT INTO settings(key,value) VALUES('paused',?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                ("1" if paused else "0",))


class Telegram:
    def __init__(self, token: str):
        if not token:
            raise ValueError("Token do Telegram ausente")
        self._token = token

    def call(self, method: str, payload: dict, timeout: int = 40):
        endpoint = "https://api.telegram.org/bot" + self._token + "/" + method
        req = request.Request(endpoint, data=json.dumps(payload).encode(),
                              headers={"Content-Type": "application/json"}, method="POST")
        # URLs Telegram carregam o token; nunca propagar erro HTTP cru.
        try:
            with request.urlopen(req, timeout=timeout) as reply:
                result = json.load(reply)
        except (error.HTTPError, error.URLError, TimeoutError, OSError,
                ValueError, TypeError, KeyError):
            raise RuntimeError("Falha de transporte do Telegram; entrega não confirmada") from None
        if not isinstance(result, dict) or not result.get("ok"):
            raise RuntimeError("Telegram não confirmou a operação")
        return result["result"]

    def send(self, chat_id: int, text: str):
        self.call("sendMessage", {"chat_id": chat_id, "text": text[:4000]})

    def updates(self, offset: int):
        return self.call("getUpdates", {
            "offset": offset, "timeout": 25, "limit": 25,
            "allowed_updates": ["message"]
        })


HELP = (
    "Comandos: /status, /pausar, /retomar, /alertas, /ativar_alertas, /desativar_alertas, "
    "/lembrete AAAA-MM-DDTHH:MM-04:00 | mensagem, "
    "/ia_status, /ativar_ia, /desativar_ia, "
    "/cancelar ID, /evento início | fim | título. "
    "Por ora este bot é uma ponte de agendamento, não uma IA autônoma."
)


def handle_update(bot: str, update: dict, store: Store, telegram: Telegram,
                  allowed_user_id: int, calendar=None, now: datetime | None = None, outbox=None, agent=None):
    update_id = update.get("update_id")
    if not isinstance(update_id, int) or update_id < store.offset(bot):
        return
    message = update.get("message") or {}
    sender = message.get("from") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if (sender.get("id") != allowed_user_id or chat.get("type") != "private"
            or chat_id != allowed_user_id):
        store.advance(bot, update_id)
        return  # Não revelar sequer a existência do serviço para terceiros.
    raw = (message.get("text") or "").strip()
    command = raw.split(None, 1)[0].split("@", 1)[0].lower() if raw else ""
    args = raw.split(None, 1)[1] if " " in raw else ""
    try:
        if command in ("/start", "/ajuda"):
            answer = HELP
        elif command == "/status":
            answer = (f"{bot.capitalize()}: " +
                      ("pausado" if store.paused() else "ativo") +
                      f"; lembretes pendentes: {store.pending(bot, chat_id)}.")
        elif command == "/ia_status":
            answer = ("Conversas com IA: " +
                      ("autorizadas" if store.llm_consent() and agent is not None
                       else "desativadas") +
                      ". O envio de texto ao provedor depende de autorização explícita.")
        elif command == "/ativar_ia":
            if agent is None:
                answer = "IA ainda indisponível no servidor Oracle; nenhum texto foi enviado."
            else:
                store.set_llm_consent(True)
                answer = ("IA autorizada: mensagens de texto enviadas aos bots poderão ser "
                          "processadas pela API externa de IA, com cobrança separada. "
                          "Use /desativar_ia para revogar.")
        elif command == "/desativar_ia":
            store.set_llm_consent(False)
            answer = ("IA desativada; mensagens posteriores não serão encaminhadas à API. "
                      "Pedidos já enviados podem estar em processamento.")
        elif command == "/alertas":
            answer = ("Alertas proativos: " +
                      ("ativados" if outbox is not None and outbox.enabled() else "desativados") +
                      ". Limite inicial: 4/dia, 07–22h, intervalo mínimo 60min.")
        elif command == "/ativar_alertas":
            if outbox is None:
                answer = "Serviço de alertas não disponível."
            else:
                outbox.set_enabled(True)
                answer = "Alertas proativos ativados. Use /desativar_alertas para revogar."
        elif command == "/desativar_alertas":
            if outbox is None:
                answer = "Serviço de alertas não disponível."
            else:
                outbox.set_enabled(False)
                answer = "Alertas proativos desativados."
        elif command == "/pausar":
            store.set_paused(True)
            answer = "Notificações pausadas. Use /retomar para continuar."
        elif command == "/retomar":
            store.set_paused(False)
            answer = "Notificações retomadas."
        elif command == "/lembrete":
            pieces = [p.strip() for p in args.split("|", 1)]
            if len(pieces) != 2 or not 1 <= len(pieces[1]) <= 500:
                raise ValueError("Uso: /lembrete AAAA-MM-DDTHH:MM-04:00 | mensagem")
            due = parse_time(pieces[0], now=now)
            rid = store.schedule(bot, chat_id, due, pieces[1], f"telegram:{bot}:{update_id}")
            answer = f"Lembrete {rid} registrado. Horário: {due.isoformat()} (UTC)."
        elif command == "/cancelar":
            if not args.isdecimal():
                raise ValueError("Uso: /cancelar ID")
            ok = store.cancel(int(args), bot, chat_id)
            answer = "Lembrete cancelado." if ok else "Lembrete não encontrado ou já concluído."
        elif command == "/evento":
            if calendar is None:
                answer = "Agenda Oracle não autorizada. Conecte o Google OAuth separadamente."
            else:
                pieces = [p.strip() for p in args.split("|", 2)]
                if len(pieces) != 3 or not 1 <= len(pieces[2]) <= 160:
                    raise ValueError("Uso: /evento início ISO | fim ISO | título")
                start = parse_time(pieces[0], now=now)
                end = parse_time(pieces[1], now=now)
                if end <= start or end - start > timedelta(hours=12):
                    raise ValueError("O evento deve terminar depois de começar e durar até 12h")
                event_id = calendar.create_event(start, end, pieces[2], f"{bot}:{update_id}")
                answer = f"Evento confirmado no calendário UFMS (ID {event_id})."
        else:
            if raw and not raw.startswith("/") and agent is not None:
                if store.llm_consent():
                    answer = agent.answer(bot, raw, f"{bot}:{update_id}")
                else:
                    answer = ("Para conversar com IA, autorize primeiro /ativar_ia. "
                              "Isso envia o texto à API externa de IA.")
            else:
                answer = ("Motor de IA indisponível ou comando desconhecido. " + HELP)
    except ValueError as exc:
        answer = str(exc)
    except Exception:
        answer = "Operação externa não confirmada; confira o estado antes de repetir."
    telegram.send(chat_id, answer)
    store.advance(bot, update_id)


def dispatch_due(store: Store, clients: dict[str, Telegram],
                 now: datetime | None = None):
    if store.paused():
        return 0
    completed = 0
    at = now or datetime.now(UTC)
    for _ in range(15):
        reminder = store.claim_due(at)
        if reminder is None:
            break
        try:
            clients[reminder["bot"]].send(reminder["chat_id"], reminder["body"])
        except Exception:
            # Timeout pode ocorrer depois da entrega. Não tentar de novo às cegas.
            store.mark_uncertain(reminder["id"])
            continue
        store.mark_sent(reminder["id"])
        completed += 1
    return completed


def poll_loop(bot: str, client: Telegram, store: Store, allowed_id: int, calendar, outbox, agent):
    while True:
        try:
            for update in client.updates(store.offset(bot)):
                handle_update(bot, update, store, client, allowed_id, calendar, outbox=outbox, agent=agent)
        except Exception:
            # Não logar URLs do Telegram: incluem o token.
            time.sleep(5)


def main():
    tokens = {
        "tutor": os.getenv("UFMS_TUTOR_BOT_TOKEN", ""),
        "coach": os.getenv("UFMS_COACH_BOT_TOKEN", ""),
    }
    allowed = os.getenv("UFMS_ALLOWED_TELEGRAM_USER_ID", "")
    if not all(tokens.values()) or not allowed.isdecimal() or int(allowed) <= 0:
        raise SystemExit("Configuração incompleta: dois tokens e ID numérico autorizado obrigatórios")
    store = Store(os.getenv("UFMS_SQLITE_PATH", "/data/ufms-bridge.sqlite3"))
    clients = {name: Telegram(token) for name, token in tokens.items()}
    from .google_calendar import configured_calendar
    calendar = configured_calendar()
    outbox = ProactiveOutbox(store, int(allowed))
    agent = configured_agent(store)
    checkins_enabled = os.getenv("UFMS_GENERIC_CHECKINS", "") == "1"
    for name, client in clients.items():
        threading.Thread(target=poll_loop, args=(name, client, store, int(allowed), calendar, outbox, agent),
                         daemon=True, name=f"poll-{name}").start()
    while True:
        generate_generic_checkins(outbox, enabled=checkins_enabled)
        dispatch_due(store, clients)
        dispatch_proactive(outbox, clients)
        time.sleep(10)


if __name__ == "__main__":
    main()
