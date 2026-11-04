"""Deterministic pagination and mixed-age governance readback tests."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_live_governance as live
import trusted_app_check as app

BASE = "repos/Andraus35/UFMS-MEU-ESTUDO/commits/" + "c"*40 + "/check-runs?per_page=100"


def paged(total=102, duplicate=False, inconsistent=False, omit_last=False, short=False):
    def get(path):
        assert path == BASE or path == BASE + "&page=2"
        page = 1 if path == BASE else 2
        if page == 2 and omit_last:
            raise OSError("network outage")
        ids = list(range(1, 101)) if page == 1 else list(range(101, total+1))
        if short and page == 1:
            ids = ids[:99]
        if duplicate and page == 2:
            ids[0] = 99
        return {"total_count": total + (1 if inconsistent and page == 2 else 0),
                "check_runs": [{"id": i, "name": "irrelevant"} for i in ids]}
    return get


class CheckHistoryPaginationTests(unittest.TestCase):
    def test_live_reads_second_page(self):
        result = live.complete_check_runs(paged(), BASE)
        self.assertEqual(len(result), 102)
        self.assertEqual(result[-1]["id"], 102)

    def test_app_reads_second_page(self):
        result = app.complete_check_runs(paged(), BASE)
        self.assertEqual(len(result), 102)

    def test_live_rejects_duplicate(self):
        with self.assertRaisesRegex(live.EvidenceMissing, "duplicate"):
            live.complete_check_runs(paged(duplicate=True), BASE)

    def test_app_rejects_duplicate(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            app.complete_check_runs(paged(duplicate=True), BASE)

    def test_live_rejects_changing_count(self):
        with self.assertRaisesRegex(live.EvidenceMissing, "count changed"):
            live.complete_check_runs(paged(inconsistent=True), BASE)

    def test_app_rejects_changing_count(self):
        with self.assertRaisesRegex(ValueError, "count changed"):
            app.complete_check_runs(paged(inconsistent=True), BASE)

    def test_live_rejects_short_first_page(self):
        with self.assertRaisesRegex(live.EvidenceMissing, "short"):
            live.complete_check_runs(paged(short=True), BASE)

    def test_app_rejects_short_first_page(self):
        with self.assertRaisesRegex(ValueError, "short"):
            app.complete_check_runs(paged(short=True), BASE)

    def test_live_rejects_missing_page(self):
        with self.assertRaisesRegex(live.EvidenceMissing, "page unavailable"):
            live.complete_check_runs(paged(omit_last=True), BASE)

    def test_app_rejects_missing_page(self):
        with self.assertRaisesRegex(ValueError, "page unavailable"):
            app.complete_check_runs(paged(omit_last=True), BASE)


if __name__ == "__main__":
    unittest.main()
