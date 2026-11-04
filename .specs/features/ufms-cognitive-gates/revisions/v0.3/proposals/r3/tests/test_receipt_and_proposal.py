import copy,hashlib,importlib.util,json,re,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
SRC=HERE.parents[1]/'approved-r2'
spec=importlib.util.spec_from_file_location('receipt_checker',HERE/'tools/verify_receipt_and_composition.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class ReceiptAndProposal(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.base=Path(self.tmp.name)
  self.r2=self.base/'approved-r2'; self.r2.mkdir(parents=True)
  self.proposal=self.base/'proposals/r2';self.proposal.mkdir(parents=True)
  for name in ['plan.md','checks.md','approval-receipt.json']:(self.r2/name).write_bytes((SRC/name).read_bytes())
  for name in ['plan.md','checks-preview.md']:(self.proposal/name).write_bytes((SRC.parent/'proposals/r2'/('plan.md' if name=='plan.md' else 'checks-preview.md')).read_bytes())
  self.lock=self.base/'lock.json';self.lock.write_bytes((HERE/'composition-lock.json').read_bytes())
 def verdict(self):return mod.audit(self.r2,self.lock)
 def edit_receipt(self,fn):
  p=self.r2/'approval-receipt.json';o=json.loads(p.read_text());fn(o);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
 def edit_lock(self,fn):
  o=json.loads(self.lock.read_text());fn(o);self.lock.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
 def test_00_baseline_receipt_passes_documentary_only(self):
  r=self.verdict();self.assertEqual(r['result'],'PASS_DOCUMENTARY_ONLY',r)
  self.assertFalse(r['composition_executed']);self.assertEqual(r['functional_27'],'NOT_RUN')
 def test_01_mutant_new_01_git_blob_zero_rejected(self):
  self.edit_receipt(lambda o:o['approval'].__setitem__('source_git_blob_sha1','0'*40));self.assertIn('RECEIPT_GIT_BLOB_INVALID',self.verdict()['errors'])
 def test_02_mutant_new_02_pr1_sha_zero_rejected(self):
  self.edit_receipt(lambda o:o['dependencies'].__setitem__('PR1','0'*40));self.assertIn('RECEIPT_DEPENDENCIES_DRIFT',self.verdict()['errors'])
 def test_03_mutant_new_03_scope_escalation_rejected(self):
  self.edit_receipt(lambda o:o['approval'].__setitem__('scope','PLAN + DEPLOY + PERSONAL WRITE'));self.assertIn('RECEIPT_SCOPE_ESCALATION',self.verdict()['errors'])
 def test_04_noncanonical_receipt_extra_key_rejected(self):
  self.edit_receipt(lambda o:o.__setitem__('allow_telegram_write',True));self.assertIn('RECEIPT_OUTSIDE_PINNED_HASH',self.verdict()['errors'])
 def test_05_deploy_flag_rejected(self):
  self.edit_receipt(lambda o:o.__setitem__('no_deploy',False));self.assertIn('RECEIPT_SCOPE_PERMISSIONS_ESCALATION',self.verdict()['errors'])
 def test_06_gate_pass_fabrication_rejected(self):
  self.edit_receipt(lambda o:o.__setitem__('independent_GQD','APROVADA'));self.assertIn('FALSE_GATES_CLEARED',self.verdict()['errors'])
 def test_07_main_integrated_sha_tampered_rejected(self):
  self.edit_lock(lambda o:o['components'][0].__setitem__('commit_sha','f'*40));self.assertIn('COMPOSITION_IDENTITY_DRIFT_main_integrated',self.verdict()['errors'])
 def test_08_composition_digest_forgery_rejected(self):
  self.edit_lock(lambda o:o.__setitem__('composition_digest','sha256:'+'0'*64));self.assertIn('COMPOSITION_DIGEST_MISMATCH',self.verdict()['errors'])
 def test_09_false_claim_execution_rejected(self):
  self.edit_lock(lambda o:o['assembly'].__setitem__('proof_replay_status','PASS'));self.assertIn('COMPOSITION_EXECUTION_FALSE_CLAIM',self.verdict()['errors'])
 def test_10_original_source_bitflip_rejected(self):
  p=self.proposal/'plan.md';p.write_bytes(p.read_bytes().replace(b'NOVA PROPOSTA',b'NOVA PROPOSTB',1));self.assertIn('SOURCE_BYTES_INVALID',self.verdict()['errors'])
 def test_11_r3_plan_not_approved_and_27_ac(self):
  txt=(HERE/'plan.md').read_text();ids=re.findall(r'(?m)^(\d+)\. (?:WHEN|IF|WHILE)',txt)
  self.assertEqual(ids,[str(i) for i in range(1,28)]);self.assertIn('PROPOSTA NÃO APROVADA',txt);self.assertNotIn('**Approved**: 2026',txt)
 def test_12_r3_202_403_authorization_mapping(self):
  txt=(HERE/'plan.md').read_text();p202=next(x for x in txt.splitlines() if x.startswith('| `evaluate` | `202'))
  p403=next(x for x in txt.splitlines() if x.startswith('| `evaluate` | `403'))
  self.assertIn('AC13',p202);self.assertNotIn('AC14',p202)
  self.assertIn('AC14',p403);self.assertIn('DENY:AUTH_MISMATCH',txt)
 def test_13_renderer_revocation_and_atomicity_in_plan(self):
  txt=(HERE/'plan.md').read_text();self.assertIn('S-NEW-03',txt);self.assertIn('S-NEW-04',txt)
  self.assertIn('atômica em armazenamento compartilhado',txt);self.assertIn('authorization_epoch',txt);self.assertIn('revogada',txt)
 def test_14_r3_checks_preview_27_and_only_preview(self):
  txt=(HERE/'checks-preview.md').read_text()
  self.assertEqual(re.findall(r'(?m)^\*\*C(\d+)\*\*\s*-',txt),[str(i) for i in range(1,28)])
  self.assertIn('NÃO APROVADOS',txt);self.assertIn('NOT_RUN',txt)
  self.assertIn('test_renderer_concurrent_nonce_exactly_one_publication',txt)
 def test_15_no_approval_elevation_from_r2(self):
  t=(HERE/'APPROVAL_PRECEDENCE.md').read_text();self.assertIn('v0.3-r3',t);self.assertIn('NÃO APROVADO',t);self.assertIn('NOT_VERIFIABLE',t)

if __name__=='__main__':unittest.main(verbosity=2)
