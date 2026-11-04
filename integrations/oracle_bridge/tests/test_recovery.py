import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bridge.gateway import Store, dispatch_due
from bridge.proactive import ProactiveOutbox


class TelegramFake:
    def __init__(self, failure=False):
        self.attempts = []
        self.failure = failure

    def send(self, chat, body):
        self.attempts.append((chat, body))
        if self.failure:
            raise TimeoutError("ACK ambíguo")


class ReminderRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name)/"db.sqlite3")
        self.store = Store(self.path)
        self.now = datetime(2026, 11, 4, 12, tzinfo=timezone.utc)
        self.client = TelegramFake()

    def tearDown(self):
        self.temp.cleanup()

    def put(self):
        return self.store.schedule("tutor", 123, self.now, "Mensagem", "request-key-100")

    def test_no_replay_after_ambiguous_ack(self):
        rid = self.put()
        failed = TelegramFake(failure=True)
        self.assertEqual(dispatch_due(self.store, {"tutor":failed}, self.now),0)
        self.assertEqual(len(failed.attempts),1)
        self.assertEqual(len(self.store.unresolved()),1)
        self.assertEqual(dispatch_due(self.store,{"tutor":self.client},self.now),0)
        self.assertEqual(self.client.attempts,[])
        self.assertTrue(self.store.resolve_uncertain(rid,"delivered"))
        self.assertFalse(self.store.resolve_uncertain(rid,"delivered"))

    def test_crash_mid_send_is_not_replayed(self):
        rid = self.put()
        r = self.store.claim_due(self.now)
        self.assertEqual(r["id"],rid)
        restarted = Store(self.path)
        self.assertEqual(dispatch_due(restarted,{"tutor":self.client},self.now),0)
        self.assertEqual(self.client.attempts,[])
        self.assertEqual(restarted.unresolved()[0]["status"],"sending")
        self.assertTrue(restarted.resolve_uncertain(rid,"cancelled"))

    def test_claim_once_across_connections(self):
        rid=self.put()
        second=Store(self.path)
        self.assertEqual(self.store.claim_due(self.now)["id"],rid)
        self.assertIsNone(second.claim_due(self.now))

    def test_migration_from_old_sqlite(self):
        import sqlite3
        oldpath=str(Path(self.temp.name)/"legacy.sqlite3")
        with sqlite3.connect(oldpath) as db:
            db.execute("""CREATE TABLE reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot TEXT NOT NULL,chat_id INTEGER NOT NULL,due_utc TEXT NOT NULL,
                body TEXT NOT NULL,request_key TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'pending',
                created_utc TEXT NOT NULL,sent_utc TEXT)""")
        migrated=Store(oldpath)
        with migrated.connect() as db:
            cols={row["name"] for row in db.execute("PRAGMA table_info(reminders)")}
        self.assertIn("claimed_utc",cols)

    def test_reconcile_does_not_expose_message(self):
        rid=self.put()
        self.store.claim_due(self.now)
        data=str(self.store.unresolved())
        self.assertNotIn("Mensagem",data)
        self.assertNotIn("123",data)
        self.assertTrue(self.store.resolve_uncertain(rid,"cancelled"))

    def test_invalid_reconciliation_fails_closed(self):
        rid=self.put()
        self.store.claim_due(self.now)
        with self.assertRaises(ValueError):
            self.store.resolve_uncertain(rid,"retry")

    def test_proactive_reconciliation_excludes_payload(self):
        outbox=ProactiveOutbox(self.store,123)
        outbox.set_enabled(True)
        rid=outbox.enqueue(bot="coach",user_id=123,category="checkin",
            due=self.now,body="Conteúdo sensível",reason="Relato confirmado",
            source_ref="event:valid-001",request_key="coach-checkin-1",now=self.now)
        outbox.set_enabled(True)
        item=outbox.claim_next(self.now)
        self.assertEqual(item["id"],rid)
        self.assertNotIn("sensível",str(outbox.unresolved()))
        self.assertTrue(outbox.resolve_uncertain(rid,"cancelled"))
        self.assertFalse(outbox.resolve_uncertain(rid,"delivered"))


if __name__=="__main__":
    unittest.main()
