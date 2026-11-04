"""Índice determinístico do Anexo IV (atribuições 523/324), sem semântica inventada."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from chunk_edital import SOURCE, blob_sha
from search_edital import load

ROOT = Path(__file__).resolve().parents[1]
SPECS = [
    {
        "cargo": "523",
        "page": 23,
        "chunk_id": "p23-c01",
        "heading": "Analista em Educação/Administração e Informação / Gestão Pública",
        "first_text": "Planejar, desenvolver, executar, acompanhar e avaliar atividades, programas, projetos e processos relacionados à gestão pública e à administração universitária.",
        "last_text": "ambiente organizacional.",
        "neighbor_exclusion": ["Produção Cultural", "(Campus)", "Endodontia"],
    },
    {
        "cargo": "324",
        "page": 28,
        "chunk_id": "p28-c02",
        "heading": "Técnico em Educação / Processos Educacionais / Assuntos Estudantis**",
        "first_text": "Executar atividades administrativas de apoio às secretarias acadêmicas,",
        "last_text": "natureza e nível de complexidade associadas ao ambiente organizacional.",
        "neighbor_exclusion": ["Veterinária e Zootecnia", "hospital veterinário", "Técnico em Tecnologia da Informação"],
    },
]

def locate(spec, chunk):
    if chunk["page"] != spec["page"] or chunk["id"] != spec["chunk_id"]:
        raise ValueError("Identificação de chunk/página divergente")
    body = chunk["body"]
    headings = list(re.finditer(r"(?m)^[ \t]*" + re.escape(spec["heading"]) + r"[ \t]*$", body))
    if len(headings) != 1:
        raise ValueError("Título ausente ou não único do cargo " + spec["cargo"])
    start = headings[0].start()
    expected_text = body.find(spec["first_text"], headings[0].end())
    if expected_text < 0 or expected_text - headings[0].end() > 12:
        raise ValueError("Atribuição não começa logo após o título: " + spec["cargo"])
    stop = body.find(spec["last_text"], expected_text)
    if stop < 0 or body.find(spec["last_text"], stop + 1) >= 0:
        raise ValueError("Final ausente ou ambíguo: " + spec["cargo"])
    end = stop + len(spec["last_text"])
    passage = body[start:end]
    if not 200 <= len(passage) <= 5000:
        raise ValueError("Comprimento do trecho inesperado: " + spec["cargo"])
    for forbidden in spec["neighbor_exclusion"]:
        if forbidden in passage:
            raise ValueError("Contaminação de cargo adjacente: " + spec["cargo"])
    trailing = body[end:].strip()
    if spec["cargo"] == "523" and trailing:
        raise ValueError("Texto não esperado após as atribuições 523")
    if spec["cargo"] == "324" and not re.fullmatch(
        r"Edital\s+6775306\s+SEI\s+23104\.030868/2026-19\s*/\s*pg\.\s*28",
        trailing):
        raise ValueError("Rodapé após as atribuições 324 diverge")
    return {
        "chunk_char_start": start,
        "chunk_char_end": end,
        "page_char_start": chunk["char_start"] + start,
        "page_char_end": chunk["char_start"] + end,
        "characters": len(passage),
        "literal_sha256": hashlib.sha256(passage.encode("utf-8")).hexdigest(),
        "text": passage,
    }

def build(root=ROOT):
    manifest = json.loads((root/"edital/manifest.json").read_text(encoding="utf-8"))
    source = (root/SOURCE).read_text(encoding="utf-8")
    if manifest["source"] != SOURCE or manifest["source_git_blob_sha"] != blob_sha(source):
        raise ValueError("Documento canônico diverge do manifest")
    by_id = {chunk["id"]: chunk for chunk in load(root)}
    records = []
    for spec in SPECS:
        if spec["chunk_id"] not in by_id:
            raise ValueError("Chunk de atribuição ausente")
        chunk = by_id[spec["chunk_id"]]
        span = locate(spec, chunk)
        records.append({
            "cargo": spec["cargo"],
            "page": spec["page"],
            "chunk_id": spec["chunk_id"],
            "path": chunk["path"],
            "heading": spec["heading"],
            "first_text": spec["first_text"],
            "last_text": spec["last_text"],
            "neighbor_exclusion": spec["neighbor_exclusion"],
            **{key: value for key, value in span.items() if key != "text"},
        })
    return {
        "schema_version": "1.0",
        "classification": "derived_non_normative",
        "annex": "IV",
        "source": SOURCE,
        "source_git_blob_sha": manifest["source_git_blob_sha"],
        "source_pdf_sha256": manifest["source_pdf_sha256"],
        "description": "Recortes literais das atribuições dos cargos 523 (p. 23) e 324 (p. 28). Metadados e hash de cada recorte derivados, sem alterar texto normativo.",
        "entries": records,
    }

def validate(root=ROOT):
    actual = json.loads((root/"edital/atribuicoes_index.json").read_text(encoding="utf-8"))
    expected = build(root)
    if actual != expected:
        raise ValueError("Índice de atribuições divergente da fonte")
    return len(expected["entries"])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        (ROOT/"edital/atribuicoes_index.json").write_text(
            json.dumps(build(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
    print(f"OK: {validate()} atribuições indexadas, com origem e limites íntegros")

if __name__ == "__main__":
    main()
