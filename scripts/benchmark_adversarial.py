"""Holdout diagnóstico adversarial do edital, sem alterar índices nem aliases."""
import json
from search_edital import ROOT, search

def run(root=ROOT):
    fixture=json.loads((root/'tests/fixtures/adversarial_cases.json').read_text(encoding='utf-8'))
    cases=fixture['cases']
    summary={'positive':0,'hit_at_1':0,'hit_at_3':0,
             'isolations_ok':0,'negatives_ok':0,'conflicts_ok':0,'not_item_ok':0,
             'total_cases':len(cases),'failures':[]}
    for case in cases:
        label=case['kind']
        try:
            result=search(case['query'],cargo=case['cargo'],area=case['area'],
                          root=root,limit=3)
        except ValueError as err:
            if label=='conflict' and 'contradiz' in str(err):
                summary['conflicts_ok']+=1
                continue
            summary['failures'].append({'query':case['query'],'exception':str(err)})
            continue
        ok=True
        if label=='positive':
            summary['positive']+=1
            if result and result[0]['page']==case['page']:
                summary['hit_at_1']+=1
            if any(x['page']==case['page'] for x in result):
                summary['hit_at_3']+=1
            else:
                ok=False
        elif label=='isolation':
            ok=all(x['chunk_id']!=case['forbidden_chunk'] for x in result)
            summary['isolations_ok']+=int(ok)
        elif label=='negative':
            ok=(result==[])
            summary['negatives_ok']+=int(ok)
        elif label=='not_item':
            ok=all(x['route']!='literal_item_marker' for x in result)
            summary['not_item_ok']+=int(ok)
        else:ok=False
        if not ok:
            summary['failures'].append({'query':case['query'],'kind':label,
                                        'results':[x['chunk_id'] for x in result]})
    return summary

if __name__=='__main__':
    metrics=run()
    print(json.dumps(metrics,ensure_ascii=False,indent=2))
    if metrics['failures'] or metrics['hit_at_1']<metrics['positive']:
        raise SystemExit(1)
