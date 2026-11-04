import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from verify_approval_snapshot import audit, SRCPLAN, SRCCHECK, MARKER, digest

class ApprovalSnapshotTests(unittest.TestCase):
    def test_real_artifacts(self):
        self.assertEqual(audit(ROOT)['result'],'PASS')
    def test_source_plan_sha(self):
        self.assertEqual(digest((ROOT/'../proposals/r2/plan.md').read_bytes()),SRCPLAN)
    def test_source_checks_sha(self):
        self.assertEqual(digest((ROOT/'../proposals/r2/checks-preview.md').read_bytes()),SRCCHECK)
    def test_approval_line_not_in_original(self):
        self.assertNotIn(b'**Approved**:',(ROOT/'../proposals/r2/plan.md').read_bytes())
    def test_approval_added_only_as_suffix(self):
        self.assertEqual((ROOT/'plan.md').read_bytes(),(ROOT/'../proposals/r2/plan.md').read_bytes()+MARKER)
    def test_check_body_exact(self):
        sep=b'\n## Checks\n'
        self.assertEqual((ROOT/'checks.md').read_bytes().split(sep,1)[1],(ROOT/'../proposals/r2/checks-preview.md').read_bytes().split(sep,1)[1])
    def test_snapshot_receipt_has_exact_source_commit(self):
        self.assertEqual(json.loads((ROOT/'approval-receipt.json').read_text())['approval']['source_head_commit'],'426286a913ea17adddb2cdb951120b45282ad938')
    def test_no_functional_proof(self):
        r=json.loads((ROOT/'approval-receipt.json').read_text());self.assertEqual(r['derivation']['functional_checks_pass'],0);self.assertEqual(r['derivation']['functional_checks_not_run'],27)
    def test_no_unsafe_gate_promotion(self):
        r=json.loads((ROOT/'approval-receipt.json').read_text());self.assertEqual(r['VERIFY_C'],'NOT_RUN');self.assertEqual(r['VERIFY_O'],'BLOCKED')
    def test_one_byte_mutation_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            # patch read on the plan path for a semantic attack, retaining the exact source snapshot.
            real_read=pathlib.Path.read_bytes
            def malicious_read(path):
                val=real_read(path)
                if pathlib.Path(path)==(ROOT/'plan.md'):
                    return val.replace(b'SHALL',b'MAY',1)
                return val
            with patch.object(pathlib.Path,'read_bytes',malicious_read):
                self.assertIn('PLAN_NORMATIVE_BYTES_CHANGED_OR_APPROVAL_MISSING',audit(ROOT)['errors'])
    def test_missing_approval_marker_fails(self):
        real_read=pathlib.Path.read_bytes
        def patched_read(path):
            val=real_read(path)
            return val[:-len(MARKER)] if pathlib.Path(path)==ROOT/'plan.md' else val
        with patch.object(pathlib.Path,'read_bytes',patched_read):
            self.assertIn('PLAN_NORMATIVE_BYTES_CHANGED_OR_APPROVAL_MISSING',audit(ROOT)['errors'])
    def test_check_mutation_fails(self):
        real_read=pathlib.Path.read_bytes
        def patched_read(path):
            val=real_read(path)
            if pathlib.Path(path)==ROOT/'checks.md':return val.replace(b'DENY:',b'ALLOW:',1)
            return val
        with patch.object(pathlib.Path,'read_bytes',patched_read):
            self.assertIn('CHECKS_NORMATIVE_CONTENT_CHANGED',audit(ROOT)['errors'])
    def test_false_functional_claim_rejected(self):
        real_read=pathlib.Path.read_text
        def patched_read(path,*args,**kwargs):
            val=real_read(path,*args,**kwargs)
            if pathlib.Path(path)==ROOT/'approval-receipt.json':
                r=json.loads(val);r['derivation']['functional_checks_pass']=27;return json.dumps(r)
            return val
        with patch.object(pathlib.Path,'read_text',patched_read):
            self.assertIn('FALSE_FUNCTIONAL_PROOF_CLAIM',audit(ROOT)['errors'])

if __name__=='__main__':unittest.main()
