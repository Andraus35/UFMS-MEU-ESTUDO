import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from bridge.gateway import Store
from bridge.proactive import ProactiveOutbox, dispatch_proactive
from bridge.checkins import generate_generic_checkins


class Stub:
    def __init__(self):
        self.items=[]
    def send(self,who,body):
        self.items.append((who,body))


class GenericCheckinTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=Store(str(Path(self.tmp.name)/"test.sqlite"))
        self.queue=ProactiveOutbox(self.store,123)
        self.client=Stub()
        self.clients={"tutor":self.client,"coach":self.client}

    def tearDown(self):
        self.tmp.cleanup()

    def when(self,hour,minute=0):
        # Campo Grande UTC-4 no edital 2026
        return datetime(2026,11,5,hour+4,minute,tzinfo=timezone.utc)

    def test_off_by_default_even_if_student_opted_in(self):
        self.queue.set_enabled(True)
        self.assertEqual(generate_generic_checkins(self.queue,now=self.when(18)),0)

    def test_no_consent_never_scheduled(self):
        self.assertEqual(generate_generic_checkins(
            self.queue,enabled=True,now=self.when(18)),0)
        self.assertEqual(self.queue.unresolved_counts(),{})

    def test_tutor_and_coach_generate_only_in_their_slots(self):
        self.queue.set_enabled(True)
        self.assertEqual(generate_generic_checkins(self.queue,enabled=True,now=self.when(18)),1)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.when(18)),1)
        self.assertIn("Tutor UFMS",self.client.items[0][1])
        self.assertEqual(generate_generic_checkins(self.queue,enabled=True,now=self.when(19)),1)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.when(19)),1)
        self.assertIn("Coach UFMS",self.client.items[1][1])

    def test_restart_cannot_queue_missed_checkin(self):
        self.queue.set_enabled(True)
        self.assertEqual(generate_generic_checkins(
            self.queue,enabled=True,now=self.when(18,15)),0)

    def test_idempotent_within_slot(self):
        self.queue.set_enabled(True)
        self.assertEqual(generate_generic_checkins(
            self.queue,enabled=True,now=self.when(18)),1)
        self.assertEqual(generate_generic_checkins(
            self.queue,enabled=True,now=self.when(18,1)),1)
        with self.store.connect() as db:
            count=db.execute("SELECT count(*) AS total FROM proactive_notifications").fetchone()["total"]
        self.assertEqual(count,1)

    def test_revocation_while_pending_blocks_later_send(self):
        self.queue.set_enabled(True)
        generate_generic_checkins(self.queue,enabled=True,now=self.when(18))
        self.queue.set_enabled(False)
        self.queue.set_enabled(True)
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.when(18)),0)
        self.assertEqual(self.client.items,[])
        # Mesmo dia, o mesmo ID cancelado não deve ser enviado.
        generate_generic_checkins(self.queue,enabled=True,now=self.when(18,2))
        self.assertEqual(dispatch_proactive(self.queue,self.clients,self.when(18,2)),0)

    def test_no_invented_progress(self):
        self.queue.set_enabled(True)
        generate_generic_checkins(self.queue,enabled=True,now=self.when(19))
        with self.store.connect() as db:
            row=db.execute("SELECT body,reason FROM proactive_notifications").fetchone()
        self.assertNotIn("você acertou",row["body"].lower())
        self.assertIn("sem evidência",row["reason"])


if __name__=="__main__":
    unittest.main()
