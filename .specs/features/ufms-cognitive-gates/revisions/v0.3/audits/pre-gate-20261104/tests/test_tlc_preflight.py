import unittest, sys, tempfile, shutil, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tlc_preflight_snapshot import check
BASE=Path(__file__).resolve().parents[1]

def finding(report, key):
    return next(x for x in report['findings'] if x['id']==key)['status']

class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory()
        self.root=Path(self.dir.name)
        for f in ['plan.md','checks.md','approval-receipt.json','composition-manifest.json']:
            shutil.copy2(BASE/f,self.root/f)
    def tearDown(self): self.dir.cleanup()
    def test_frozen_hashes(self):
        out=check(self.root)
        self.assertEqual(finding(out,'SHA_plan.md'),'PASS')
        self.assertEqual(finding(out,'SHA_checks.md'),'PASS')
    def test_human_acceptance_receipt_binding(self):
        self.assertEqual(finding(check(self.root),'APPROVAL_RECEIPT'),'PASS')
    def test_official_inline_approval_blocked(self):
        self.assertEqual(finding(check(self.root),'TLC_APPROVED_IN_SIBLING_PLAN'),'BLOCKED')
    def test_gates_not_falsely_approved(self):
        out=check(self.root)
        self.assertEqual(finding(out,'TLC_OFFICIAL_EXECUTION'),'NOT_RUN')
        self.assertEqual(finding(out,'FUNCTIONAL_PROOFS'),'NOT_RUN')
    def test_frozen_plan_change_detected_even_with_inline_marker(self):
        with (self.root/'plan.md').open('a',encoding='utf-8') as f:
            f.write('\n**Approved**: 2026-11-04 - user: "APROVO"\n')
        out=check(self.root)
        self.assertEqual(finding(out,'SHA_plan.md'),'FAIL')
        self.assertEqual(finding(out,'TLC_APPROVED_IN_SIBLING_PLAN'),'PASS')
    def test_check_change_detected(self):
        p=self.root/'checks.md'
        p.write_text(p.read_text(encoding='utf-8').replace('**C27**','**C28**'),encoding='utf-8')
        out=check(self.root)
        self.assertEqual(finding(out,'SHA_checks.md'),'FAIL')
        self.assertEqual(finding(out,'CHECKS_27_AND_PROOFS'),'FAIL')
    def test_noop_proof_absence_detected(self):
        p=self.root/'checks.md';t=p.read_text(encoding='utf-8');p.write_text(t.replace('Proof:', 'NoProof:'),encoding='utf-8')
        out=check(self.root)
        self.assertEqual(finding(out,'CHECKS_27_AND_PROOFS'),'FAIL')
    def test_fake_approval_receipt_rejected(self):
        p=self.root/'approval-receipt.json';x=json.loads(p.read_text(encoding='utf-8'))
        x['approved_object']['sha256']='0'*64;p.write_text(json.dumps(x),encoding='utf-8')
        self.assertEqual(finding(check(self.root),'APPROVAL_RECEIPT'),'FAIL')
    def test_composition_manifest_outdated(self):
        self.assertEqual(finding(check(self.root),'COMPOSITION_MANIFEST_CURRENCY'),'WARN')
    def test_no_false_runtime_success(self):
        o=check(self.root)
        self.assertEqual(finding(o,'TLC_BUILD_EXECUTE_SINGLE_HEAD'),'BLOCKED')
        self.assertEqual(finding(o,'INDEPENDENT_GQD'),'PENDING')

if __name__=='__main__': unittest.main()
