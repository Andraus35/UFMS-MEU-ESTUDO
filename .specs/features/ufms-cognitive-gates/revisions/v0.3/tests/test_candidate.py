import sys,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from check_candidate import run,validate_texts,ac_blocks,parse_checks

PLAN=(ROOT/'plan.md').read_text()
CHECKS=(ROOT/'checks-preview.md').read_text()
MATRIX=(ROOT/'nc-matrix.md').read_text()
MANIFEST=json.loads((ROOT/'composition-manifest.json').read_text())

class CorrectivePlanTests(unittest.TestCase):
    def test_baseline_scoped_documentary_pass(self):
        x=run();self.assertTrue(x['ok'],x['errors']);self.assertEqual(x['ac_count'],27);self.assertEqual(x['target_ac_count'],10)
    def test_m_ind_01_no_personal_write_denial(self):
        p=PLAN.replace('DENY:PERSONAL_WRITE_DISABLED','ALLOW:PERSONAL_WRITE_ENABLED',1)
        self.assertFalse(validate_texts(p,CHECKS,MATRIX,MANIFEST)['ok'])
    def test_m_ind_02_tautological_proof(self):
        check=CHECKS.replace('Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_authorization_bindings_all_fields`',"Proof: `python -c \"print('PASS')\"`",1)
        self.assertFalse(validate_texts(PLAN,check,MATRIX,MANIFEST)['ok'])
    def test_m_ind_03_false_critical_claim_allowed(self):
        p=PLAN.replace('NEEDS_EVIDENCE:CLAIM_UNSUPPORTED','ALLOW:CLAIM_SUPPORTED',1)
        self.assertFalse(validate_texts(p,CHECKS,MATRIX,MANIFEST)['ok'])
    def test_m_ind_04_emitter_unbound(self):
        p=PLAN.replace('issuer_id, approver_id, approval_id, actor','actor',1)
        self.assertFalse(validate_texts(p,CHECKS,MATRIX,MANIFEST)['ok'])
    def test_rate_limit_after_transport_mutant(self):
        p=PLAN.replace('antes do transport externo','depois do transport externo',1)
        self.assertFalse(validate_texts(p,CHECKS,MATRIX,MANIFEST)['ok'])
    def test_renderer_stale_state_mutant(self):
        p=PLAN.replace('state_revision + source_set_sha + actor_role','actor_role',1)
        self.assertFalse(validate_texts(p,CHECKS,MATRIX,MANIFEST)['ok'])
    def test_source_conflict_absent(self):
        p=PLAN.replace('NEEDS_EVIDENCE:SOURCE_CONFLICT','ALLOW:SOURCE_CONFLICT',1)
        self.assertFalse(validate_texts(p,CHECKS,MATRIX,MANIFEST)['ok'])
    def test_false_pass_claim_in_preview(self):
        c=CHECKS.replace('**Resultado:** `NOT_RUN`','**Resultado:** `PASS`',1)
        self.assertFalse(validate_texts(PLAN,c,MATRIX,MANIFEST)['ok'])
    def test_missing_manifest_dependency(self):
        m=json.loads(json.dumps(MANIFEST));m['components'].pop()
        self.assertFalse(validate_texts(PLAN,CHECKS,MATRIX,m)['ok'])
    def test_wrong_composition_digest(self):
        m=json.loads(json.dumps(MANIFEST));m['composition_digest']='sha256:'+'0'*64
        self.assertFalse(validate_texts(PLAN,CHECKS,MATRIX,m)['ok'])
    def test_no_new_approval(self):
        self.assertIn('v0.3 NÃO APROVADO',PLAN)
        self.assertIn('NÃO ENCERRADA',MATRIX)
    def test_revision_suffix_without_approval_is_allowed(self):
        result=validate_texts(PLAN,CHECKS,MATRIX,MANIFEST)
        self.assertTrue(result["ok"],result["errors"])
        self.assertIn("v0.3-r1", PLAN.splitlines()[2])
    def test_forged_v03_approval_is_denied(self):
        forged=PLAN.replace("v0.3 NÃO APROVADO", "v0.3 APROVADO", 1)
        result=validate_texts(forged,CHECKS,MATRIX,MANIFEST)
        self.assertIn("APPROVAL_MISREPRESENTED", result["errors"])
    def test_missing_approval_pending_is_denied(self):
        forged=PLAN.replace("AGUARDA APROVAÇÃO HUMANA", "APROVADO", 1)
        result=validate_texts(forged,CHECKS,MATRIX,MANIFEST)
        self.assertIn("APPROVAL_MISREPRESENTED", result["errors"])
    def test_exact_27_distinct_criteria(self):
        self.assertEqual(list(ac_blocks(PLAN)),list(range(1,28)))
    def test_10_target_deltas(self):
        self.assertEqual(parse_checks(CHECKS)['delta_count'],10)

if __name__=='__main__':unittest.main()
