#!/usr/bin/env python3
"""Fail-closed documentary provenance for Spec Lean approved R2 (NOT a functional harness verifier)."""
import argparse
import hashlib
import json
import re
from pathlib import Path

SRCPLAN='e528bd36ff4e106622e04b009a8cce381ea5fa079558cc14adc3f5227f90362c'
SRCCHECK='e7ea97d5ee8069961721fa62013b2d101feb77c55203054958d70a6f6edf5295'
MARKER=b'\n**Approved**: 2026-11-04 - user: "APROVO"\n'
SOURCE_COMMIT='426286a913ea17adddb2cdb951120b45282ad938'

def digest(buf):return hashlib.sha256(buf).hexdigest()

def audit(root):
    root=Path(root)
    srcplan=(root/'../proposals/r2/plan.md').resolve().read_bytes()
    srccheck=(root/'../proposals/r2/checks-preview.md').resolve().read_bytes()
    plan=(root/'plan.md').read_bytes()
    checks=(root/'checks.md').read_bytes()
    rec=json.loads((root/'approval-receipt.json').read_text())
    errs=[]
    require=lambda condition,reason: errs.append(reason) if not condition else None
    require(digest(srcplan)==SRCPLAN,'SOURCE_PLAN_HASH_MISMATCH')
    require(digest(srccheck)==SRCCHECK,'SOURCE_CHECKS_HASH_MISMATCH')
    require(plan==srcplan+MARKER,'PLAN_NORMATIVE_BYTES_CHANGED_OR_APPROVAL_MISSING')
    require(digest(plan)==rec['derivation']['canonical_plan_sha256'],'CANONICAL_PLAN_RECEIPT_MISMATCH')
    require(digest(checks)==rec['derivation']['canonical_checks_sha256'],'CANONICAL_CHECKS_RECEIPT_MISMATCH')
    # Only the introductory administrative metadata may differ.
    separator=b'\n## Checks\n'
    require(separator in srccheck and separator in checks,'CHECKS_SECTION_MISSING')
    if separator in srccheck and separator in checks:
        require(checks.split(separator,1)[1]==srccheck.split(separator,1)[1],'CHECKS_NORMATIVE_CONTENT_CHANGED')
    srcplan_text=srcplan.decode('utf-8')
    checks_text=checks.decode('utf-8')
    ac=re.findall(r'(?m)^(\d+)\. (?:WHEN|IF|WHILE)',srcplan_text)
    cn=re.findall(r'(?m)^\*\*C(\d+)\*\*\s*-',checks_text)
    require(ac==[str(i) for i in range(1,28)],'EARS_27_SEQUENTIAL_FAILED')
    require(cn==[str(i) for i in range(1,28)],'CHECKS_27_SEQUENTIAL_FAILED')
    require(rec['approval']['literal_user_message']=='APROVO','HUMAN_APPROVAL_MISMATCH')
    require(rec['approval']['source_head_commit']==SOURCE_COMMIT,'APPROVED_SOURCE_COMMIT_MISMATCH')
    require(rec['approval']['source_sha256']==SRCPLAN,'APPROVED_SOURCE_HASH_MISMATCH')
    require(rec['derivation']['checks_preview_sha256']==SRCCHECK,'CHECKS_PREVIEW_RECEIPT_MISMATCH')
    require(rec['derivation']['functional_checks_pass']==0 and rec['derivation']['functional_checks_not_run']==27,'FALSE_FUNCTIONAL_PROOF_CLAIM')
    require(rec['independent_GQD'].startswith('REPROVADA') and rec['VERIFY_C']=='NOT_RUN' and rec['VERIFY_O']=='BLOCKED','FALSE_GATES_APPROVAL')
    require(rec['no_merge'] and rec['no_deploy'] and rec['no_personal_results_writes'],'UNSAFE_PERMISSION_CLAIM')
    # Previously approved version is immutable and remains available at old canonical path.
    prior_plan=(root/'../plan.md').resolve().read_bytes()
    prior_checks=(root/'../checks.md').resolve().read_bytes()
    require(digest(prior_plan)=='fa37d9c5cc2fb4288c477c4b175c8ec923ebb419be2aa9e785b32471b850c70c','R1_PLAN_CHANGED')
    require(digest(prior_checks)=='50dff7d0f8ff6f9d6ce7a66ea624cd06d6a6f90bb8055be18dd74461b5481bc0','R1_CHECKS_CHANGED')
    return {'result':'PASS' if not errs else 'FAIL','errors':errs,'source_plan_sha256':digest(srcplan),'source_checks_preview_sha256':digest(srccheck),'approved_plan_sha256':digest(plan),'derived_checks_sha256':digest(checks),'ears_count':len(ac),'checks_count':len(cn),'functional_checks_pass':0,'functional_checks_not_run':27,'GQD':'REPROVADA_PENDING_REAUDIT'}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',required=True)
    args=a.parse_args();result=audit(args.root)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['result']=='PASS' else 1)
