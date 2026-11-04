"""Métrica reproduzível de recuperação (conjunto diagnóstico curado, não recall universal)."""
import json
from pathlib import Path
from search_edital import ROOT, search

def run(root=ROOT):
    cases=json.loads((root/'tests/fixtures/retrieval_cases.json').read_text(encoding='utf-8'))['cases']
    source=(root/'EDITAL_UFMS_152_2026.md').read_text(encoding='utf-8')
    good_at_1=good_at_3=negative_ok=0
    positive=negative=0
    chars=0
    failures=[]
    for c in cases:
        results=search(c['query'],limit=3,cargo=c['cargo'],area=c['area'],
                       root=root,full=True)
        chars+=sum(len(r.get('text','')) for r in results)
        if c['type']=='negative':
            negative+=1
            if not results:negative_ok+=1
            else:failures.append({'query':c['query'],'issue':'false_positive',
                                  'chunks':[r['chunk_id'] for r in results]})
            continue
        positive+=1
        match=(lambda r:r['page']==c['page']) if c['type']=='rule' else (
            lambda r:r.get('topic_id')==c['topic_id'] and r['page']==c['page'])
        if results and match(results[0]):good_at_1+=1
        if any(match(r) for r in results):good_at_3+=1
        else:failures.append({'query':c['query'],'issue':'not_in_top3',
                              'chunks':[r['chunk_id'] for r in results]})
    report={
        'source':'EDITAL_UFMS_152_2026.md',
        'kind':'curated_diagnostic_queries_not_global_recall',
        'positive_cases':positive,'negative_cases':negative,
        'hit_at_1':f'{good_at_1}/{positive}',
        'hit_at_3':f'{good_at_3}/{positive}',
        'negative_correct':f'{negative_ok}/{negative}',
        'total_retrieved_characters':chars,
        'full_document_characters':len(source),
        'retrieval_vs_full_for_each_query':round(
            chars/(len(source)*len(cases)),6),
        'failures':failures}
    return report

if __name__=='__main__':
    result=run()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if result['failures']:
        raise SystemExit(1)
