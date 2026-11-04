import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from bridge.gateway import Store
from bridge.proactive import (
    ProactiveOutbox, dispatch_proactive, DAILY_CAP, COOLDOWN, LOCAL
)


class Stub:
    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    def send(self, chat, body):
        self.sent.append((chat, body))
        if self.fail:
            raise TimeoutError("Ambiguous Telegram ACK")


class ProactiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(str(Path(self.tmp.name) / "outbox.sqlite3"))
        self.queue = ProactiveOutbox(self.store, 123)
        self.now = datetime(2026, 11, 4, 13, tzinfo=timezone.utc) # 09:00 Campo Grande
        self.client = Stub()
        self.clients = {"tutor": self.client, "coach": self.client}

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, i=1, bot="tutor", due=None, category="review"):
        return self.queue.enqueue(
            bot=bot, user_id=123, category=category,
            due=due or self.now, body="Revisão autorizada",
            reason="Observação registrada no estudo",
            source_ref="event:valid-001", request_key=f"event-{i}",
            now=self.now
        )

    def test_no_opt_in_no_send(self):
        with self.assertRaises(PermissionError):
            self.add()
        self.assertEqual(dispatch_proactive(self.queue, self.clients, self.now), 0)
        self.assertEqual(self.client.sent, [])

    def test_opt_in_and_delivery(self):
        self.queue.set_enabled(True)
        rid = self.add()
        self.assertEqual(dispatch_proactive(self.queue, self.clients, self.now), 1)
        self.assertEqual(self.queue.status(rid), "sent")
        self.assertEqual(self.client.sent, [(123, "Revisão autorizada")])
        self.assertEqual(dispatch_proactive(self.queue, self.clients, self.now), 0)

    def test_user_unauthorized(self):
        self.assertRaises(PermissionError, self.queue.enqueue,
                          bot="tutor",user_id=999,category="review",due=self.now,
                          body="ok",reason="Porque existe evidência",source_ref="event:001",request_key="ev-001",
                          now=self.now)

    def test_bot_and_category_rejected(self):
        self.assertRaises(PermissionError, self.add, 1, "attacker")
        self.assertRaises(ValueError, self.add, 1, "tutor", None, "spam")

    def test_idempotency_and_conflicting_key(self):
        self.queue.set_enabled(True)
        first = self.add()
        self.assertEqual(first, self.add())
        with self.assertRaises(ValueError):
            self.queue.enqueue(
                bot="coach",user_id=123,category="review",due=self.now,body="Alterado",
                reason="Porque existe evidência",source_ref="event:valid-001",
                request_key="event-1",now=self.now)

    def test_quiet_hours_and_release(self):
        self.queue.set_enabled(True)
        rid = self.add()
        late = self.now.replace(hour=2) + timedelta(days=1)  # 22:00 local, APÓS vencimento
        self.assertEqual(dispatch_proactive(self.queue, self.clients, late), 0)
        self.assertEqual(self.queue.status(rid), "pending")
        self.assertEqual(dispatch_proactive(self.queue, self.clients, self.now), 1)

    def test_cooldown(self):
        self.queue.set_enabled(True)
        first = self.add(1)
        second = self.add(2)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now),1)
        self.assertEqual(self.queue.status(first),"sent")
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now + COOLDOWN - timedelta(seconds=1)),0)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now + COOLDOWN),1)
        self.assertEqual(self.queue.status(second),"sent")

    def test_daily_cap(self):
        self.queue.set_enabled(True)
        for i in range(DAILY_CAP + 1):
            self.add(i)
        for i in range(DAILY_CAP):
            self.assertEqual(dispatch_proactive(self.queue,self.clients,
                             self.now + i * COOLDOWN),1)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,
                         self.now + DAILY_CAP * COOLDOWN),0)
        self.assertEqual(len(self.client.sent),DAILY_CAP)

    def test_pause_blocks(self):
        self.queue.set_enabled(True)
        self.add()
        self.store.set_paused(True)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now),0)
        self.store.set_paused(False)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now),1)

    def test_uncertain_no_blind_retry(self):
        self.queue.set_enabled(True)
        rid=self.add()
        bad=Stub(fail=True)
        self.assertEqual(dispatch_proactive(self.queue,
                         {"tutor":bad,"coach":bad},self.now),0)
        self.assertEqual(self.queue.status(rid),"uncertain")
        self.assertEqual(dispatch_proactive(self.queue,
                         self.clients,self.now + COOLDOWN),0)
        self.assertEqual(len(self.client.sent),0)

    def test_crash_after_claim_not_resent(self):
        self.queue.set_enabled(True)
        rid=self.add()
        claim=self.queue.claim_next(self.now)
        self.assertEqual(claim["id"],rid)
        # simula processo interrompido antes de persistir confirmação
        restored=ProactiveOutbox(Store(self.store.path),123)
        self.assertEqual(dispatch_proactive(restored,self.clients,
                         self.now + COOLDOWN),0)
        self.assertEqual(restored.status(rid),"sending")

    def test_distinct_bots_same_cap(self):
        self.queue.set_enabled(True)
        self.add(1,"tutor")
        self.add(2,"coach")
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now),1)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,
                         self.now+COOLDOWN),1)

    def test_untrusted_missing_evidence_rejected(self):
        with self.assertRaises(ValueError):
            self.queue.enqueue(
                bot="coach",user_id=123,category="checkin",due=self.now,
                body="Mensagem",reason="",source_ref="",
                request_key="source-12",now=self.now)

    def test_sql_claim_once(self):
        self.queue.set_enabled(True)
        self.add()
        first=self.queue.claim_next(self.now)
        second=self.queue.claim_next(self.now)
        self.assertIsNotNone(first)
        self.assertIsNone(second)

    def test_disabled_after_queue_does_not_dispatch(self):
        self.queue.set_enabled(True)
        rid=self.add()
        self.queue.set_enabled(False)
        self.assertEqual(self.queue.status(rid),"cancelled")
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now),0)
        self.queue.set_enabled(True)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now),0)
        new_id=self.add(2)
        self.assertNotEqual(new_id,rid)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.now),1)

    def test_due_must_have_timezone(self):
        with self.assertRaises(ValueError):
            self.add(due=datetime(2026,11,4,13))

    def test_only_future_due(self):
        with self.assertRaises(ValueError):
            self.add(due=self.now-timedelta(days=2))


if __name__ == "__main__":
    unittest.main()
