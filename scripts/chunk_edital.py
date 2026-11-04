"""Segmentação reversível e verificação dos 81 trechos, sem dependências externas."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE="EDITAL_UFMS_152_2026.md"
DIR="edital/chunks"
FENCE=chr(96)*3
MAX=7200
MIN=1500

def blob_sha(text):
    b=text.encode("utf-8")
    return hashlib.sha1(f"blob {len(b)}\0".encode("ascii")+b).hexdigest()

def read_pages(text):
    heads=list(re.finditer(r"^## Página (\d+) de 47$",text,re.M))
    if len(heads)!=47: raise ValueError("Edital deve conter 47 páginas")
    pages=[]
    for i,h in enumerate(heads):
        num=int(h.group(1))
        if num!=i+1: raise ValueError("Página fora de ordem")
        end=heads[i+1].start() if i+1<len(heads) else len(text)
        block=text[h.end():end]
        match=re.fullmatch(r"\n\n"+FENCE+r"text\n([\s\S]*?)\n"+FENCE+r"\n\n",block)
        if not match: raise ValueError(f"Delimitação da página {num} inválida")
        pages.append((num,match.group(1)))
    return pages

def split_page(body):
    count=max(1,(len(body)+MAX-1)//MAX)
    parts=[]
    start=0
    for seg in range(1,count):
        remaining=count-seg+1
        target=start+(len(body)-start+remaining//2)//remaining
        lo=max(start+MIN,len(body)-MAX*(remaining-1))
        hi=min(start+MAX,len(body)-MIN*(remaining-1))
        chosen=None
        for delimiter in ("\n\n","\n"):
            offset=body.find(delimiter,lo)
            best=10**15
            while offset>=0 and offset+len(delimiter)<=hi:
                pos=offset+len(delimiter)
                distance=abs(pos-target)
                if distance<best: chosen,best=pos,distance
                offset=body.find(delimiter,offset+1)
            if chosen is not None: break
        if chosen is None: chosen=target
        parts.append(body[start:chosen])
        start=chosen
    parts.append(body[start:])
    if "".join(parts)!=body or any(not p or len(p)>MAX for p in parts):
        raise ValueError("Segmentação não reversível")
    return parts

def build(source):
    pages=read_pages(source)
    manifest={"schema_version":"1.0","source":SOURCE,"source_git_blob_sha":blob_sha(source),
              "source_pdf_sha256":"c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675",
              "page_count":len(pages),"max_chunk_chars":MAX,"chunks":[]}
    files={}
    for page,body in pages:
        parts=split_page(body)
        offset=0
        for seq,part in enumerate(parts,1):
            ident=f"p{page:02d}-c{seq:02d}"
            path=f"{DIR}/{ident}.md"
            files[path]=(f"---\nchunk_id: {ident}\npage: {page}\nsegment: {seq}/{len(parts)}\n"
                         f"source: {SOURCE}\nchar_start: {offset}\nchar_end: {offset+len(part)}\n"
                         f"---\n\n# Edital UFMS 152/2026 — página {page}, parte {seq}/{len(parts)}\n\n"
                         f"{FENCE}text\n{part}\n{FENCE}\n")
            categories=["edital"]
            if page<=13: categories.append("regras_e_cronograma")
            if 14<=page<=18: categories.append("cargos_e_vagas")
            if 29<=page<=45: categories.append("conteudo_programatico")
            if page in (15,35,36): categories.append("cargo_523")
            if page in (18,45): categories.append("cargo_324")
            if page==29: categories.append("conhecimentos_gerais")
            manifest["chunks"].append({"id":ident,"path":path,"page":page,
                "segment":seq,"segments_on_page":len(parts),"char_start":offset,
                "char_end":offset+len(part),"characters":len(part),"categories":categories})
            offset+=len(part)
    return files,manifest

def validate(root=ROOT):
    text=(root/SOURCE).read_text(encoding="utf-8")
    expected,manifest=build(text)
    actual=json.loads((root/"edital/manifest.json").read_text(encoding="utf-8"))
    if actual!=manifest: raise ValueError("Manifest divergente")
    names={str(x.relative_to(root)) for x in (root/DIR).glob("*.md")}
    if names!=set(expected): raise ValueError("Chunks ausentes ou extras")
    for path,content in expected.items():
        if (root/path).read_text(encoding="utf-8")!=content:
            raise ValueError("Chunk divergente: "+path)
    if sum(c["characters"] for c in manifest["chunks"])!=sum(len(p) for _,p in read_pages(text)):
        raise ValueError("Omissão de caracteres")
    return len(expected)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true")
    g.add_argument("--check",action="store_true")
    args=parser.parse_args()
    if args.write:
        files,manifest=build((ROOT/SOURCE).read_text(encoding="utf-8"))
        (ROOT/DIR).mkdir(parents=True,exist_ok=True)
        for path,content in files.items(): (ROOT/path).write_text(content,encoding="utf-8")
        (ROOT/"edital/manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"OK: 47 páginas e {validate()} chunks fiéis")

if __name__=="__main__": main()
