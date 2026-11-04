"""Gate OFFLINE para proveniência e anomalia do cronograma do edital UFMS.

Nunca baixa documentos, deduz datas corretas nem incorpora retificações.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from chunk_edital import SOURCE, blob_sha, read_pages

ROOT=Path(__file__).resolve().parents[1]
REGISTRY="edital/fontes_oficiais.json"
FAPEC_URL="https://portal.concurso.fundacaofapec.org.br/edital/ver/22"
UFMS_PDF_URL="https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf"
UFMS_NEWS_URL="https://www.ufms.br/ufms-lanca-154-vagas-em-concurso-de-tecnicos-em-educacao-para-fortalecer-a-educacao-superior-em-ms/"

def _date(value):
    return datetime.strptime(value,"%d/%m/%Y").date()

def _official_url(url):
    parsed=urlparse(url)
    return parsed.scheme=="https" and parsed.hostname in (
        "portal.concurso.fundacaofapec.org.br",
        "concurso.fundacaofapec.org.br",
        "boletimoficial.ufms.br",
        "www.ufms.br",
        "progep.ufms.br"
    ) and not parsed.username and not parsed.password

def validate(root=ROOT):
    data=json.loads((root/REGISTRY).read_text(encoding="utf-8"))
    manifest=json.loads((root/"edital/manifest.json").read_text(encoding="utf-8"))
    source=(root/SOURCE).read_text(encoding="utf-8")
    if data["schema_version"]!="1.0":
        raise ValueError("Versão de esquema não suportada")
    orig=data["canonical"]
    if orig["document"]!=SOURCE or orig["source_git_blob_sha"]!=manifest["source_git_blob_sha"]:
        raise ValueError("Identidade Git do edital original divergente")
    if orig["original_pdf_sha256"]!=manifest["source_pdf_sha256"]:
        raise ValueError("SHA-256 original do PDF divergente")
    if blob_sha(source)!=orig["source_git_blob_sha"]:
        raise ValueError("Fonte canônica modificada sem versionamento")
    if orig["pdf_pages"]!=47 or manifest["page_count"]!=47:
        raise ValueError("Paginação divergente")
    if orig["status"]!="original_user_provided_hash_verified" or orig["scope"]!="não incorpora retificações":
        raise ValueError("Fonte original apresentada como versão corrigida")
    if data["amendment_policy"]["auto_apply"] is not False:
        raise ValueError("Importação automática de retificação não permitida")
    observations=data["publication_observations"]
    if not observations:
        raise ValueError("Falta observação de fonte externa")
    for obs in observations:
        if obs["page_url"]!=FAPEC_URL or not _official_url(obs["page_url"]):
            raise ValueError("Origem de observação do portal inválida")
        # Um SHA copiado ao JSON nao comprova os bytes hospedados na origem.
        # Sem arquivo remoto arquivado e hash recalculado, falhar fechado.
        if (obs["remote_pdf_equivalence"]!="unverified" or
            obs["download_bytes_sha256"] is not None or
            obs["status"]!="observed_listing_not_remote_pdf_hash_verified"):
            raise ValueError("Equivalência remota sem prova independente dos bytes oficiais")
        if obs["verified_amendment_found"] is True and not data["verified_amendments"]:
            raise ValueError("Retificação declarada sem evidência verificada")
    if not data["open_alerts"]:
        raise ValueError("Alerta cronológico removido sem resolução")
    alerts=[a for a in data["open_alerts"] if a["id"]=="ALERTA-DOC-01"]
    if len(alerts)!=1:
        raise ValueError("ALERTA-DOC-01 ausente ou duplicado")
    a=alerts[0]
    if a["annex"]!="II" or a["page"]!=13:
        raise ValueError("Localização do alerta incorreta")
    bodies=dict(read_pages(source))
    page=bodies[13]
    start=page.find(a["result_label_anchor"])
    after=page.find(a["appeal_label_anchor"],start)
    if start<0 or after<=start:
        raise ValueError("Marcadores do cronograma ausentes ou fora de ordem")
    window1=page[start:after]
    window2=page[after:after+350]
    if a["result_date_text"] not in window1:
        raise ValueError("Data de resultado não corresponde ao edital")
    if a["appeal_date_text"] not in window2:
        raise ValueError("Data de recurso não corresponde ao edital")
    result_date=_date(a["result_date_text"])
    first, second=re.fullmatch(r"(\d{2}) e (\d{2}/\d{2}/\d{4})",
                               a["appeal_date_text"]).groups()
    appeal_start=_date(first+"/"+second[3:])
    appeal_end=_date(second)
    if not (appeal_start<=appeal_end<result_date):
        raise ValueError("Inconsistência cronológica não reproduzida")
    if a["status"]=="resolved":
        if not any(x["document_id"]==a["resolution_document_id"]
                   for x in data["verified_amendments"]):
            raise ValueError("Alerta encerrado sem retificação verificada")
    elif a["status"]!="unresolved_source_inconsistency" or a["resolution_document_id"] is not None:
        raise ValueError("Alerta indevidamente alterado")
    # Segunda localização institucional: conteúdo da p. 13 cotejado,
    # mas a cópia PDF remota não teve seus bytes obtidos para hashing.
    institutional=data.get("institutional_pdf_observations")
    if not isinstance(institutional,list) or len(institutional)!=1:
        raise ValueError("Referência institucional UFMS ausente ou não única")
    doc=institutional[0]
    if (doc.get("pdf_url")!=UFMS_PDF_URL or
        doc.get("announcement_url")!=UFMS_NEWS_URL or
        not _official_url(doc["pdf_url"]) or
        not _official_url(doc["announcement_url"])):
        raise ValueError("URL institucional UFMS divergente")
    if (doc.get("document_identifier_visible")!=
            "EDITAL PROGEP/UFMS Nº 152, DE 29 DE OUTUBRO DE 2026" or
        doc.get("sei_process_visible")!="23104.030868/2026-19" or
        doc.get("pdf_page_count_observed")!=orig["pdf_pages"]):
        raise ValueError("Identidade visual UFMS divergente")
    if (doc.get("annex_ii_page")!=a["page"] or
        doc.get("result_date_visible")!=a["result_date_text"] or
        doc.get("appeal_date_visible")!=a["appeal_date_text"]):
        raise ValueError("Datas institucionais UFMS não correspondem ao alerta")
    if (doc.get("remote_pdf_equivalence")!="unverified" or
        doc.get("pdf_bytes_sha256") is not None or
        doc.get("status")!="institutional_pdf_selected_content_observed_hash_unverified"):
        raise ValueError("Equivalência institucional indevida sem bytes oficiais")
    for item in data["verified_amendments"]:
        required=("document_id","official_issuer","official_publication_url",
                  "published_on","title","sha256_verified_bytes",
                  "repository_relative_path","target_original_or_previous_version",
                  "affected_items","human_review_before_normative_adoption")
        if any(not item.get(key) for key in required):
            raise ValueError("Retificação sem evidência obrigatória")
        if not _official_url(item["official_publication_url"]):
            raise ValueError("URL de retificação não pertence a fonte permitida")
        path=item["repository_relative_path"]
        if not isinstance(path,str) or not re.fullmatch(
                r"edital/retificacoes/[a-zA-Z0-9_.-]+\.pdf",path):
            raise ValueError("Caminho de retificação não é autorizado")
        file=(root/path)
        if not file.is_file():
            raise ValueError("PDF de retificação ausente: "+path)
        if hashlib.sha256(file.read_bytes()).hexdigest()!=item["sha256_verified_bytes"]:
            raise ValueError("SHA-256 de retificação divergente")
        datetime.strptime(item["published_on"],"%Y-%m-%d")
        if item["human_review_before_normative_adoption"] is not True:
            raise ValueError("Retificação sem revisão humana obrigatória")
    if data["last_check"]["exhaustive"] is not False:
        raise ValueError("Cobertura externa classificada indevidamente como exaustiva")
    if not data["last_check"]["status"]=="partial_website_check":
        raise ValueError("Status de verificação externa não suportado")
    return len(observations),len(data["verified_amendments"]),len(alerts)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check",action="store_true",required=True)
    a=p.parse_args()
    seen,ret,alerts=validate()
    print(f"OK: {seen} observação oficial parcial; {ret} retificações comprovadas; "
          f"{alerts} alerta cronológico preservado; equivalência remota não presumida")

if __name__=="__main__":
    main()
