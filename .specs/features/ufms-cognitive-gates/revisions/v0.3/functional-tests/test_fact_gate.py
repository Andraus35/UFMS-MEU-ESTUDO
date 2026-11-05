"""C25 adversarial tests on true source spans and false conclusions."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts"))
from chunk_edital import read_pages
from fact_gate import FACTS, CONFLICT_ID, check_critical_claim
from source_gate import SOURCE, PINNED_SOURCE_BLOB

PAGES = dict(read_pages((ROOT / SOURCE).read_text(encoding="utf-8")))


def citation(page, anchor):
    pos = PAGES[page].index(anchor)
    return {
        "source": SOURCE, "source_sha": PINNED_SOURCE_BLOB, "page": page,
        "span": {"start": pos, "end": pos + len(anchor)}, "quote": anchor,
    }


def claim(fact_id, value):
    return {
        "fact_id": fact_id,
        "claimed_value": value,
        "citations": [citation(page, anchor) for page, anchor in FACTS[fact_id]["basis"]],
    }


class C25CuratedFactsTests(unittest.TestCase):
    def blocked(self, proposal, code="CLAIM_UNSUPPORTED", root=ROOT):
        out = check_critical_claim(proposal, root=root)
        self.assertEqual(out["reason_code"], code, out)
        self.assertIn(out["decision"], ("DENY", "NEEDS_EVIDENCE"))
        self.assertEqual(out["source_refs"], [])
        self.assertFalse(out["publication_authorized"])
        self.assertEqual(out["external_effects"], 0)

    def test_50_percent_literal_is_supported_not_published(self):
        out = check_critical_claim(claim("objective_minimum_percent", 50))
        self.assertEqual(out["decision"], "FACT_MATCHED")
        self.assertEqual(out["semantic_support"], "CURATED_FACT_MATCH_ONLY")
        self.assertEqual(out["source_refs"][0]["page"], 10)
        self.assertFalse(out["publication_authorized"])

    def test_60_percent_contradicts_true_10_1_quote(self):
        self.blocked(claim("objective_minimum_percent", 60))

    def test_10_1_true_quote_cannot_justify_zero_english(self):
        p = claim("objective_minimum_percent", 50)
        p["fact_id"] = "may_pass_with_zero_in_english"
        p["claimed_value"] = True
        self.blocked(p)

    def test_zero_english_false_claim_rejected_with_correct_anchors(self):
        self.blocked(claim("may_pass_with_zero_in_english", True))

    def test_zero_area_rule_is_verifiable(self):
        out = check_critical_claim(claim("zero_in_any_area_eliminates", True))
        self.assertEqual(out["decision"], "FACT_MATCHED")
        self.assertFalse(out["publication_authorized"])

    def test_english_rule_requires_both_independent_anchors(self):
        p = claim("may_pass_with_zero_in_english", False)
        self.assertEqual(check_critical_claim(p)["decision"], "FACT_MATCHED")
        p["citations"] = p["citations"][:1]
        self.blocked(p)

    def test_irrelevant_real_quote_does_not_support_different_rule(self):
        p = claim("objective_minimum_percent", 50)
        p["fact_id"] = "zero_in_any_area_eliminates"
        p["claimed_value"] = True
        self.blocked(p)

    def test_missing_malformed_wrong_sha_and_page(self):
        base = claim("objective_minimum_percent", 50)
        variants = [
            dict(base, citations=[]),
            dict(base, citations="incorrect"),
            dict(base, citations=None),
            dict(base, citations=[dict(base["citations"][0], source_sha="0" * 40)]),
            dict(base, citations=[dict(base["citations"][0], page=11)]),
        ]
        for p in variants:
            with self.subTest(p=str(p)[:65]):
                self.blocked(p)

    def test_missing_unknown_fact_refused(self):
        self.blocked({"fact_id": "fabricated_passing_rule", "claimed_value": 123,
                      "citations": claim("objective_minimum_percent", 50)["citations"]})
        self.blocked(None)

    def test_type_confusion_bool_and_integer_refused(self):
        self.blocked(claim("objective_minimum_percent", True))
        self.blocked(claim("zero_in_any_area_eliminates", 1))

    def test_appeal_date_conflict_never_silently_fixed(self):
        p = {
            "fact_id": CONFLICT_ID,
            "claimed_value": "11 e 12/01/2027",
            "citations": [citation(13, "11 e 12/01/2027")],
        }
        self.blocked(p, "SOURCE_CONFLICT")
        p["claimed_value"] = "11 e 12/02/2027"
        self.blocked(p, "SOURCE_CONFLICT")

    def test_alert_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copy2(ROOT / SOURCE, root / SOURCE)
            shutil.copytree(ROOT / "edital", root / "edital")
            path = root / "edital/fontes_oficiais.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["open_alerts"][0]["status"] = "resolved_without_evidence"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            p = {
                "fact_id": CONFLICT_ID, "claimed_value": "11 e 12/02/2027",
                "citations": [citation(13, "11 e 12/01/2027")],
            }
            self.blocked(p, "BOOTSTRAP_INVALID", root)

    def test_no_external_effect_for_any_positive_case(self):
        for ident, record in FACTS.items():
            with self.subTest(fact_id=ident):
                out = check_critical_claim(claim(ident, record["value"]))
                self.assertEqual(out["decision"], "FACT_MATCHED")
                self.assertFalse(out["publication_authorized"])
                self.assertEqual(out["external_effects"], 0)


if __name__ == "__main__":
    unittest.main()
