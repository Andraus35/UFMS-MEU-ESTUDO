"""Busca lexical BM25 nos chunks, sem rede, embeddings ou dependências."""
import argparse
import collections
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FENCE=chr(96)*3
STOP={'a','as','o','os','e','de','da','das','do','dos','em','na','nas','no','nos','para','por','com','um','uma','que','ou','ao','aos','sobre'}

def terms(value):
    text=''.join(ch for ch in unicodedata.normalize('NFKD',value.casefold()) if not unicodedata.combining(ch))
    return [w for w in re.findall(r'[a-z0-9]+',text) if len(w)>1 and w not in STOP]

def load(root=ROOT):
    manifest=json.loads((root/'edital/manifest.json').read_text(encoding='utf-8'))
    chunks=[]
    pattern=re.escape(FENCE)+r'text\n([\s\S]*?)\n'+re.escape(FENCE)+r'\n?$'
    for meta in manifest['chunks']:
        data=(root/meta['path']).read_text(encoding='utf-8')
        match=re.search(pattern,data)
        if not match: raise ValueError('Chunk malformado: '+meta['path'])
        chunks.append({**meta,'body':match.group(1)})
    return chunks

def search(query,limit=4,cargo=None,root=ROOT):
    if cargo not in (None,'523','324'): raise ValueError('Cargo inválido')
    if not 1<=limit<=20: raise ValueError('Limite inválido')
    wanted=set(terms(query))
    if not wanted: return []
    chunks=load(root)
    cnts=[collections.Counter(terms(c['body'])) for c in chunks]
    lengths=[sum(c.values()) for c in cnts]
    n=len(chunks); average=sum(lengths)/n if n else 1
    df={w:sum(w in c for c in cnts) for w in wanted}
    ranked=[]
    for chunk,cnt,length in zip(chunks,cnts,lengths):
        score=0
        for w in wanted:
            tf=cnt[w]
            if not tf: continue
            idf=math.log(1+(n-df[w]+0.5)/(df[w]+0.5))
            score+=idf*(tf*2.2)/(tf+1.2*(0.25+0.75*length/average))
        if score<=0: continue
        if cargo and f'cargo_{cargo}' in chunk['categories']: score*=1.35
        if cargo and 'conhecimentos_gerais' in chunk['categories']: score*=1.1
        excerpt=next((line.strip() for line in chunk['body'].splitlines()
                      if len(line.strip())>16 and wanted.intersection(terms(line))),'')[:220]
        ranked.append({'chunk_id':chunk['id'],'path':chunk['path'],
                       'page':chunk['page'],'score':round(score,3),
                       'excerpt':excerpt,'source':'EDITAL_UFMS_152_2026.md'})
    ranked.sort(key=lambda x:(-x['score'],x['page'],x['chunk_id']))
    return ranked[:limit]

def page_text(page,root=ROOT):
    chunks=[c for c in load(root) if c['page']==page]
    if not chunks: raise ValueError('Página não encontrada')
    return '\n'.join(f"[{c['path']}]\n{c['body']}" for c in chunks)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query',nargs='?')
    parser.add_argument('--limit',type=int,default=4)
    parser.add_argument('--cargo',choices=['523','324'])
    parser.add_argument('--page',type=int,choices=range(1,48))
    a=parser.parse_args()
    if a.page: print(page_text(a.page))
    elif a.query: print(json.dumps(search(a.query,a.limit,a.cargo),ensure_ascii=False,indent=2))
    else: parser.error('Informe uma consulta ou --page')

if __name__=="__main__": main()
