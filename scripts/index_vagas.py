"""Índice auditável de linhas do Anexo III. Dados derivados, não normativos."""
import argparse
import json
import re
from pathlib import Path
from chunk_edital import SOURCE, blob_sha

ROOT=Path(__file__).resolve().parents[1]
SPECS=(
    {"cargo":"523","page":15,"chunk_id":"p15-c01",
     "normalized_name":"Analista em Educação / Administração e Informação / Gestão Pública",
     "vacancies":29,"location":"Campo Grande","pdf_row_rect":[70,110,560,250],
     "before_code":"Curso Superior em Administração, Administração",
     "after_code":"Curso Superior em Administração, Administração",
     "evidence_anchors":[
         {"field":"role","literal":"Analista em Educação/ Administração e"},
         {"field":"specialty","literal":"Gestão Pública**"},
         {"field":"qualification_option_a","literal":"Curso Superior em Administração, Administração"},
         {"field":"qualification_connector","literal":"OU"},
         {"field":"qualification_option_b","literal":"Curso Superior em qualquer área do conhecimento,"},
         {"field":"qualification_specialization","literal":"Especialização em Gestão Pública, em nível de"},
         {"field":"qualification_hours","literal":"mínima de 360 horas, reconhecida pelo MEC"}
     ]},
    {"cargo":"324","page":18,"chunk_id":"p18-c02",
     "normalized_name":"Técnico em Educação / Processos Educacionais / Assuntos Estudantis",
     "vacancies":18,"location":"Campo Grande","pdf_row_rect":[70,640,560,660],
     "before_code":"Técnico em Educação/Processos Educacionais/",
     "after_code":"Técnico em Educação/Processos",
     "evidence_anchors":[
         {"field":"role","literal":"Técnico em Educação/Processos Educacionais/"},
         {"field":"specialty","literal":"Assuntos Estudantis**"},
         {"field":"qualification","literal":"Ensino Médio completo"}
     ]})

def build(root=ROOT):
    manifest=json.loads((root/"edital/manifest.json").read_text(encoding="utf-8"))
    canonical=(root/SOURCE).read_text(encoding="utf-8")
    if manifest["source"]!=SOURCE or blob_sha(canonical)!=manifest["source_git_blob_sha"]:
        raise ValueError("Identidade da fonte canônica divergente")
    chunks={m["id"]:m for m in manifest["chunks"]}
    result={"schema_version":"1.0","classification":"derived_non_normative",
        "source":SOURCE,"source_git_blob_sha":manifest["source_git_blob_sha"],
        "source_pdf_sha256":manifest["source_pdf_sha256"],
        "description":"Campos dos cargos 523 e 324 no Anexo III; coordenadas PDF auditadas visualmente; offsets derivados dos chunks.",
        "entries":[{**s,"path":chunks[s["chunk_id"]]["path"]} for s in SPECS]}
    for entry in result["entries"]: locate_row(entry,root,manifest)
    return result

def _field(field,literal,start,meta):
    return {"field":field,"literal":literal,
        "chunk_char_start":start,"chunk_char_end":start+len(literal),
        "page_char_start":meta["char_start"]+start,
        "page_char_end":meta["char_start"]+start+len(literal)}

def locate_row(entry,root=ROOT,manifest=None):
    if manifest is None:
        manifest=json.loads((root/"edital/manifest.json").read_text(encoding="utf-8"))
    matches=[m for m in manifest["chunks"] if m["id"]==entry["chunk_id"]]
    if len(matches)!=1:raise ValueError("Chunk não encontrado")
    meta=matches[0]
    if meta["page"]!=entry["page"] or meta["path"]!=entry["path"]:
        raise ValueError("Metadados de chunk divergentes")
    text=(root/meta["path"]).read_text(encoding="utf-8")
    fence=re.escape(chr(96)*3)
    match=re.search(fence+r'text\n([\s\S]*?)\n'+fence+r'\n?$',text)
    if not match:raise ValueError("Chunk de vagas malformado")
    body=match.group(1)
    code=entry["cargo"];vacancies=str(entry["vacancies"])
    row_pattern=re.compile(r"(?m)^[ \t]*"+re.escape(code)+r"[ \t]+"+
        re.escape(vacancies)+r"[ \t]+"+re.escape(entry["location"])+r"[^\n]*(?:\n|$)")
    found=list(row_pattern.finditer(body))
    if len(found)!=1:raise ValueError("Linha de código/vagas/lotação não única: "+code)
    pos=found[0].start()
    begin=body.rfind(entry["before_code"],0,pos)
    end=body.find(entry["after_code"],found[0].end())
    if begin<0 or end<=pos:raise ValueError("Limites da linha de tabela não encontrados: "+code)
    row=body[begin:end]
    if len(row)>3200:raise ValueError("Linha excede limite de contexto")
    code_line=body[found[0].start():found[0].end()]
    fields=[]
    for field,literal in (("cargo_code",code),("vacancies",vacancies),("location",entry["location"])):
        matches=list(re.finditer(r"(?<!\w)"+re.escape(literal)+r"(?!\w)",code_line))
        if len(matches)!=1:raise ValueError("Campo base ambíguo: "+field)
        start=found[0].start()+matches[0].start()
        fields.append(_field(field,literal,start,meta))
    for anchor in entry["evidence_anchors"]:
        literal=anchor["literal"]
        positions=[m.start() for m in re.finditer(re.escape(literal),row)]
        if len(positions)!=1:raise ValueError("Âncora ambígua/ausente: "+code+" "+anchor["field"])
        fields.append(_field(anchor["field"],literal,begin+positions[0],meta))
    if any(f["chunk_char_start"]<begin or f["chunk_char_end"]>end for f in fields):
        raise ValueError("Campo fora do recorte do cargo")
    return {"text":row,"chunk_char_start":begin,"chunk_char_end":end,
        "page_char_start":meta["char_start"]+begin,
        "page_char_end":meta["char_start"]+end,"fields":fields}

def validate(root=ROOT):
    actual=json.loads((root/"edital/vagas_index.json").read_text(encoding="utf-8"))
    if actual!=build(root):raise ValueError("Índice de vagas divergente")
    return len(actual["entries"])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--write",action="store_true")
    a=p.parse_args()
    if a.write:
        (ROOT/"edital/vagas_index.json").write_text(
            json.dumps(build(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"OK: {validate()} linhas de vagas e requisitos vinculadas à fonte")
if __name__=="__main__":main()
