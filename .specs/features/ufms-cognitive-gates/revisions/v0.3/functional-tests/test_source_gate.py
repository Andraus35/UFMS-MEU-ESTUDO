"""Functional, offline C2/C3 tests on the actual composed source bytes.

No live tutor, renderer or externally privileged tool is exercised.
"""
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
from source_gate import PINNED_SOURCE_BLOB, SOURCE, resolve_reference


class SourceReferenceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = dict(read_pages((ROOT / SOURCE).read_text(encoding="utf-8")))

    def citation(self, page=2, quote_text="ser considerado apto física e mentalmente"):
        body = self.pages[page]
        start = body.index(quote_text)
        end = start + len(quote_text)
        return {
            "source": SOURCE,
            "source_sha": PINNED_SOURCE_BLOB,
            "page": page,
            "span": {"start": start, "end": end},
            "quote": quote_text,
        }

    def assert_needs_evidence(self, proposal, root=ROOT):
        decision = resolve_reference(proposal, root=root)
        self.assertEqual(decision["decision"], "NEEDS_EVIDENCE", decision)
        self.assertEqual(decision["reason_code"], "SOURCE_NOT_FOUND")
        self.assertEqual(decision["source_refs"], [])
        self.assertFalse(decision["publication_authorized"])
        self.assertEqual(decision["external_effects"], 0)

    def copied_root(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        tmp = Path(holder.name)
        shutil.copy2(ROOT / SOURCE, tmp / SOURCE)
        shutil.copytree(ROOT / "edital", tmp / "edital")
        return tmp

    def test_c2_unknown_source_rejected(self):
        q = self.citation()
        q["source"] = "edital-fabricado.md"
        self.assert_needs_evidence(q)

    def test_c2_missing_source_identity_rejected(self):
        for key in ("source", "source_sha"):
            q = self.citation()
            del q[key]
            with self.subTest(key=key):
                self.assert_needs_evidence(q)

    def test_c3_exact_original_span_resolves_without_publish_grant(self):
        q = self.citation()
        result = resolve_reference(q)
        self.assertEqual(result["decision"], "EVIDENCE_RESOLVED", result)
        self.assertEqual(result["reason_code"], "EXACT_SPAN_MATCH")
        self.assertEqual(result["quote"], q["quote"])
        self.assertEqual(result["source_refs"][0]["page"], q["page"])
        self.assertEqual(result["source_refs"][0]["source_sha"], PINNED_SOURCE_BLOB)
        self.assertEqual(result["semantic_support"], "NOT_CHECKED")
        self.assertFalse(result["publication_authorized"])
        self.assertEqual(result["external_effects"], 0)

    def test_c3_wrong_sha_rejected(self):
        q = self.citation()
        q["source_sha"] = "0" * 40
        self.assert_needs_evidence(q)

    def test_c3_wrong_page_or_quote_rejected(self):
        q = self.citation()
        q["page"] = 3
        self.assert_needs_evidence(q)
        q = self.citation()
        q["quote"] = "As inscrições serão sempre gratuitas"
        self.assert_needs_evidence(q)

    def test_c3_span_bounds_rejected(self):
        for span in (
            {"start": -1, "end": 5},
            {"start": 10, "end": 10},
            {"start": 10, "end": 9},
            {"start": 0, "end": 1001},
            {"start": 9999999, "end": 99999999},
            {"start": True, "end": 10},
            {"start": "0", "end": 10},
        ):
            with self.subTest(span=span):
                q = self.citation()
                q["span"] = span
                self.assert_needs_evidence(q)

    def test_c3_non_integer_page_rejected(self):
        for page in (True, "2", 0, 48, None):
            with self.subTest(page=page):
                q = self.citation()
                q["page"] = page
                self.assert_needs_evidence(q)

    def test_c3_cross_chunk_span_resolves_two_ids(self):
        page = 15
        manifest = json.loads((ROOT / "edital/manifest.json").read_text(encoding="utf-8"))
        cut = next(x["char_end"] for x in manifest["chunks"] if x["id"] == "p15-c01")
        body = self.pages[page]
        start, end = cut - 15, cut + 15
        q = {
            "source": SOURCE,
            "source_sha": PINNED_SOURCE_BLOB,
            "page": page,
            "span": {"start": start, "end": end},
            "quote": body[start:end],
        }
        decision = resolve_reference(q)
        self.assertEqual(decision["decision"], "EVIDENCE_RESOLVED", decision)
        self.assertEqual(decision["source_refs"][0]["chunk_ids"], ["p15-c01", "p15-c02"])

    def test_integrity_source_tamper_denied(self):
        tmp = self.copied_root()
        file = tmp / SOURCE
        file.write_bytes(file.read_bytes() + b"tamper")
        r = resolve_reference(self.citation(), root=tmp)
        self.assertEqual((r["decision"], r["reason_code"]), ("DENY", "BOOTSTRAP_INVALID"))

    def test_integrity_manifest_tamper_denied(self):
        tmp = self.copied_root()
        target = tmp / "edital/manifest.json"
        raw = json.loads(target.read_text(encoding="utf-8"))
        raw["chunks"][1]["page"] = 99
        target.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        r = resolve_reference(self.citation(), root=tmp)
        self.assertEqual((r["decision"], r["reason_code"]), ("DENY", "BOOTSTRAP_INVALID"))

    def test_integrity_chunk_tamper_denied(self):
        tmp = self.copied_root()
        chunk = tmp / "edital/chunks/p02-c01.md"
        chunk.write_text(chunk.read_text(encoding="utf-8") + "TAMPER", encoding="utf-8")
        r = resolve_reference(self.citation(), root=tmp)
        self.assertEqual((r["decision"], r["reason_code"]), ("DENY", "BOOTSTRAP_INVALID"))

    def test_c2_c3_do_not_claim_semantic_truth(self):
        q = self.citation()
        q["claim"] = "Este trecho prova que a prova foi cancelada"
        result = resolve_reference(q)
        self.assertEqual(result["decision"], "EVIDENCE_RESOLVED")
        self.assertEqual(result["semantic_support"], "NOT_CHECKED")
        self.assertFalse(result["publication_authorized"])


if __name__ == "__main__":
    unittest.main()
