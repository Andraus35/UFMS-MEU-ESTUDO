"""Sonda HTTP de hash do PDF institucional; leitura apenas, sem mudança normativa.

Uso: python scripts/probe_pdf_ufms.py --live
Resultados: digest_match_unarchived (0), digest_mismatch (2), unverifiable (3).
Mesmo um hash igual NÃO substitui arquivo de evidência durável e auditoria externa.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT=Path(__file__).resolve().parents[1]
URL="https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf"
MAX_BYTES=12*1024*1024
CHUNK_SIZE=64*1024

class BlockExternalRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        # Proibir redirecionamentos, inclusive aos destinos com DNS diferente:
        # alterações do servidor precisam de revisão humana antes do fetch.
        raise ValueError("Redirecionamento de PDF não autorizado")

def probe(reader, expected_sha):
    """Compara bytes de um response stream, sem gravar arquivo nem confiar em headers."""
    if not isinstance(expected_sha,str) or not re.fullmatch(r"[0-9a-f]{64}",expected_sha):
        raise ValueError("SHA-256 esperado inválido")
    status=getattr(reader,"status",None)
    if status!=200:
        raise ValueError("HTTP status diferente de 200")
    headers=getattr(reader,"headers",{})
    content_type=str(headers.get("Content-Type","")).lower().split(";")[0].strip()
    if content_type not in ("application/pdf","application/octet-stream"):
        raise ValueError("Content-Type não indica PDF")
    declared=headers.get("Content-Length")
    if declared is not None:
        if not str(declared).isdigit() or int(declared)>MAX_BYTES:
            raise ValueError("Content-Length inválido ou acima do limite")
    digest=hashlib.sha256()
    size=0
    first=b""
    tail=b""
    while True:
        part=reader.read(CHUNK_SIZE)
        if not part:
            break
        if not isinstance(part,bytes):
            raise ValueError("Resposta HTTP não contém bytes")
        if not first:
            first=part[:8]
        size+=len(part)
        if size>MAX_BYTES:
            raise ValueError("PDF acima do limite de tamanho")
        digest.update(part)
        tail=(tail+part)[-2048:]
    if size<1024 or not first.startswith(b"%PDF-") or b"%%EOF" not in tail:
        raise ValueError("PDF incompleto ou assinatura inválida")
    observed=digest.hexdigest()
    return {"status":("digest_match_unarchived" if observed==expected_sha else "digest_mismatch"),
            "sha256_observed":observed,"sha256_expected":expected_sha,
            "bytes_read":size,"bytes_obtained":True,
            "verified_normative_revision":False,"archived_official_pdf":False}

def probe_live(root=ROOT,opener=None,timeout=12):
    manifest=json.loads((Path(root)/"edital/manifest.json").read_text(encoding="utf-8"))
    expected=manifest["source_pdf_sha256"]
    if not isinstance(expected,str) or not re.fullmatch(r"[0-9a-f]{64}",expected):
        raise ValueError("Manifest com SHA-256 inválido")
    result={"url":URL,"observation_utc":datetime.now(timezone.utc).isoformat(),
            "scope":"institutional_pdf_bytes_single_attempt",
            "verified_normative_revision":False,"archived_official_pdf":False}
    if urlparse(URL).scheme!="https" or urlparse(URL).hostname!="www.ufms.br":
        raise ValueError("URL institucional não permitida")
    opener=opener or build_opener(BlockExternalRedirect())
    try:
        req=Request(URL,headers={"User-Agent":"UFMS-MEU-ESTUDO-auditoria-documental/1.0"})
        with opener.open(req,timeout=timeout) as response:
            final_url=response.geturl()
            if final_url!=URL:
                raise ValueError("Resposta redirecionada fora da URL esperada")
            result.update(probe(response,expected))
    except (HTTPError,URLError,OSError,UnicodeError,ValueError,TimeoutError) as exc:
        result.update({"status":"unverifiable","reason":"Consulta indisponível ou inconclusiva: "+type(exc).__name__,
                       "sha256_observed":None,"sha256_expected":expected,"bytes_obtained":False})
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live",action="store_true",required=True)
    args=parser.parse_args()
    result=probe_live()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return {"digest_match_unarchived":0,"digest_mismatch":2,"unverifiable":3}[result["status"]]

if __name__=="__main__":
    sys.exit(main())
