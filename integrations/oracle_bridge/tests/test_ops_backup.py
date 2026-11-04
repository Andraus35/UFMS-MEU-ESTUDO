import io
import os
import shutil
import sqlite3
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bridge.gateway import Store
from bridge.ops_backup import (
    backup_database, restore_database, verify_backup, _check_database
)
from bridge.runtime_lock import acquire_runtime_lock


RECIPIENT = "age1" + "a" * 58


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.secure = self.base / "encrypted"
        self.scratch = self.base / "tmpfs-test"
        for p in (self.secure, self.scratch):
            p.mkdir(mode=0o700)
            p.chmod(0o700)
        self.db = self.base / "ufms.sqlite3"
        self.store = Store(str(self.db))
        self.store.schedule("tutor", 123, __import__("datetime").datetime(
            2026,11,5,tzinfo=__import__("datetime").timezone.utc),
            "Dado sensível", "key-b1")
        self.archive = self.secure / "snapshot.age"
        self.identity = self.base / "identity"
        self.identity.write_text("AGE-SECRET-KEY-FAKE")
        self.identity.chmod(0o600)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def fake_age(argv):
        # Unit tests validate workflow, not actual encryption strength.
        # Real age integration is exercised separately by Docker CI.
        if "-d" in argv:
            dst = Path(argv[argv.index("-o")+1])
            shutil.copyfile(Path(argv[-1]),dst)
        else:
            dst = Path(argv[argv.index("-o")+1])
            shutil.copyfile(Path(argv[-1]),dst)

    def test_backup_never_publishes_plaintext_and_cleans_temp(self):
        with patch("bridge.ops_backup._age", side_effect=self.fake_age):
            result = backup_database(str(self.db),str(self.archive),
                                     RECIPIENT,scratch_dir=str(self.scratch))
        self.assertTrue(result["created"])
        self.assertEqual(os.listdir(self.scratch),[])
        self.assertEqual(list(self.secure.glob(".ufms-incomplete-*")),[])
        self.assertEqual(stat.S_IMODE(self.archive.stat().st_mode),0o600)

    def test_existing_archive_not_overwritten(self):
        self.archive.write_text("keep")
        self.archive.chmod(0o600)
        with patch("bridge.ops_backup._age") as called:
            with self.assertRaises(FileExistsError):
                backup_database(str(self.db),str(self.archive),
                                RECIPIENT,scratch_dir=str(self.scratch))
            called.assert_not_called()
        self.assertEqual(self.archive.read_text(),"keep")

    def test_invalid_recipient_never_calls_age(self):
        with patch("bridge.ops_backup._age") as called:
            with self.assertRaises(ValueError):
                backup_database(str(self.db),str(self.archive),
                                "not-an-age-key",scratch_dir=str(self.scratch))
            called.assert_not_called()

    def test_symlink_database_refused(self):
        link=self.base/"symlink.sqlite3"
        link.symlink_to(self.db)
        with self.assertRaises(ValueError):
            backup_database(str(link),str(self.archive),
                            RECIPIENT,scratch_dir=str(self.scratch))

    def test_insecure_backup_directory_refused(self):
        self.secure.chmod(0o755)
        with self.assertRaises(PermissionError):
            backup_database(str(self.db),str(self.archive),
                            RECIPIENT,scratch_dir=str(self.scratch))

    def test_failed_encryption_removes_temp_and_no_final(self):
        def fail(argv):
            raise RuntimeError("age failed")
        with patch("bridge.ops_backup._age",side_effect=fail):
            with self.assertRaises(RuntimeError):
                backup_database(str(self.db),str(self.archive),
                                RECIPIENT,scratch_dir=str(self.scratch))
        self.assertFalse(self.archive.exists())
        self.assertEqual(os.listdir(self.scratch),[])
        self.assertEqual(os.listdir(self.secure),[])

    def test_verify_returns_only_non_sensitive_fields(self):
        with patch("bridge.ops_backup._age",side_effect=self.fake_age):
            backup_database(str(self.db),str(self.archive),
                            RECIPIENT,scratch_dir=str(self.scratch))
            data=verify_backup(str(self.archive),str(self.identity),
                               scratch_dir=str(self.scratch))
        self.assertTrue(data["verified"])
        self.assertNotIn("Dado sensível",str(data))
        self.assertEqual(os.listdir(self.scratch),[])

    def test_missing_confirmation_rejects_restore_before_age(self):
        self.archive.write_bytes(b"fake")
        with patch("bridge.ops_backup._age") as called:
            with self.assertRaises(PermissionError):
                restore_database(str(self.archive),str(self.db),str(self.identity))
            called.assert_not_called()

    def test_restore_rejects_running_gateway(self):
        with patch("bridge.ops_backup._age",side_effect=self.fake_age):
            backup_database(str(self.db),str(self.archive),
                            RECIPIENT,scratch_dir=str(self.scratch))
        lock=acquire_runtime_lock(str(self.db))
        try:
            with self.assertRaisesRegex(RuntimeError,"Banco em uso"):
                restore_database(str(self.archive),str(self.db),str(self.identity),
                                 confirm=True,replace_existing=True)
        finally:
            os.close(lock)

    def test_restore_rejects_existing_without_extra_flag(self):
        with patch("bridge.ops_backup._age",side_effect=self.fake_age):
            backup_database(str(self.db),str(self.archive),
                            RECIPIENT,scratch_dir=str(self.scratch))
            with self.assertRaises(PermissionError):
                restore_database(str(self.archive),str(self.db),str(self.identity),
                                 confirm=True)

    def test_restore_rejects_bad_identity_permissions(self):
        self.archive.write_bytes(b"fake")
        self.identity.chmod(0o644)
        with self.assertRaises(PermissionError):
            restore_database(str(self.archive),str(self.base/"restore.sqlite3"),
                             str(self.identity),confirm=True)

    def test_restore_does_not_touch_db_with_wal_sidecar(self):
        with patch("bridge.ops_backup._age",side_effect=self.fake_age):
            backup_database(str(self.db),str(self.archive),
                            RECIPIENT,scratch_dir=str(self.scratch))
        wal=Path(str(self.db)+"-wal")
        wal.touch()
        try:
            with self.assertRaisesRegex(RuntimeError,"WAL/SHM"):
                restore_database(str(self.archive),str(self.db),str(self.identity),
                                 confirm=True,replace_existing=True)
        finally:
            wal.unlink()

    def test_round_trip_restores_schema_and_message(self):
        with patch("bridge.ops_backup._age",side_effect=self.fake_age):
            backup_database(str(self.db),str(self.archive),
                            RECIPIENT,scratch_dir=str(self.scratch))
            restored=self.base/"restored.sqlite3"
            result=restore_database(str(self.archive),str(restored),str(self.identity),
                                    confirm=True)
        self.assertTrue(result["restored"])
        _check_database(restored)
        with sqlite3.connect(restored) as conn:
            body=conn.execute("SELECT body FROM reminders").fetchone()[0]
        self.assertEqual(body,"Dado sensível")
        self.assertEqual(stat.S_IMODE(restored.stat().st_mode),0o600)

    def test_integrity_check_rejects_empty_archive(self):
        self.archive.write_bytes(b"badciphertext")
        def fake_invalid(argv):
            Path(argv[argv.index("-o")+1]).write_bytes(b"not a sqlite file")
        with patch("bridge.ops_backup._age",side_effect=fake_invalid):
            with self.assertRaises((ValueError,sqlite3.DatabaseError)):
                verify_backup(str(self.archive),str(self.identity),
                              scratch_dir=str(self.scratch))
        self.assertEqual(os.listdir(self.scratch),[])

    def test_restore_does_not_overwrite_with_bad_archive(self):
        original=self.db.read_bytes()
        self.archive.write_bytes(b"fake")
        def bad_archive(argv):
            Path(argv[argv.index("-o")+1]).write_bytes(b"not sqlite")
        with patch("bridge.ops_backup._age",side_effect=bad_archive):
            with self.assertRaises(sqlite3.DatabaseError):
                restore_database(str(self.archive),str(self.db),str(self.identity),
                                 confirm=True,replace_existing=True)
        self.assertEqual(self.db.read_bytes(),original)


if __name__ == "__main__":
    unittest.main()
