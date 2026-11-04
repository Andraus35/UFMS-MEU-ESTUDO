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
