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

def _views(chunks, index, cargo, area, root=ROOT):
    """Exclui conteúdo de outros cargos de chunks compartilhados, ao recortar as áreas."""
    ranges=collections.defaultdict(list)
    for topic, loc in _topic_locations(index,cargo,area):
        ranges[loc['chunk_id']].append((loc['chunk_char_start'],loc['chunk_char_end']))
    # Anexo IV: excluir integralmente as descrições de cargos vizinhos.
    attrib_spans={}
    if cargo is not None and area is None:
        from index_atribuicoes import build as build_atribuicoes
        attrib_index=build_atribuicoes(root)
        attrib_spans={
            entry["chunk_id"]:(entry["chunk_char_start"],entry["chunk_char_end"])
            for entry in attrib_index["entries"] if entry["cargo"] == cargo
        }
    views=[]
    for c in chunks:
        if cargo is not None and area is None and 20 <= c["page"] <= 28:
            if c["id"] not in attrib_spans:
                continue
            a,b=attrib_spans[c["id"]]
            views.append({**c,"search_body":c["body"][a:b]})
            continue
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
        "route":"quadro_vagas_derived_verified_anchors","annex":"III",
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

def search_atribuicao(cargo, root=ROOT, full=False):
    """Retorna o parágrafo literal do Anexo IV, excluindo cargos vizinhos."""
    from index_atribuicoes import build, locate, validate
    validate(root)
    index = build(root)
    matches = [x for x in index["entries"] if x["cargo"] == str(cargo)]
    if len(matches) != 1:
        raise ValueError("Cargo não indexado no Anexo IV")
    entry = matches[0]
    chunk = next(c for c in load(root) if c["id"] == entry["chunk_id"])
    span = locate(entry, chunk)
    result = {
        "cargo": entry["cargo"], "page": entry["page"],
        "chunk_id": entry["chunk_id"], "path": entry["path"],
        "source": index["source"],
        "source_sha": index["source_git_blob_sha"],
        "source_pdf_sha256": index["source_pdf_sha256"],
        "route": "anexo_iv_atribuicoes_literal", "annex": "IV",
        "classification": "literal_source_with_derived_locator",
        "page_char_start": entry["page_char_start"],
        "page_char_end": entry["page_char_end"],
        "chunk_char_start": entry["chunk_char_start"],
        "chunk_char_end": entry["chunk_char_end"],
        "literal_sha256": entry["literal_sha256"],
        "excerpt": " ".join(span["text"].split())[:220],
    }
    if full:
        result["text"] = span["text"]
    return result

def search_programa(cargo, root=ROOT, full=False, area=None):
    """Inventário integral do Anexo V para um cargo, sem inferência de conteúdo."""
    if str(cargo) not in ("523", "324"):
        raise ValueError("Cargo não indexado no Anexo V")
    if area not in (None, "gerais", "especificos"):
        raise ValueError("Área inválida no Anexo V")
    from index_edital import validate as validate_topics
    validate_topics(root)
    index=topic_index(root)
    by_id={c["id"]:c for c in load(root)}
    selected=[t for t in index["topics"]
              if str(cargo) in t["cargo_ids"]
              and (area is None or t["area"]==area)]
    expected=14 if str(cargo)=="523" else 13
    if area is None and len(selected)!=expected:
        raise ValueError("Anexo V não contém o conjunto completo esperado")
    if area=="gerais" and len(selected)!=4:
        raise ValueError("Conhecimentos gerais incompletos")
    if area=="especificos" and len(selected)!=expected-4:
        raise ValueError("Conhecimentos específicos incompletos")
    topics=[]
    for t in selected:
        locations=[]
        for loc in t["locations"]:
            c=by_id[loc["chunk_id"]]
            a,b=loc["chunk_char_start"],loc["chunk_char_end"]
            if c["page"]!=loc["page"] or not (0<=a<b<=len(c["body"])):
                raise ValueError("Offsets de tópico incompatíveis")
            literal=c["body"][a:b]
            record={**loc,"excerpt":" ".join(literal.split())[:180]}
            if full:record["text"]=literal
            locations.append(record)
        topics.append({"topic_id":t["topic_id"],"title":t["title"],
                       "area":t["area"],"locations":locations})
    return {"cargo":str(cargo),"annex":"V",
            "route":"anexo_v_programa_literal",
            "classification":"literal_source_with_derived_topic_index",
            "source":index["source"],"source_sha":index["source_git_blob_sha"],
            "source_pdf_sha256":index["source_pdf_sha256"],
            "num_topics":len(topics),"area":area or "todos",
            "topics":topics}


def search_anexo(cargo, anexo, root=ROOT, full=False, area=None):
    """Roteamento explícito: III=requisitos, IV=atribuições, V=programa."""
    if str(cargo) not in ("523","324"):
        raise ValueError("Cargo não indexado")
    if anexo not in ("III","IV","V"):
        raise ValueError("Anexo inválido (III, IV ou V)")
    if anexo in ("III","IV") and area is not None:
        raise ValueError("Filtro --area somente é válido para Anexo V")
    if anexo=="III":
        return search_vaga(cargo,root,full)
    if anexo=="IV":
        return search_atribuicao(cargo,root,full)
    return search_programa(cargo,root,full,area)


def search(query='',limit=4,cargo=None,root=ROOT,topic=None,area=None,full=False,neighbors=False,anexo=None):
    if cargo not in (None,'523','324'): raise ValueError('Cargo inválido')
    if area not in (None,'gerais','especificos'): raise ValueError('Área inválida')
    if area=='especificos' and cargo is None:
        raise ValueError('Informe --cargo para conhecimentos específicos')
    if not 1<=limit<=20: raise ValueError('Limite inválido')
    if anexo is not None and anexo not in ('III','IV','V'):
        raise ValueError('Anexo inválido')
    if anexo is not None and cargo is None:
        raise ValueError('Informe --cargo para selecionar o anexo')
    if anexo in ('III','IV') and topic is not None:
        raise ValueError('Tópico do Anexo V incompatível com outro anexo')
    if anexo in ('III','IV') and area is not None:
        raise ValueError('Filtro de área somente para Anexo V')
    # Não transformar perguntas de comparação em resposta parcial sobre um cargo.
    mentioned=re.findall(r'\b(?:cargo|c[oó]digo)\s*(?:n[º°.]?\s*)?(523|324)\b',query,re.I)
    if len(set(mentioned))>1:
        raise ValueError('Consulta menciona múltiplos cargos; consulte cada cargo separadamente')
    # Consultas que nomeiam outro cargo contradizem o filtro explícito: falha segura.
    declared=re.search(r'\b(?:cargo|c[oó]digo)\s*(?:n[º°.]?\s*)?(523|324)\b',query,re.I)
    if cargo and declared and declared.group(1)!=cargo:
        raise ValueError('Cargo da consulta contradiz --cargo')
    if anexo is not None:
        if topic is not None and anexo=='V':
            raise ValueError('Use --topic separadamente de --anexo V')
        return [search_anexo(cargo,anexo,root,full,area)]
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
    # Os anexos têm objetos jurídicos distintos; consultas misturadas falham sem
    # usar similaridade lexical como substituto da evidência normativa.
    target=(declared.group(1) if declared else cargo)
    query_clean=normalized(query)
    ann_mentions=re.findall(r'\banexos?\s+(iii|iv|v)\b',query_clean)
    annex_name={"iii":"III","iv":"IV","v":"V"}
    explicit_annexes={annex_name[x] for x in ann_mentions}
    role_intents=set(explicit_annexes)
    if re.search(r'\b(atribuicoes?|funcoes?|responsabilidades?|o que faz|descricao do cargo|tarefas do cargo)\b',
                 query_clean):
        role_intents.add("IV")
    if re.search(r'\b(vagas?|requisitos?|escolaridade|lotacao|formacao|localidade|habilitacao para o cargo)\b',
                 query_clean):
        role_intents.add("III")
    if re.search(r'\b(conteudo programatico|ementa|o que cai|conhecimentos especificos|conhecimentos gerais|disciplinas|materias da prova|assuntos (?:da prova|cobrados)|topicos (?:da prova|cobrados))\b',
                 query_clean):
        role_intents.add("V")
    if target and len(role_intents)>1:
        if role_intents=={"III","IV"}:
            raise ValueError("Consulta mistura atribuições e requisitos; consulte separadamente")
        raise ValueError("Consulta mistura anexos distintos; consulte cada anexo separadamente")
    if target and role_intents:
        chosen=next(iter(role_intents))
        if chosen in ("III","IV") and area is not None:
            raise ValueError("Filtro de área não é válido para este anexo")
        if chosen=="V":
            inferred_area=area
            if inferred_area is None:
                if "conhecimentos especificos" in query_clean or "conteudo especifico" in query_clean:
                    inferred_area="especificos"
                elif "conhecimentos gerais" in query_clean:
                    inferred_area="gerais"
            return [search_anexo(target,"V",root,full,inferred_area)]
        return [search_anexo(target,chosen,root,full)]

    attr_intent=bool(re.search(
        r'\b(atribuicoes?|funcoes?|responsabilidades?|o que faz|descricao do cargo)\b',
        query_clean))
    vagas_intent=bool(re.search(
        r'\b(vagas?|requisitos?|escolaridade|lotacao|formacao|localidade)\b',
        query_clean))
    if target and area is None and attr_intent and vagas_intent:
        raise ValueError("Consulta mistura atribuições e requisitos; consulte separadamente")
    if target and area is None and attr_intent:
        return [search_atribuicao(target,root,full)]
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
    views=_views(chunks,index,cargo,area,root)
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
    p.add_argument('--conteudo-cargo',choices=['523','324'],help='Programa completo do Anexo V')
    p.add_argument('--anexo',choices=['III','IV','V'],help='Selecionar fonte de forma explícita (requer --cargo)')
    p.add_argument('--atribuicoes-cargo',choices=['523','324'],help='Descrição literal do Anexo IV')
    p.add_argument('--full',action='store_true',help='Incluir texto literal do trecho selecionado')
    p.add_argument('--neighbors',action='store_true',help='Indicar chunks adjacentes para expansão')
    a=p.parse_args()
    if a.anexo:print(json.dumps(search_anexo(a.cargo,a.anexo,ROOT,a.full,a.area),ensure_ascii=False,indent=2))
    elif a.conteudo_cargo:print(json.dumps(search_programa(a.conteudo_cargo,ROOT,a.full,a.area),ensure_ascii=False,indent=2))
    elif a.atribuicoes_cargo:print(json.dumps(search_atribuicao(a.atribuicoes_cargo,ROOT,a.full),ensure_ascii=False,indent=2))
    elif a.vagas_cargo:print(json.dumps(search_vaga(a.vagas_cargo,ROOT,a.full),ensure_ascii=False,indent=2))
    elif a.page:print(page_text(a.page))
    elif a.query or a.topic:print(json.dumps(search(a.query,a.limit,a.cargo,ROOT,a.topic,a.area,a.full,a.neighbors),ensure_ascii=False,indent=2))
    else:p.error('Informe uma consulta, --topic ou --page')

if __name__=='__main__':main()
