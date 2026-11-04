import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from verify_spec import audit_text
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/".specs/features/ufms-cognitive-gates"
PLAN=(BASE/"plan.md").read_text(encoding="utf-8")
CHECKS=(BASE/"checks.md").read_text(encoding="utf-8")

class VerificationMutants(unittest.TestCase):
    def test_unmodified_structure_passes(self):
        self.assertTrue(audit_text(PLAN,CHECKS)["structural_pass"])
    def reject(self,plan=PLAN,checks=CHECKS,code=None):
        x=audit_text(plan,checks)
        self.assertFalse(x["structural_pass"],x)
        if code:self.assertIn(code,[f["code"] for f in x["issues"]])
    def test_mutant_missing_approval(self):
        self.reject(plan=PLAN.replace('**Approved**: 2026-11-04 - user: "APROVO"','**Approved**: TODO',1),code="APPROVAL_MISSING")
    def test_mutant_missing_AC_27(self):
        s=PLAN.splitlines(keepends=True)
        s=[line for line in s if not line.lstrip().startswith('27. IF ')]
        self.reject(plan=''.join(s),code="AC_SET_INCOMPLETE")
    def test_mutant_wrong_SHALL(self):
        self.reject(plan=PLAN.replace('27. IF uma avaliação', '27. IF uma avaliação',1).replace('o gate de release SHALL retornar', 'o gate de release MAY retornar',1),code="AC_SHALL_MISSING")
    def test_mutant_missing_C_22(self):
        s=CHECKS.splitlines(keepends=True)
        s=[line for line in s if not line.startswith('**C22**')]
        self.reject(checks=''.join(s),code="CHECK_SET_INCOMPLETE")
    def test_mutant_mapped_wrong_AC(self):
        self.reject(checks=CHECKS.replace('**C27** -', '**C27** -',1).replace('(AC 27)','(AC 26)',1),code="AC_CHECK_MISMATCH")
    def test_mutant_missing_proof(self):
        import re
        s=re.sub(r'(?ms)(\*\*C26\*\*.*?)(?=\*\*C27\*\*)', lambda m: re.sub(r'(?m)^Proof:.*$', 'Proof: ', m.group(1)), CHECKS)
        self.reject(checks=s,code="CHECK_PROOF_MISSING")
    def test_mutant_missing_coverage_member(self):
        self.reject(checks=CHECKS.replace('AC 27 C27','AC 27 NO_PROOF',1),code="COVERAGE_INCOMPLETE")
    def test_mutant_missing_sweep(self):
        s=CHECKS.replace('- authorization:', '- NOT_AUTHORIZATION:',1)
        self.reject(checks=s,code="SWEEP_MISSING")
    def test_mutant_gateway_door_missing(self):
        s=PLAN.replace('D2 — autorização de efeito','D? — autorização de efeito',1)
        self.reject(plan=s,code="DOOR_MISSING")
    def test_mutant_privacy_flag(self):
        self.reject(plan=PLAN.replace('personal_results_writes_enabled=false','personal_results_writes_enabled=true'),code="PRIVACY_INVARIANT_MISSING")

if __name__=='__main__':unittest.main()
