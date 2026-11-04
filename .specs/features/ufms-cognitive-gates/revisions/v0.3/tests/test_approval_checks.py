"""Synthetic/document-only guard for checks derivation; never a gate implementation."""
import unittest,re,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent.parent
CHECKS=(HERE/'checks.md').read_text(encoding='utf8')
PLAN=(HERE/'plan.md').read_bytes()
RECEIPT=json.loads((HERE/'approval-receipt.json').read_text())
DELTA={4:'SOURCE_CONFLICT',11:'trust root',13:'aprovador',14:'approver_id',15:'concorrência',18:'DEPENDENCY_FAILED',20:'composition_digest',22:'isolamento',25:'CITE-IND-01',26:'recipient'}

def valid(s):
    ids=re.findall(r'^\*\*C(\d{1,2})\*\* -',s,re.M)
    if ids!=[str(i) for i in range(1,28)]:return False
    if any(s.count(f'**C{i}** -') != 1 for i in range(1,28)):return False
    if re.search(r'\|[^\n]*\|\s*(?:PENDING|NOT_RUN|BLOCKED|GQ-O BLOCKED)\s*\|',s):return False
    for n,required in DELTA.items():
        part=s.split(f'**C{n}** -',1)[1].split(f'**C{n+1}** -',1)[0]
        if required.lower() not in part.lower():return False
        if n==14 and 'telegram.send' not in part:return False
        for m in ['**Positivo:**','**Negativo:**','**Oráculo de aprovação:**','**Resultado:** `NOT_RUN`']:
            if m not in part:return False
    if 'python -c "print(\'PASS\')"' in s:return False
    return True

class ApprovalChecksTests(unittest.TestCase):
    def test_identity(self):self.assertEqual(hashlib.sha256(PLAN).hexdigest(),RECEIPT['approved_object']['sha256'])
    def test_approval_scope(self):self.assertEqual(RECEIPT['approval_text'],'APROVO');self.assertTrue(RECEIPT['constraints']['no_merge'])
    def test_27_members(self):self.assertTrue(valid(CHECKS))
    def test_27_proofs(self):self.assertGreaterEqual(len(re.findall(r'^Proof: ',CHECKS,re.M)),27)
    def test_no_fake_pass(self):self.assertIn('0 PASS / 27 NOT_RUN',CHECKS)
    def test_mutation_remove_C14(self):self.assertFalse(valid(CHECKS.replace('**C14** -','**C14a** -',1)))
    def test_mutation_drop_nonce_claim(self):self.assertFalse(valid(CHECKS.replace('approver_id', 'approver_REMOVED')))
    def test_mutation_disable_source_conflict(self):self.assertFalse(valid(CHECKS.replace('SOURCE_CONFLICT', 'SOURCE_MISSING')))
    def test_mutation_delete_positive(self):self.assertFalse(valid(CHECKS.replace('**Positivo:**','**Gone:**')))
    def test_mutation_delete_negative(self):self.assertFalse(valid(CHECKS.replace('**Negativo:**','**Gone:**')))
    def test_mutation_remove_oracle(self):self.assertFalse(valid(CHECKS.replace('**Oráculo de aprovação:**','**Absent:**')))
    def test_mutation_replace_proof_noop(self):self.assertFalse(valid(CHECKS.replace('Proof: `python -m unittest', 'Proof: `python -c "print(\'PASS\')"`\nProof: `python -m unittest',1)))
    def test_mutation_hide_CITE(self):self.assertFalse(valid(CHECKS.replace('CITE-IND-01','CITE-REMOVED')))
    def test_mutation_tool_swap(self):self.assertFalse(valid(CHECKS.replace('telegram.send','email.send')))
    def test_mutation_remove_dependency_failure(self):self.assertFalse(valid(CHECKS.replace('DEPENDENCY_FAILED','FAILED_GENERIC')))
    def test_mutation_remove_composition(self):self.assertFalse(valid(CHECKS.replace('composition_digest','COMPOSITIONLESS')))

if __name__=='__main__':unittest.main()