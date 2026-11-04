import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bridge.gateway import (
    Store, MAX_ACTIVE_REMINDERS_PER_USER, MAX_NEW_REMINDERS_PER_24H
)


UTC = timezone.utc


class RateRetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=str(Path(self.temp.name)/"rate.sqlite3")
        self.store=Store(self.db)
        self.now=datetime(2026,11,4,14,tzinfo=UTC)

    def tearDown(self):
        self.temp.cleanup()

    def add(self, i=1, bot="tutor", chat=123, at=None, due=None):
        at = at or self.now
        return self.store.schedule(
            bot,chat,due or at+timedelta(days=1),f"Revisar {i}",f"manual-key-{i}",
            now=at
        )

    def test_24_hour_cap_shared_across_bots_even_after_cancellation(self):
        ids=[]
        for i in range(MAX_NEW_REMINDERS_PER_24H):
            ids.append(self.add(i,bot="tutor" if i%2 else "coach"))
        self.assertTrue(self.store.cancel(ids[0],"coach",123))
        with self.assertRaisesRegex(ValueError,"24 horas"):
            self.add(100)
        self.assertEqual(len(ids),MAX_NEW_REMINDERS_PER_24H)

    def test_active_cap_shared_across_bots_even_with_old_creations(self):
        for i in range(MAX_ACTIVE_REMINDERS_PER_USER):
            created=self.now-timedelta(days=i*2)
            self.add(i,bot="tutor" if i%2 else "coach",at=created,
                     due=self.now+timedelta(days=60))
        with self.assertRaisesRegex(ValueError,"ativos"):
            self.add(500)
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM reminders").fetchone()[0],
                             MAX_ACTIVE_REMINDERS_PER_USER)

    def test_replay_at_daily_limit_does_not_create_second_record(self):
        for i in range(MAX_NEW_REMINDERS_PER_24H):
            self.add(i)
        old=self.add(0)
        self.assertEqual(old,self.add(0))
        with self.assertRaises(ValueError):
            self.add(501)

    def test_reused_request_key_with_different_message_rejected(self):
        self.add(1)
        with self.assertRaisesRegex(ValueError,"reutilizada"):
            self.store.schedule("coach",123,self.now+timedelta(days=1),
                                "Mensagem modificada","manual-key-1",now=self.now)

    def test_replay_works_at_active_cap(self):
        for i in range(MAX_ACTIVE_REMINDERS_PER_USER):
            at=self.now-timedelta(days=i*2)
            self.add(i,at=at,due=self.now+timedelta(days=60))
        self.assertEqual(self.add(0,at=self.now-timedelta(days=100),
                                  due=self.now+timedelta(days=60)),1)

    def test_rejected_fields_do_not_write(self):
        inputs=[
            ("tutor",123,datetime(2026,11,5),"ok","key-1"),
            ("intruso",123,self.now,"ok","key-2"),
            ("tutor",123,self.now,"", "key-3"),
            ("tutor",123,self.now,"a"*501,"key-4"),
            ("tutor",-1,self.now,"ok","key-5"),
        ]
        for args in inputs:
            with self.assertRaises(ValueError):
                self.store.schedule(*args,now=self.now)
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM reminders").fetchone()[0],0)

    def test_utc_storage_even_with_negative_four_offset(self):
        local=timezone(timedelta(hours=-4))
        due=datetime(2026,11,5,9,tzinfo=local)
        self.store.schedule("tutor",123,due,"Revisar","utc-1",now=self.now)
        with self.store.connect() as db:
            saved=db.execute("SELECT due_utc FROM reminders").fetchone()[0]
        self.assertEqual(saved,datetime(2026,11,5,13,tzinfo=UTC).isoformat())

    def test_retention_is_dry_run_by_default(self):
        rid=self.add(1)
        with self.store.connect() as db:
            db.execute("""UPDATE reminders SET status='sent',sent_utc=?,finalized_utc=?
                WHERE id=?""", ((self.now-timedelta(days=31)).isoformat(),)*2+(rid,))
        report=self.store.purge_finalized(now=self.now)
        self.assertEqual(report["eligible_finalized"],1)
        self.assertEqual(report["deleted"],0)
        self.assertTrue(report["dry_run"])
        with self.store.connect() as db:
            self.assertIsNotNone(db.execute("SELECT id FROM reminders WHERE id=?", (rid,)).fetchone())

    def test_explicit_retention_preserves_unresolved_and_pending(self):
        old=(self.now-timedelta(days=45)).isoformat()
        r1=self.add(1)
        r2=self.add(2)
        r3=self.add(3)
        r4=self.add(4)
        with self.store.connect() as db:
            for rid, status in [(r1,"sent"),(r2,"cancelled"),(r3,"uncertain")]:
                db.execute("""UPDATE reminders SET status=?,finalized_utc=?
                    WHERE id=?""",(status,old,rid))
        report=self.store.purge_finalized(now=self.now,apply=True)
        self.assertEqual(report["deleted"],2)
        self.assertEqual(report["unresolved"],1)
        self.assertEqual(report["pending"],1)
        with self.store.connect() as db:
            remaining=[row[0] for row in db.execute("SELECT id FROM reminders ORDER BY id")]
        self.assertEqual(remaining,[r3,r4])

    def test_sent_yesterday_after_old_creation_is_preserved(self):
        rid=self.add(1,at=self.now-timedelta(days=100),due=self.now+timedelta(days=1))
        with self.store.connect() as db:
            db.execute("UPDATE reminders SET status='sent',finalized_utc=? WHERE id=?",
                       ((self.now-timedelta(days=1)).isoformat(),rid))
        self.assertEqual(self.store.purge_finalized(now=self.now,apply=True)["deleted"],0)

    def test_legacy_cancelled_without_finalized_date_not_deleted(self):
        rid=self.add(1)
        with self.store.connect() as db:
            db.execute("UPDATE reminders SET status='cancelled',finalized_utc=NULL WHERE id=?",(rid,))
        self.assertEqual(self.store.purge_finalized(now=self.now,apply=True)["deleted"],0)

    def test_invalid_retention_fails_without_mutation(self):
        self.add()
        with self.assertRaises(ValueError):
            self.store.purge_finalized(now=self.now,days=0,apply=True)
        with self.assertRaises(ValueError):
            self.store.purge_finalized(now=self.now,days=366,apply=True)

    def test_reminder_status_report_does_not_include_private_details(self):
        self.store.schedule("tutor",123,self.now+timedelta(days=1),
                            "Conteúdo pessoal","private-key-99",now=self.now)
        output=str(self.store.retention_report(now=self.now))
        self.assertNotIn("Conteúdo pessoal",output)
        self.assertNotIn("123",output)
        self.assertNotIn("private-key",output)

    def test_legacy_schema_migrates_without_deleting_data(self):
        path=str(Path(self.temp.name)/"legacy.db")
        with sqlite3.connect(path) as db:
            db.execute("""CREATE TABLE reminders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot TEXT NOT NULL,chat_id INTEGER NOT NULL,due_utc TEXT NOT NULL,
                body TEXT NOT NULL,request_key TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_utc TEXT NOT NULL,sent_utc TEXT,
                claimed_utc TEXT)""")
            db.execute("""INSERT INTO reminders(
                bot,chat_id,due_utc,body,request_key,created_utc)
                VALUES(?,?,?,?,?,?)""", ("tutor",123,self.now.isoformat(),"retido",
                                        "legacy-key",self.now.isoformat()))
        migrated=Store(path)
        with migrated.connect() as db:
            cols={row["name"] for row in db.execute("PRAGMA table_info(reminders)")}
            row=db.execute("SELECT body FROM reminders").fetchone()
        self.assertIn("finalized_utc",cols)
        self.assertEqual(row["body"],"retido")


if __name__=="__main__":
    unittest.main()
