import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from bridge.google_calendar import GoogleCalendar


class CalendarTests(unittest.TestCase):
    def test_requires_explicit_secondary_calendar(self):
        bridge = GoogleCalendar("id", "secret", "refresh", "primary")
        with self.assertRaises(ValueError):
            bridge.create_event(datetime.now(timezone.utc), datetime.now(timezone.utc),
                                "Teste", "key")

    def test_event_key_stable(self):
        client = GoogleCalendar("id", "secret", "refresh", "study@example.com")
        results = []

        def fake_post(path, payload):
            results.append((path, payload))
            return {"id": payload["id"]}

        with patch.object(client, "_post", side_effect=fake_post):
            first = client.create_event(datetime.now(timezone.utc), datetime.now(timezone.utc),
                                        "Estudo", "tutor:42")
            second = client.create_event(datetime.now(timezone.utc), datetime.now(timezone.utc),
                                         "Estudo", "tutor:42")
        self.assertEqual(first, second)
        self.assertEqual(results[0][0], "/calendars/study%40example.com/events")
        self.assertEqual(len(first), 32)


if __name__ == "__main__":
    unittest.main()


class CalendarAdversarialTests(unittest.TestCase):
    def client(self):
        return GoogleCalendar("id","secret","refresh","study@example.com")

    def when(self):
        at=datetime(2026,11,5,14,tzinfo=timezone.utc)
        return at, at.replace(hour=15)

    def test_id_is_google_base32hex_for_multiple_keys(self):
        import re
        client=self.client()
        ids=[]
        def fake_post(path,payload):
            ids.append(payload["id"])
            return {"id": payload["id"]}
        with patch.object(client,"_post",side_effect=fake_post):
            a,b=self.when()
            for i in range(128):
                client.create_event(a,b,"UFMS",f"tutor:{i}")
        self.assertTrue(all(re.fullmatch("[0-9a-v]{32}",x) for x in ids))
        self.assertEqual(len(set(ids)),128)

    def test_conflict_only_valid_if_existing_event_matches(self):
        import io
        from urllib.error import HTTPError
        client=self.client()
        a,b=self.when()
        payloads=[]
        def conflict(path,payload):
            payloads.append(payload)
            raise HTTPError(url="https://google.example",code=409,msg="Conflict",hdrs=None,fp=io.BytesIO(b""))
        def exists(event_id):
            return {**payloads[-1], "start":{"dateTime": a.isoformat()},
                    "end":{"dateTime": b.isoformat()}, "status":"confirmed"}
        with patch.object(client,"_post",side_effect=conflict),patch.object(client,"_get_event",side_effect=exists):
            returned=client.create_event(a,b,"UFMS","coach:123")
        self.assertEqual(returned,payloads[0]["id"])

    def test_conflicting_event_not_falsely_confirmed(self):
        import io
        from urllib.error import HTTPError
        client=self.client()
        a,b=self.when()
        def conflict(path,payload):
            raise HTTPError(url="https://google.example",code=409,msg="Conflict",hdrs=None,fp=io.BytesIO(b""))
        with patch.object(client,"_post",side_effect=conflict),patch.object(client,"_get_event",return_value={
            "id":"different","summary":"Outro evento",
            "start":{"dateTime":a.isoformat()},
            "end":{"dateTime":b.isoformat()}}):
            with self.assertRaises(RuntimeError):
                client.create_event(a,b,"UFMS","coach:123")

    def test_invalid_timezone_rejected_without_http(self):
        client=self.client()
        with patch.object(client,"_post") as remote:
            a=datetime(2026,11,5,14)
            b=datetime(2026,11,5,15)
            with self.assertRaises(ValueError):
                client.create_event(a,b,"UFMS","tutor:20")
            remote.assert_not_called()

    def test_interval_validated_without_http(self):
        client=self.client()
        with patch.object(client,"_post") as remote:
            a,b=self.when()
            with self.assertRaises(ValueError):
                client.create_event(b,a,"UFMS","tutor:20")
            remote.assert_not_called()
