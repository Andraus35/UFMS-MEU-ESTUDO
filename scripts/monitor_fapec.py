"""Verificação somente leitura do portal FAPEC; não interpreta atos nem atualiza o edital.

Use --live para consulta externa (pode retornar inconclusivo), ou --fixture
para diagnóstico offline. Nenhuma execução escreve em arquivos.
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from validate_fontes_oficiais import ROOT, REGISTRY, FAPEC_URL

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip=0
        self.fragments=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower() in ("script","style","noscript"):
            self.skip+=1
    def handle_endtag(self,tag):
        if tag.lower() in ("script","style","noscript") and self.skip:
            self.skip-=1
    def handle_data(self,data):
        if not self.skip and data.strip():
            self.fragments.append(data.strip())

def normalize(text):
    text="".join(c for c in unicodedata.normalize("NFKD",text.casefold())
                 if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+",text))

def assess_portal_html(html,registry):
    visible=VisibleText()
    visible.feed(html)
    normalized=normalize(" ".join(visible.fragments))
    expected=normalize(registry["publication_observations"][0]["listing_label"])
    contest=normalize("CONCURSO PÚBLICO PARA INGRESSO NA CARREIRA DE TÉCNICO-ADMINISTRATIVOS EM EDUCAÇÃO DA FUNDAÇÃO UNIVERSIDADE FEDERAL DE MATO GROSSO DO SUL")
    if not normalized or contest not in normalized:
        return {"status":"unverifiable","reason":"Página não confirma a identidade do concurso","publication_candidate":False}
    if expected not in normalized:
        return {"status":"needs_manual_review","reason":"A publicação inicial não coincide com o registro de origem","publication_candidate":True}
    # Marcas só apontam candidatas a conferir, nunca confirmam retificações.
    words=set(normalized.split())
    marker_words={"retificacao","retificacoes","retifica","retificado","errata",
                  "corrigido","correcao","comunicado","esclarecimento"}
    candidates=sorted(words.intersection(marker_words))
    download_count=len(re.findall(r"\bDOWNLOAD\b"," ".join(visible.fragments),re.I))
    expected_downloads=registry["publication_observations"][0]["listing_count_observed"]
    if candidates or download_count!=expected_downloads:
        return {"status":"needs_manual_review",
                "reason":"Possível mudança nas publicações do concurso no portal",
                "publication_candidate":True,
                "marker_words":candidates,
                "download_links_text_count":download_count}
    return {"status":"no_change_observed_on_single_page",
            "reason":"A listagem observada não apresenta alteração detectável; outras fontes não foram cobertas",
            "publication_candidate":False,
            "download_links_text_count":download_count}

def check_live(registry,timeout=12):
    request=Request(FAPEC_URL,headers={
        "User-Agent":"UFMS-MEU-ESTUDO/1.0 (+monitoramento somente leitura)"
    })
    try:
        with urlopen(request,timeout=timeout) as response:
            content_type=response.headers.get("Content-Type","")
            if response.status!=200 or "text/html" not in content_type:
                raise ValueError("Resposta HTTP não é página HTML da FAPEC")
            content=response.read(1024*1024+1)
            if len(content)>1024*1024:
                raise ValueError("Resposta excede limite de 1 MiB")
            text=content.decode("utf-8",errors="strict")
    except (OSError,HTTPError,URLError,ValueError,UnicodeError) as err:
        return {"status":"unverifiable","publication_candidate":False,
                "reason":"Falha de acesso ou validação do portal: "+type(err).__name__}
    return assess_portal_html(text,registry)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--live",action="store_true")
    g.add_argument("--fixture",type=Path)
    args=parser.parse_args()
    registry=json.loads((ROOT/REGISTRY).read_text(encoding="utf-8"))
    if args.live:
        result=check_live(registry)
    else:
        result=assess_portal_html(args.fixture.read_text(encoding="utf-8"),registry)
    result.update({"checked_url":FAPEC_URL,
                   "observation_utc":datetime.now(timezone.utc).isoformat(),
                   "scope":"single_fapec_contest_page_only",
                   "writes":False,"normative_revision_verified":False})
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if result["status"]=="no_change_observed_on_single_page":
        return 0
    if result["status"]=="needs_manual_review":
        return 2
    return 3

if __name__=="__main__":
    sys.exit(main())
