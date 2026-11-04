"""Busca em camadas: tópico/alias -> BM25 -> expansão controlada; sem serviços externos."""
import argparse
import collections
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FENCE = chr(96) * 3
STOP = {'a','as','o','os','e','de','da','das','do','dos','em','na','nas',
        'no','nos','para','por','com','um','uma','que','ou','ao','aos','sobre'}

def terms(value):
    text = ''.join(ch for ch in unicodedata.normalize('NFKD', value.casefold())
                   if not unicodedata.combining(ch))
    return [w for w in re.findall(r'[a-z0-9]+', text) if len(w)>1 and w not in STOP]

def normalized(value):
    return ' '.join(re.findall(r'[a-z0-9]+',
        ''.join(ch for ch in unicodedata.normalize('NFKD',value.casefold())
                if not unicodedata.combining(ch))))

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

def topic_index(root=ROOT):
    index=json.loads((root/'edital/topic_index.json').read_text(encoding='utf-8'))
    manifest=json.loads((root/'edital/manifest.json').read_text(encoding='utf-8'))
    if index['source_git_blob_sha'] != manifest['source_git_blob_sha']:
        raise ValueError('Índice de tópicos incompatível com a fonte')
    return index

def _topic_locations(index, cargo=None, area=None):
    for t in index['topics']:
        if cargo is not None and cargo not in t['cargo_ids']:
            continue
        if area is not None and t['area'] != area:
            continue
        for loc in t['locations']:
            yield t, loc

def _views(chunks, index, cargo, area):
    """Exclui conteúdo de outros cargos de chunks compartilhados, ao recortar as áreas."""
    ranges=collections.defaultdict(list)
    for topic, loc in _topic_locations(index,cargo,area):
        ranges[loc['chunk_id']].append((loc['chunk_char_start'],loc['chunk_char_end']))
    views=[]
    for c in chunks:
        relevant=ranges.get(c['id'])
        # Com cargo informado, descartar programas de OUTROS cargos, inclusive
        # quando --area não foi informado. Regras comuns fora do Anexo V ficam acessíveis.
        if (area is not None or (cargo is not None and 29 <= c['page'] <= 45)) and not relevant:
            continue
        if relevant:
            # Os tópicos oficiais formam intervalos adjacentes por programa.
            spans=sorted(relevant)
            body='\n'.join(c['body'][a:b] for a,b in spans)
        else:
            body=c['body']
        views.append({**c, 'search_body':body})
    return views

def _neighbors(chunk, chunks):
    same=[c for c in chunks if c['page']==chunk['page']]
    return [{'chunk_id':c['id'],'path':c['path'],'page':c['page']}
            for c in same if abs(c['segment']-chunk['segment'])==1]

def section_results(number,chunks,source_sha,limit=4,full=False,neighbors=False):
    """Roteamento por item literal, sem inferir abrangência jurídica do item."""
    if not re.fullmatch(r'[1-9][0-9]?(?:\.[0-9]{1,3}){1,3}',number):
        raise ValueError('Item inválido')
    marker=re.compile(r'(?m)^[ \t]*'+re.escape(number)+r'\.[ \t]+')
    results=[]
    for c in chunks:
        for match in marker.finditer(c['body']):
            start=match.start()
            # Apresenta uma janela literal e pequena; se necessário, abrir o chunk inteiro.
            end=min(len(c['body']),start+450)
            fragment=c['body'][start:end]
            result={'chunk_id':c['id'],'path':c['path'],'page':c['page'],
                    'score':1.0,'excerpt':' '.join(fragment.split())[:220],
                    'source':'EDITAL_UFMS_152_2026.md','source_sha':source_sha,
                    'route':'literal_item_marker',
                    'classification':'source_excerpt',
                    'item':number,
                    'page_char_start':c['char_start']+start,
                    'page_char_end':c['char_start']+end}
            if full:result['text']=fragment
            if neighbors:result['adjacent_chunks']=_neighbors(c,chunks)
            results.append(result)
            if len(results)>=limit:return results
    return results

def search_vaga(code,root=ROOT,full=False):
    """Recupera SOMENTE a linha do quadro de vagas auditada no PDF original."""
    from index_vagas import build, locate_row
    index=build(root)
    matches=[entry for entry in index["entries"] if entry["cargo"]==str(code)]
    if len(matches)!=1: raise ValueError("Cargo não indexado no quadro de vagas")
    entry=matches[0]
    located=locate_row(entry,root)
    result={"cargo":entry["cargo"],"page":entry["page"],"chunk_id":entry["chunk_id"],
        "path":entry["path"],"source":index["source"],
        "source_sha":index["source_git_blob_sha"],
        "source_pdf_sha256":index["source_pdf_sha256"],
        "route":"quadro_vagas_derived_verified_anchors",
        "classification":"derived_metadata_with_literal_evidence",
        "normalized_name":entry["normalized_name"],
        "vacancies":entry["vacancies"],"location":entry["location"],
        "page_char_start":located["page_char_start"],
        "page_char_end":located["page_char_end"],
        "pdf_row_rect":entry["pdf_row_rect"],
        "field_evidence":located["fields"],
        "excerpt":" ".join(located["text"].split())[:240]}
    if full:result["text"]=located["text"]
    return result

def search(query='',limit=4,cargo=None,root=ROOT,topic=None,area=None,full=False,neighbors=False):
    if cargo not in (None,'523','324'): raise ValueError('Cargo inválido')
    if area not in (None,'gerais','especificos'): raise ValueError('Área inválida')
    if area=='especificos' and cargo is None:
        raise ValueError('Informe --cargo para conhecimentos específicos')
    if not 1<=limit<=20: raise ValueError('Limite inválido')
    # Consultas que nomeiam outro cargo contradizem o filtro explícito: falha segura.
    declared=re.search(r'\b(?:cargo|c[oó]digo)\s*(?:n[º°.]?\s*)?(523|324)\b',query,re.I)
    if cargo and declared and declared.group(1)!=cargo:
        raise ValueError('Cargo da consulta contradiz --cargo')
    index=topic_index(root)
    chunks=load(root)
    selected=[t for t in index['topics']
              if (cargo is None or cargo in t['cargo_ids'])
              and (area is None or t['area']==area)]
    by_topic={t['topic_id']:t for t in selected}
    source_sha=index['source_git_blob_sha']
    if topic is not None:
        if topic not in by_topic: raise ValueError('Tópico ausente ou incompatível: '+topic)
        return direct_results([by_topic[topic]],chunks,'topic_id',limit,source_sha,full,neighbors)
    # Item explícito precede BM25, mas não atravessa filtros de áreas específicas.
    if area is None:
        item_match=re.search(r'(?<![\w.])([1-9][0-9]?(?:\.[0-9]{1,3}){1,3})(?![\d.])',query)
        if item_match:
            located=section_results(item_match.group(1),chunks,source_sha,
                                    limit,full,neighbors)
            if located:return located
    # Consulta do quadro de vagas exige cargo inequívoco e intenção de vaga/requisito.
    target=(declared.group(1) if declared else cargo)
    if target and area is None and re.search(
            r'\b(vagas?|requisitos?|escolaridade|lotacao|formacao|localidade)\b',
            normalized(query)):
        return [search_vaga(target,root,full)]
    normalized_query=normalized(query)
    if not normalized_query:return []
    # Roteamento direto exige título completo, ID exato ou alias com limites de palavra.
    ranked=[]
    for t in selected:
        candidates=[t['title']]+t['aliases']+[t['topic_id']]
        hits=[len(normalized(s)) for s in candidates
              if normalized(s) and ' '+normalized(s)+' ' in ' '+normalized_query+' ']
        if hits:ranked.append((max(hits),t))
    if ranked:
        ranked.sort(key=lambda pair:(-pair[0],pair[1]['topic_id']))
        max_match=ranked[0][0]
        return direct_results([t for score,t in ranked if score==max_match],
                              chunks,'derived_alias_or_title',limit,source_sha,full,neighbors)
    wanted=set(terms(query))
    if not wanted:return []
    views=_views(chunks,index,cargo,area)
    cnts=[collections.Counter(terms(c['search_body'])) for c in views]
    lengths=[sum(c.values()) for c in cnts]
    n=len(views)
    if not n:return []
    avg=sum(lengths)/n or 1
    df={w:sum(w in c for c in cnts) for w in wanted}
    ranked=[]
    for c,cnt,length in zip(views,cnts,lengths):
        score=0.0
        for w in wanted:
            tf=cnt[w]
            if not tf:continue
            idf=math.log(1+(n-df[w]+0.5)/(df[w]+0.5))
            score+=idf*(tf*2.2)/(tf+1.2*(0.25+0.75*length/avg))
        # BM25 de correspondência em apenas uma palavra de consultas longas
        # produz falsos positivos, especialmente ao comparar cargos vizinhos.
        if score<=0 or (len(wanted)>=3 and sum(w in cnt for w in wanted)<2):
            continue
        if cargo and 'cargo_'+cargo in c['categories']:score*=1.35
        if cargo and 'conhecimentos_gerais' in c['categories']:score*=1.1
        excerpt=next((line.strip() for line in c['search_body'].splitlines()
                      if len(line.strip())>16 and wanted.intersection(terms(line))),'')[:220]
        result={'chunk_id':c['id'],'path':c['path'],'page':c['page'],
                'score':round(score,3),'excerpt':excerpt,
                'source':'EDITAL_UFMS_152_2026.md','source_sha':source_sha,
                'route':'bm25','classification':'source_excerpt'}
        if full:result['text']=c['search_body']
        if neighbors:result['adjacent_chunks']=_neighbors(c,chunks)
        ranked.append(result)
    ranked.sort(key=lambda x:(-x['score'],x['page'],x['chunk_id']))
    return ranked[:limit]

def direct_results(topics,chunks,why,limit,source_sha,full=False,neighbors=False):
    by_id={c['id']:c for c in chunks}
    results=[]
    for topic in topics:
        for loc in topic['locations']:
            c=by_id[loc['chunk_id']]
            passage=c['body'][loc['chunk_char_start']:loc['chunk_char_end']]
            result={'chunk_id':c['id'],'path':c['path'],'page':c['page'],
                    'score':1.0,'excerpt':' '.join(passage.split())[:220],
                    'source':'EDITAL_UFMS_152_2026.md','source_sha':source_sha,
                    'route':why,'topic_id':topic['topic_id'],
                    'classification':'derived_routing_with_literal_excerpt',
                    'page_char_start':loc['page_char_start'],
                    'page_char_end':loc['page_char_end']}
            if full:result['text']=passage
            if neighbors:result['adjacent_chunks']=_neighbors(c,chunks)
            results.append(result)
            if len(results)>=limit:return results
    return results

def page_text(page,root=ROOT):
    chunks=[c for c in load(root) if c['page']==page]
    if not chunks:raise ValueError('Página não encontrada')
    return '\n'.join(f"[{c['path']}]\n{c['body']}" for c in chunks)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('query',nargs='?',default='')
    p.add_argument('--limit',type=int,default=4)
    p.add_argument('--cargo',choices=['523','324'])
    p.add_argument('--area',choices=['gerais','especificos'])
    p.add_argument('--topic',help='ID de config/topics.csv, por exemplo 523-06')
    p.add_argument('--page',type=int,choices=range(1,48))
    p.add_argument('--vagas-cargo',choices=['523','324'],help='Linha exata do Anexo III')
    p.add_argument('--full',action='store_true',help='Incluir texto literal do trecho selecionado')
    p.add_argument('--neighbors',action='store_true',help='Indicar chunks adjacentes para expansão')
    a=p.parse_args()
    if a.vagas_cargo:print(json.dumps(search_vaga(a.vagas_cargo,ROOT,a.full),ensure_ascii=False,indent=2))
    elif a.page:print(page_text(a.page))
    elif a.query or a.topic:print(json.dumps(search(a.query,a.limit,a.cargo,ROOT,a.topic,a.area,a.full,a.neighbors),ensure_ascii=False,indent=2))
    else:p.error('Informe uma consulta, --topic ou --page')

if __name__=='__main__':main()
