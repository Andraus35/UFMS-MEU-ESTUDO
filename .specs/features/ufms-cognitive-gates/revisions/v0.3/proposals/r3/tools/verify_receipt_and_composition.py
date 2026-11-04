#!/usr/bin/env python3
"""Independent *documentary* receipt/lock audit. No external effects, no proof of LLM safety.

Expected identities are pinned from authenticated GitHub readback at source commit,
not trusted from receipt fields. A colluding attacker who can alter both code and
commit requires external auditor SHA readback; this is not a signature/trust service.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

APPROVED_SOURCE_SHA256='e528bd36ff4e106622e04b009a8cce381ea5fa079558cc14adc3f5227f90362c'
APPROVED_SOURCE_BLOB='a1482c25e064a1ccc06c4a649a704fbd5bf97cf5'
APPROVED_SOURCE_COMMIT='426286a913ea17adddb2cdb951120b45282ad938'
APPROVED_SCOPE='PLAN v0.3-r2 only; produce checks without changing normative AC'
PR1='1079d7aa2cadb97d099d1e478f9e83b36180a624'
PR2='6e1fa661a33565d580f99962c3510d5361decbe6'
MAIN='2b09c08036035bfff334e84ee0b976efaed577a8'
MAIN_TREE='9cf12e9550ae2e04840823e8b080be3f91e6fc2b'
PR5='652634b70a411ed4641cb7a202b0ae2f9a19ed1b'
PR5_TREE='724b77597fc8e53c190caa244a99fe8f40a5a69c'
R2_PLAN_HASH='b1dbe81a4723163bb209af39d3ae4a9637e22a9075de2ebce6d1197275a2ad55'
R2_CHECKS_HASH='57f1b2c49226a1ed9a0f836c99084f42e4b655fcd2300251feb169791e6f5568'
SOURCE_PREVIEW_HASH='e7ea97d5ee8069961721fa62013b2d101feb77c55203054958d70a6f6edf5295'
MARKER=b'\n**Approved**: 2026-11-04 - user: "APROVO"\n'
EXPECTED_RECEIPT_SHA256='dd60d0060d850b334d310662a5017109310ef309b2fcfd6d9019bcd57fee23b9'


def sha(b):return hashlib.sha256(b).hexdigest()
def git_blob(b):return hashlib.sha1((b'blob '+str(len(b)).encode()+b'\0')+b).hexdigest()
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')
def audit(r2_root, lock_path):
    root=Path(r2_root)
    errors=[]
    def require(cond,code):
        if not cond: errors.append(code)
    receipt_path=root/'approval-receipt.json'
    receipt_bytes=receipt_path.read_bytes()
    receipt=json.loads(receipt_bytes)
    source=(root/'../proposals/r2/plan.md').resolve().read_bytes()
    preview=(root/'../proposals/r2/checks-preview.md').resolve().read_bytes()
    approved=(root/'plan.md').read_bytes()
    derived=(root/'checks.md').read_bytes()
    a=receipt.get('approval') or {}
    d=receipt.get('derivation') or {}
    dependencies=receipt.get('dependencies') or {}
    require(sha(receipt_bytes)==EXPECTED_RECEIPT_SHA256,'RECEIPT_OUTSIDE_PINNED_HASH')
    require(sha(source)==APPROVED_SOURCE_SHA256,'SOURCE_BYTES_INVALID')
    require(git_blob(source)==APPROVED_SOURCE_BLOB,'SOURCE_GIT_BLOB_INVALID')
    require(sha(approved)==R2_PLAN_HASH and approved==source+MARKER,'PLAN_APPROVAL_DERIVATION_INVALID')
    require(sha(preview)==SOURCE_PREVIEW_HASH,'CHECKS_PREVIEW_CHANGED')
    require(sha(derived)==R2_CHECKS_HASH,'CHECKS_APPROVED_CHANGED')
    require(a.get('source_git_blob_sha1')==git_blob(source)==APPROVED_SOURCE_BLOB,'RECEIPT_GIT_BLOB_INVALID')
    require(a.get('source_head_commit')==APPROVED_SOURCE_COMMIT,'RECEIPT_COMMIT_DRIFT')
    require(a.get('source_sha256')==APPROVED_SOURCE_SHA256,'RECEIPT_SOURCE_HASH_DRIFT')
    require(a.get('scope')==APPROVED_SCOPE,'RECEIPT_SCOPE_ESCALATION')
    require(a.get('source_repository')=='Andraus35/UFMS-MEU-ESTUDO' and a.get('source_pr')==5,'RECEIPT_IDENTITY_DRIFT')
    require(a.get('literal_user_message')=='APROVO' and a.get('date')=='2026-11-04','RECEIPT_APPROVAL_DRIFT')
    require(dependencies=={'PR1':PR1,'PR2':PR2},'RECEIPT_DEPENDENCIES_DRIFT')
    require(d.get('canonical_plan_sha256')==R2_PLAN_HASH and d.get('canonical_checks_sha256')==R2_CHECKS_HASH,'RECEIPT_DERIVATION_DRIFT')
    require(d.get('checks_preview_sha256')==SOURCE_PREVIEW_HASH,'RECEIPT_PREVIEW_DRIFT')
    require(d.get('functional_checks_pass')==0 and d.get('functional_checks_not_run')==27,'FALSE_FUNCTIONAL_APPROVAL')
    require(receipt.get('no_merge') is True and receipt.get('no_deploy') is True and receipt.get('no_personal_results_writes') is True,'RECEIPT_SCOPE_PERMISSIONS_ESCALATION')
    require(str(receipt.get('independent_GQD','')).startswith('REPROVADA') and receipt.get('VERIFY_C')=='NOT_RUN' and receipt.get('VERIFY_O')=='BLOCKED','FALSE_GATES_CLEARED')
    lock=json.loads(Path(lock_path).read_text())
    comp=lock.get('components') or []
    observed={x.get('role'):x for x in comp}
    for role,commit,tree in [('main_integrated',MAIN,MAIN_TREE),('pr5_audited_approved_r2',PR5,PR5_TREE),('pr1_historical_source',PR1,'77d8bcea815899cf5ddef478f7cf4afdedc9f3cf'),('pr2_historical_source',PR2,'f03880d22ab8df2d1c2ac2c5f811445961301974')]:
        item=observed.get(role) or {}
        require(item.get('commit_sha')==commit and item.get('tree_sha')==tree,'COMPOSITION_IDENTITY_DRIFT_'+role)
    assembled=lock.get('assembly') or {}
    require(assembled.get('no_merge') is True and assembled.get('no_push') is True and assembled.get('proof_replay_status')=='NOT_RUN' and assembled.get('do_not_use_head_fallback') is True,'COMPOSITION_EXECUTION_FALSE_CLAIM')
    digest='sha256:'+sha(canonical({'components':comp,'attribution':lock.get('attribution'),'assembly':assembled}))
    require(lock.get('composition_digest')==digest,'COMPOSITION_DIGEST_MISMATCH')
    return {'result':'PASS_DOCUMENTARY_ONLY' if not errors else 'FAIL','errors':errors,'approved_version':'v0.3-r2','new_proposal':'v0.3-r3_NOT_APPROVED','functional_27':'NOT_RUN','composition_executed':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--r2-root',required=True)
    parser.add_argument('--lock',required=True)
    args=parser.parse_args()
    result=audit(args.r2_root,args.lock)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if not result['errors'] else 1)
