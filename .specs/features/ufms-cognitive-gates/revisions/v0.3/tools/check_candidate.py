#!/usr/bin/env python3
"""Verificador documental de escopo limitado para a candidata PLAN v0.3.

Atenção: é um scanner de obrigações fixadas + mutações conhecidas, NÃO um
avaliador geral de equivalência semântica e NÃO o validador oficial Spec Lean.
"""
import re
import json
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGETS={4,11,13,14,15,18,20,22,25,26}
CONTRACTS={"TC-01","TC-02","TC-03","TC-04","TC-05","TC-06"}


def ac_blocks(plan):
    if "## Criteria" not in plan or "## Flow" not in plan:
        raise ValueError("MISSING_CRITERIA_BOUNDARY")
    section=plan.split("## Criteria",1)[1].split("## Flow",1)[0]
    marks=list(re.finditer(r"(?m)^(\d+)\. (?:IF|WHEN|WHILE)\b",section))
    if len(marks)!=27 or [int(m.group(1)) for m in marks]!=list(range(1,28)):
        raise ValueError("AC_1_TO_27_INVALID")
    return {int(m.group(1)):section[m.start():marks[i+1].start() if i+1<len(marks) else len(section)] for i,m in enumerate(marks)}


def parse_checks(preview):
    a=set(map(int,re.findall(r"(?m)^\*\*C(\d+)\*\*",preview)))
    if a!=set(range(1,28)):
        raise ValueError("CHECKS_INCOMPLETE")
    b=set(map(int,re.findall(r"(?m)^### C(\d+) / AC\d+",preview)))
    if b!=TARGETS:
        raise ValueError("DELTA_CHECKS_INCOMPLETE")
    if re.search(r"Proof:\s*(?:`)?python\s+-c\s+[^\n]*print\s*\(",preview,re.I):
        raise ValueError("TAUTOLOGICAL_PROOF")
    if re.search(r"\*\*Resultado:\*\*\s*`?PASS",preview):
        raise ValueError("FALSE_EVIDENCE_PASS")
    if "PREVIEW NÃO APROVADO" not in preview or "NOT_RUN" not in preview:
        raise ValueError("PREVIEW_MUST_NOT_ASSERT_PASS")
    return {"old_check_count":len(a),"delta_count":len(b)}


def validate_texts(plan,preview,matrix,manifest):
    errors=[]
    try:
        blocks=ac_blocks(plan)
    except ValueError as exc:
        return {"ok":False,"errors":[str(exc)]}
    try:
        checks=parse_checks(preview)
    except ValueError as exc:
        errors.append(str(exc));checks={}
    must={
        4:["UNVERIFIED_AMENDMENT","SOURCE_CONFLICT","SHA-256"],
        11:["trust root","policy_sha","zero"],
        12:["DENY:PERSONAL_WRITE_DISABLED","sem chamada"],
        13:["emissor/aprovador","destinatário","parâmetros","source_set_sha","NEEDS_APPROVAL"],
        14:["issuer_id","approver_id","actor","tool","operation","destination","recipient","canonical action_hash","assinatura/MAC","DENY:AUTH_MISMATCH","zero invocações"],
        15:["allowlist","RATE_LIMITED","antes do transport externo","limiar","janela"],
        18:["DEPENDENCY_FAILED","UNCONFIRMED","readback","0, 1, 2 e 3"],
        20:["candidate_commit_sha","composition_digest","BLOCKED:NO_PROOF","SHAs exatos"],
        22:["CALLER_NOT_AUTHORIZED","zero chamadas","segredos"],
        25:["CLAIM_UNSUPPORTED","NEEDS_EVIDENCE:SOURCE_CONFLICT","independentemente verificado","citação real isolada"],
        26:["safe_renderer","state_revision","source_set_sha","channel","recipient","OUTPUT_NOT_APPROVED","zero publicações"],
    }
    for ac, tokens in must.items():
        for token in tokens:
            if token not in blocks[ac]:errors.append(f"AC{ac}_MISSING_{token}")
    for contract in CONTRACTS:
        if contract not in plan:errors.append("CONTRACT_MISSING_"+contract)
    tc2=plan.split("**TC-02",1)[1].split("**TC-03",1)[0] if "**TC-02" in plan else ""
    for token in ["issuer_id","approver_id","signature_or_mac","JCS(","atômic","nonce"]:
        if token not in tc2:errors.append("TRUSTED_TOKEN_MISSING_"+token)
    tc5=plan.split("**TC-05",1)[1].split("**TC-06",1)[0] if "**TC-05" in plan else ""
    for token in ["state_revision","source_set_sha","recipient","channel","uso único"]:
        if token not in tc5:errors.append("RENDER_BINDING_MISSING_"+token)
    if "PLAN v0.3 **PROPOSTA CORRETIVA" not in plan or "v0.3 NÃO APROVADO" not in plan:
        errors.append("APPROVAL_MISREPRESENTED")
    for heading in ["## Flow","## Impact","## Relations"]:
        if heading not in plan:errors.append("SECTION_MISSING_"+heading)
    ids=set(re.findall(r"NC-UFMS-GQD-(\d\d)",matrix))
    if ids!=set(f"{x:02d}" for x in range(1,10)):
        errors.append("NC_01_TO_09_INCOMPLETE")
    if "NÃO ENCERRADA" not in matrix:
        errors.append("FALSE_REMEDIATION_APPROVAL")
    sha_list=[v.get("commit_sha","") for v in manifest.get("components",[])]
    if len(sha_list)!=3 or not all(re.fullmatch("[0-9a-f]{40}",sha) for sha in sha_list):
        errors.append("COMPOSITION_SHAS_INVALID")
    if manifest.get("status")!="DOCUMENTARY_COMPOSITION_ONLY_NOT_EXECUTED":
        errors.append("COMPOSITION_STATUS_FALSE")
    if manifest.get("collision_policy")!="FAIL_CLOSED" or "NO_GIT_MERGE" not in manifest.get("assembly",""):
        errors.append("COMPOSITION_NOT_READONLY")
    expected_digest='sha256:'+hashlib.sha256(json.dumps({'components':manifest.get('components',[]),'order':manifest.get('order',[]),'assembly':manifest.get('assembly','')},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    if manifest.get('composition_digest')!=expected_digest:
        errors.append('COMPOSITION_DIGEST_MISMATCH')
    return {"ok":not errors,"errors":errors,"ac_count":len(blocks),"target_ac_count":len(TARGETS),"checks":checks,"note":"Scoped lexical tripwire, NOT semantic proof"}


def run(root=ROOT):
    d=Path(root)
    return validate_texts(
        (d/'plan.md').read_text(),
        (d/'checks-preview.md').read_text(),
        (d/'nc-matrix.md').read_text(),
        json.loads((d/'composition-manifest.json').read_text()))

if __name__=='__main__':
    result=run()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['ok'] else 1)
