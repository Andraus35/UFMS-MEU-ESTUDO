#!/usr/bin/env python3
"""Auditoria estrutural independente de estado operacional de uma spec.
Este auditor é auxiliar, NÃO substitui os validadores oficiais TLC nem um agente Verifier independente.
Não executa modelo, ferramentas ou ações externas.
"""
import re
import json
import hashlib
import argparse
from pathlib import Path

FEATURE="ufms-cognitive-gates"
REQUIRED_SWEEPS=["validation","failure modes","idempotency","authorization","concurrency","data lifecycle","dependency failure","state transitions","observability"]
PLAN_SECTIONS=["Problem","Shape","Surface","Landing","Criteria","Out of scope","Assumptions","Differences from the source","Sources"]
CHECK_SECTIONS=["Checks","Coverage","Test policy","Swept","Handoff"]
EXPECTED=set(range(1,28))

def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def audit_text(plan, checks):
    issues=[]; metrics={}
    def need(ok, code, msg):
        if not ok: issues.append({"code":code,"message":msg})
    need(bool(re.search(r'^\*\*Approved\*\*:\s*2026-11-04\s*-\s*user:\s*"APROVO"',plan,re.M)),"APPROVAL_MISSING","Aprovação literal ausente ou não conferível")
    plan_sections=re.findall(r'^## (.+?)\s*$',plan,re.M)
    checks_sections=re.findall(r'^## (.+?)\s*$',checks,re.M)
    for sec in PLAN_SECTIONS:need(sec in plan_sections,"PLAN_SECTION_MISSING",sec)
    for sec in CHECK_SECTIONS:need(sec in checks_sections,"CHECK_SECTION_MISSING",sec)
    ac=[int(v) for v in re.findall(r'^\s*(\d+)\.\s+(?:WHEN|IF|WHILE)\b[^\n]*\bSHALL\b',plan,re.M)]
    # Some criteria span multiple lines. We ensure each unique indexed EARS starts with a condition.
    all_starts=[int(v) for v in re.findall(r'^\s*(\d+)\.\s+(?:WHEN|IF|WHILE)\b',plan,re.M)]
    counts={n:all_starts.count(n) for n in set(all_starts)}
    need(set(all_starts)==EXPECTED and all(k==1 for k in counts.values()),"AC_SET_INCOMPLETE",f"AC encontrados: {sorted(all_starts)}")
    for k in EXPECTED:
        m=re.search(rf'^\s*{k}\.\s+(?:WHEN|IF|WHILE)\b(.*?)(?=^\s*\d+\.\s+(?:WHEN|IF|WHILE)\b|^## |^### |\Z)',plan,re.M|re.S)
        need(bool(m and re.search(r'\bSHALL\b',m.group(1))),"AC_SHALL_MISSING",f"AC{k}")
    check_matches=list(re.finditer(r'^\*\*C(\d+)\*\*\s*-\s*(.+?)\(AC\s+(\d+)\)\s*$',checks,re.M))
    pairs=[(int(m.group(1)),int(m.group(3))) for m in check_matches]
    check_ids=[i for i,j in pairs]
    need(set(check_ids)==EXPECTED and len(check_ids)==27 and all(check_ids.count(k)==1 for k in EXPECTED),"CHECK_SET_INCOMPLETE",f"Checks: {check_ids}")
    need(all(i==j for i,j in pairs),"AC_CHECK_MISMATCH",f"Pares fora de ordem: {[x for x in pairs if x[0]!=x[1]]}")
    # Isolate each check block to avoid a proof from next check accidentally satisfying it.
    headings=list(re.finditer(r'^\*\*C\d+\*\*\s*-',checks,re.M))
    for idx,h in enumerate(headings):
        chunk=checks[h.end():headings[idx+1].start() if idx+1<len(headings) else checks.find('## Coverage')]
        n=int(re.search(r'^\*\*C(\d+)\*\*',checks[h.start():]).group(1))
        need(bool(re.search(r'^Proof:[ \t]*\S+',chunk,re.M)),"CHECK_PROOF_MISSING",f"C{n}")
    coverage=re.search(r'^\| EARS criteria \(27\) \|([^\n]+)$',checks,re.M)
    found_pairs=set((int(a),int(b)) for a,b in re.findall(r'AC\s+(\d+)\s+C(\d+)',coverage.group(1) if coverage else ''))
    need(bool(coverage) and found_pairs=={(i,i) for i in EXPECTED},"COVERAGE_INCOMPLETE",f"Cobertura por membro: {len(found_pairs)}/27")
    swept=re.search(r'^## Swept\s*\n(.*?)(?=^## |\Z)',checks,re.M|re.S)
    lines=swept.group(1).lower() if swept else ''
    for s in REQUIRED_SWEEPS:need(bool(re.search(r'^-\s*'+re.escape(s)+r'\s*:',lines,re.M)),"SWEEP_MISSING",s)
    for d in range(1,5):
        need(bool(re.search(r'\bD'+str(d)+r'\s*[—-]',plan)),"DOOR_MISSING",f"D{d}")
    need('personal_results_writes_enabled=false' in plan,"PRIVACY_INVARIANT_MISSING","flag deve permanecer false no PLAN")
    need('DENY:PERSONAL_WRITE_DISABLED' in plan,"PRIVACY_DECISION_MISSING","bloqueio determinístico pessoal")
    need('safe_renderer' in plan and 'tool_gateway' in plan,"RUNTIME_BOUNDARY_MISSING","fronteiras renderer/gateway")
    metrics.update({"ac_count":len(all_starts),"check_count":len(check_ids),"coverage_pairs":len(found_pairs),"proof_lines":len(re.findall(r'^Proof:',checks,re.M)),"swept_dimensions":len([s for s in REQUIRED_SWEEPS if re.search(r'^-\s*'+re.escape(s)+r'\s*:',lines,re.M)]),"one_way_doors":4})
    return {"structural_pass":not issues,"issues":issues,"metrics":metrics}

def audit(root):
    base=Path(root)/'.specs'/'features'/FEATURE
    plan_path=base/'plan.md';checks_path=base/'checks.md'
    if not plan_path.exists() or not checks_path.exists():raise FileNotFoundError("plan.md ou checks.md não encontrado")
    data=audit_text(plan_path.read_text(encoding='utf-8'),checks_path.read_text(encoding='utf-8'))
    data.update({"plan_sha256":sha256(plan_path),"checks_sha256":sha256(checks_path),"independent_verifier_ran":False,"official_tlc_validators_ran":False,"cognitive_llm_trials":0,"operational_checks_executed":0,"outcome":"STRUCTURE_PASS_ONLY" if data['structural_pass'] else "STRUCTURE_FAIL"})
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();result=audit(a.root)
    encoded=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(encoded,encoding='utf-8')
    print(encoded,end='')
    raise SystemExit(0 if result['structural_pass'] else 1)
