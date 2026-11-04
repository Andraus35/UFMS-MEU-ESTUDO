import unittest
from pathlib import Path
from local_validate import audit
ROOT=Path(__file__).parent
P=(ROOT/'plan.md').read_text(); C=(ROOT/'checks-preview.md').read_text()
class Preapproval(unittest.TestCase):
    def test_valid_proposal(self):self.assertEqual(audit(P,C),[])
    def test_missing_observable(self):self.assertTrue(audit(P.replace('## Observable','## NotObservable',1),C))
    def test_missing_numeric_status(self):self.assertTrue(audit(P.replace('200 ALLOW`, `422 NEEDS_EVIDENCE`, `202 NEEDS_APPROVAL`, `403 DENY','ALLOW`, `NEEDS_EVIDENCE`, `NEEDS_APPROVAL`, `DENY',1),C))
    def test_nonexistent_landing(self):self.assertTrue(audit(P.replace('AC06, AC11, AC26 — saída','sem prova — saída'),C))
    def test_missing_surface(self):self.assertTrue(audit(P.replace('## Surface','## NotSurface',1),C))
    def test_lost_ears_requirement(self):self.assertTrue(audit(P.replace('WHEN uma sessão inicia THEN o harness SHALL conferir','WHEN uma sessão inicia THEN o harness MAY conferir',1).replace('em qualquer falha SHALL retornar','em qualquer falha MAY retornar',1),C))
    def test_wrong_checks_version(self):self.assertTrue(audit(P,C.replace('revisions/v0.3/plan.md','plan.md',1)))
    def test_premature_approval(self):self.assertTrue(audit(P+'\n**Approved**: fabricated\n',C))
    def test_unrun_unlabeled(self):self.assertTrue(audit(P,C.replace('NOT_RUN','PENDING')))
    def test_missing_status_join(self):self.assertTrue(audit(P,C.replace('Surface aliases','Surface categories')))
if __name__=='__main__':unittest.main()
