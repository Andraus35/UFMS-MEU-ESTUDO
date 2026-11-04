#!/usr/bin/env python3
"""STATIC compatibility check for Spec Lean. NOT an official TLC validator.

Inputs are copies of frozen PR #5 files. Source basis: TLC `lean_config.py`
Git blob b751517ba653478cd69330e590c8f0de7a739c24 and
`validate_checks.py` blob be14d1956cc5afaba6009608c71d7ec1a216c29f.
No external side effects or user data.
"""
from pathlib import Path
import argparse, hashlib, json, re

EXPECTED = {
  "plan.md": "fa37d9c5cc2fb4288c477c4b175c8ec923ebb419be2aa9e785b32471b850c70c",
  "checks.md": "50dff7d0f8ff6f9d6ce7a66ea624cd06d6a6f90bb8055be18dd74461b5481bc0",
}
# Literal rule copied from official `lean_config.py`, used only for a *static
# compatibility probe*. We never claim that we executed the official script.
APPROVED_RE = re.compile(
    r'^\**\s*Approved\s*\**\s*:\s*\**\s*\d{4}-\d{2}-\d{2}\b.*\buser\s*:\s*["“][^"”]*\S[^"”]*["”]',
    re.IGNORECASE)
CHECK_RE = re.compile(r'^\*\*C(\d+)\*\*\s*[-–—:]\s+(.+)$')
PROOF_RE = re.compile(r'^Proof:\s+.+$')


def check(root: Path) -> dict:
    findings=[]
    def add(name, status, detail):
        findings.append({"id":name,"status":status,"detail":detail})
    texts={}
    for name,digest in EXPECTED.items():
        p=root/name
        if not p.exists():
            add('SHA_'+name,'FAIL','arquivo ausente');continue
        content=p.read_bytes(); real=hashlib.sha256(content).hexdigest();texts[name]=content.decode('utf-8')
        add('SHA_'+name,'PASS' if real==digest else 'FAIL',real)
    receipt=root/'approval-receipt.json'
    if receipt.exists():
        try:
            a=json.loads(receipt.read_text(encoding='utf-8'))
            ok=(a.get('approval_text')=='APROVO' and a.get('approved_object',{}).get('sha256')==EXPECTED['plan.md']
                and a.get('new_checks_sha256')==EXPECTED['checks.md']
                and a.get('approved_object',{}).get('head_commit_sha_at_approval')=='aa66ac2945cc35c72bbd06401db977903dcbb3c4')
            add('APPROVAL_RECEIPT','PASS' if ok else 'FAIL','aceite externo vinculado a snapshot e checks, não incorporado no PLAN')
        except (ValueError,UnicodeDecodeError) as e: add('APPROVAL_RECEIPT','FAIL',str(e))
    else: add('APPROVAL_RECEIPT','FAIL','recibo não encontrado')
    plan=texts.get('plan.md','')
    if plan:
        found=any(APPROVED_RE.match(s.strip()) for s in plan.splitlines())
        add('TLC_APPROVED_IN_SIBLING_PLAN','PASS' if found else 'BLOCKED',
            'O validate_checks.py oficial exige uma linha **Approved**: YYYY-MM-DD - user: "..." no plan.md; arquivo separado não atende essa condição')
    checks=texts.get('checks.md','')
    if checks:
        sections={x:bool(re.search(r'^## '+x+r'\s*$',checks,re.M)) for x in ['Checks','Coverage','Swept']}
        add('SECTIONS','PASS' if all(sections.values()) else 'FAIL',sections)
        rows=[];curr=None;proofs={}
        for line in checks.splitlines():
            match=CHECK_RE.match(line.strip())
            if match:
                curr=int(match.group(1));rows.append(curr);proofs[curr]=0
            if curr is not None and PROOF_RE.match(line.strip()):proofs[curr]+=1
        uniq=set(rows)
        complete=len(rows)==27 and uniq==set(range(1,28)) and all(proofs.values())
        add('CHECKS_27_AND_PROOFS','PASS' if complete else 'FAIL',{'total':len(rows),'unique':len(uniq),'with_proof':sum(v>0 for v in proofs.values())})
    # Based on actual PR #5 HEAD tree, independently confirmed by authenticated
    # GitHub: scripts/ from PR #1 is absent on the PR #5 standalone tree.
    # This is *not* inferred from absence in the local three-file extract.
    add('TLC_BUILD_EXECUTE_SINGLE_HEAD','BLOCKED','PR #5 HEAD não possui scripts/ci_gate_contract.py, scripts/write_policy.py e scripts/validate.py; Build refere-se ao PR #1 em outro SHA')
    manifest=root/'composition-manifest.json'
    if manifest.exists():
        m=json.loads(manifest.read_text(encoding='utf-8'))
        outdated=m.get('approval_provenance','').endswith('requires new human approval') or m.get('candidate_plan_sha256')!=EXPECTED['plan.md']
        add('COMPOSITION_MANIFEST_CURRENCY','WARN' if outdated else 'PASS',
            'Manifesto antigo: foi produzido antes de v0.3-r1 e da aprovação; não pode ser recibo da candidata atual' if outdated else 'Atual')
    else: add('COMPOSITION_MANIFEST_CURRENCY','WARN','manifesto não incluído')
    add('TLC_OFFICIAL_EXECUTION','NOT_RUN','npx falhou EAI_AGAIN registry.npmjs.org; script oficial não executado')
    add('INDEPENDENT_GQD','PENDING','auditor independente ainda não examinou HEAD novo')
    add('FUNCTIONAL_PROOFS','NOT_RUN','0/27 provas funcionais da feature')
    return {'schema':'UFMS-TLC-STATIC-PREFLIGHT-1','label':'NOT_OFFICIAL_TLC_VALIDATION',
            'official_sources':{'validate_plan_py':'82f7c754fb9542e659e13a9732cf89d9a25def1f',
                                'validate_checks_py':'be14d1956cc5afaba6009608c71d7ec1a216c29f',
                                'validate_verification_py':'b2035193543df146dc5c714979b27a94972d8da4',
                                'lean_config_py':'b751517ba653478cd69330e590c8f0de7a739c24'},
            'findings':findings}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).parent)
    p.add_argument('--json',type=Path)
    args=p.parse_args();result=check(args.root)
    output=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.json:args.json.write_text(output,encoding='utf-8')
    print(output)
