#!/usr/bin/env python3
"""Complementar structure gate reproducing limited public requirements of TLC validate_plan.py.
NOT official TLC validator, NOT semantic independent auditor.
"""
from pathlib import Path
import json,re,sys
REQ=['Problem','Flow','Impact','Relations','Surface','Landing','Criteria','Out of scope','Assumptions','Observable']
STATUS=re.compile(r'\b[1-5]\d\d\b')
def audit(plan,checks):
    problems=[]; headings=set(re.findall(r'^## (.+)$',plan,re.M))
    for name in REQ:
        if name not in headings: problems.append('MISSING_SECTION:'+name)
    b=re.search(r'(?ms)^## Surface\n(.*?)(?=^## |\Z)',plan)
    cells=[]
    if b:
        rows=[r for r in b.group(1).splitlines() if r.startswith('|') and not r.startswith('| ---')]
        for line in rows[1:]:
            x=[v.strip() for v in line.strip('|').split('|')]
            if len(x)<4: problems.append('BAD_SURFACE_ROW');continue
            if not STATUS.search(x[3]):problems.append('MISSING_NUMERIC_STATUS:'+x[0]);continue
            cells.append((x[0],x[3]))
    if len(cells)!=4:problems.append('SURFACE_FOUR_REQUIRED')
    ob=re.search(r'(?ms)^## Observable\n(.*?)(?=^## |\Z)',plan)
    if ob:
        rows=[x for x in ob.group(1).splitlines() if x.startswith('|') and not x.startswith('| ---')]
        if len(rows)-1 !=16:problems.append('OBSERVABLE_16_REQUIRED')
        for line in rows[1:]:
            c=[v.strip() for v in line.strip('|').split('|')]
            if len(c)<3 or not re.search(r'AC\d\d',c[2]):problems.append('OBSERVABLE_LANDING_MISSING')
    acc=re.findall(r'(?m)^([1-9]\d?)\.\s+(.+)$',plan.split('## Criteria',1)[1].split('## Observable',1)[0])
    num=[int(i) for i,t in acc if int(i)<=27 and 'SHALL' in t]
    if num != list(range(1,28)):problems.append('AC_SHALL_27_MISMATCH')
    if 'AGUARDA APROVAÇÃO HUMANA' not in plan:problems.append('WRONG_APPROVAL_STATUS')
    if '**Approved**:' in plan:problems.append('FALSE_APPROVAL')
    if 'revisions/v0.3/plan.md' not in checks:problems.append('CHECKS_PLAN_WRONG_VERSION')
    if 'NOT_RUN' not in checks:problems.append('MISSING_UNRUN_LABEL')
    if 'Surface aliases' not in checks:problems.append('MISSING_STATUS_JOIN')
    return problems
if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
    errors=audit((root/'plan.md').read_text(),(root/'checks-preview.md').read_text())
    print(json.dumps({'pass':not errors,'errors':errors,'official':False},ensure_ascii=False,indent=2))
    raise SystemExit(1 if errors else 0)
