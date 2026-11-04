import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from urllib.error import HTTPError
import traceback
import io
from pathlib import Path

from bridge.gateway import Store, Telegram, dispatch_due, handle_update, parse_time


class FakeTelegram:
    def __init__(self):
        self.messages = []

    def send(self, chat_id, text):
        self.messages.append((chat_id, text))


class FakeCalendar:
    def __init__(self):
        self.called = []

    def create_event(self, start, end, title, key):
        self.called.append((start, end, title, key))
        return "fakeevent123"


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(str(Path(self.tmp.name) / "test.sqlite"))
        self.bot = FakeTelegram()
        self.now = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.tmp.cleanup()

    def update(self, user=123, text="/status", n=1, private=True):
        return {"update_id": n, "message": {
            "from": {"id": user}, "chat": {"id": user, "type": "private" if private else "group"},
            "text": text,
        }}

    def send(self, text, n=1, user=123, calendar=None):
        handle_update("tutor", self.update(user, text, n), self.store, self.bot,
                      123, calendar, now=self.now)

    def test_unauthorized_silent(self):
        self.send("/lembrete 2026-11-05T09:00-04:00 | teste", user=456)
        self.assertEqual(self.bot.messages, [])
        self.assertEqual(self.store.due(self.now + timedelta(days=3)), [])

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            parse_time("2026-11-05T19:00", now=self.now)

    def test_reminder_and_dedup(self):
        self.send("/lembrete 2026-11-05T09:00-04:00 | revisar", n=7)
        self.send("/lembrete 2026-11-05T09:00-04:00 | revisar", n=7)
        self.assertEqual(self.store.pending("tutor", 123), 1)
        self.assertEqual(len(self.bot.messages), 1)

    def test_pause_resume_and_delivery(self):
        self.send("/lembrete 2026-11-05T09:00-04:00 | revisar", n=1)
        self.send("/pausar", n=2)
        self.assertEqual(dispatch_due(self.store, {"tutor": self.bot, "coach": self.bot},
                                      self.now + timedelta(days=2)), 0)
        self.send("/retomar", n=3)
        self.assertEqual(dispatch_due(self.store, {"tutor": self.bot, "coach": self.bot},
                                      self.now + timedelta(days=2)), 1)
        self.assertEqual(self.store.pending("tutor", 123), 0)

    def test_cancel_scoped(self):
        due = self.now + timedelta(days=2)
        rid = self.store.schedule("tutor", 123, due, "teste", "unique1")
        self.assertFalse(self.store.cancel(rid, "coach", 123))
        self.assertFalse(self.store.cancel(rid, "tutor", 999))
        self.assertTrue(self.store.cancel(rid, "tutor", 123))

    def test_calendar_not_authorized(self):
        self.send("/evento 2026-11-05T09:00-04:00 | 2026-11-05T10:00-04:00 | Estudo", n=2)
        self.assertIn("não autorizada", self.bot.messages[-1][1])

    def test_calendar_event_authorized(self):
        calendar = FakeCalendar()
        self.send("/evento 2026-11-05T09:00-04:00 | 2026-11-05T10:00-04:00 | Estudo",
                  n=2, calendar=calendar)
        self.assertEqual(len(calendar.called), 1)
        self.assertIn("confirmado", self.bot.messages[-1][1])

    def test_no_group_chat(self):
        handle_update("coach", self.update(private=False), self.store,
                      self.bot, 123, now=self.now)
        self.assertEqual(self.bot.messages, [])

    def test_telegram_token_not_exposed_in_transport_failure(self):
        secret = "123456:TOP_SECRET_NEVER_LOG"
        client = Telegram(secret)
        failing_url = f"https://api.telegram.org/bot{secret}/sendMessage"
        http_error = HTTPError(failing_url, 401, "Unauthorized", {}, io.BytesIO(b""))
        with patch("bridge.gateway.request.urlopen", side_effect=http_error):
            try:
                client.send(123, "Privado")
            except RuntimeError as exc:
                message = str(exc)
                stack = "".join(traceback.format_exception(exc))
                self.assertNotIn(secret, message)
                self.assertNotIn(secret, stack)
            else:
                self.fail("A chamada deve falhar")

    def test_telegram_malformed_response_is_not_confirmed(self):
        client = Telegram("fake-token")
        class FakeResult:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'{"ok":false}'
        with patch("bridge.gateway.request.urlopen", return_value=FakeResult()):
            with self.assertRaises(RuntimeError):
                client.send(123, "teste")

    def test_distinct_agents_and_idempotent_store(self):
        due = self.now + timedelta(days=2)
        a = self.store.schedule("tutor", 123, due, "t", "t-1")
        b = self.store.schedule("coach", 123, due, "c", "c-1")
        self.assertNotEqual(a, b)
        self.assertEqual(self.store.schedule("tutor", 123, due, "t", "t-1"), a)


if __name__ == "__main__":
    unittest.main()
