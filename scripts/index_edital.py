"""Índice leve derivado dos títulos oficiais; nunca altera texto canônico."""
import argparse
import csv
import json
import re
from pathlib import Path

from chunk_edital import SOURCE, blob_sha
from search_edital import load

ROOT = Path(__file__).resolve().parents[1]
SCOPES = {
    "gerais": ("p29-c01",),
    "523": ("p35-c02", "p36-c01"),
    "324": ("p45-c02",),
}
GENERAL = {
    "GER-PORT": "LÍNGUA PORTUGUESA",
    "GER-ING": "LÍNGUA INGLESA",
    "GER-LEG": "LEGISLAÇÃO",
    "GER-RLM": "RACIOCÍNIO LÓGICO",
}
# Apenas atalhos de busca derivados: não são conteúdo normativo nem fatos do edital.
ALIASES = {
    "GER-PORT": ["gramatica", "interpretacao de texto", "redacao oficial"],
    "GER-ING": ["ingles", "compreensao em ingles"],
    "GER-LEG": ["normas ufms", "regime juridico servidor", "lei 8112"],
    "GER-RLM": ["logica", "matematica", "proposicoes logicas"],
    "523-01": ["organizacao administrativa", "administracao indireta"],
    "523-02": ["politicas publicas", "governanca publica", "analise swot"],
    "523-03": ["gestao de processos", "pdca", "5w2h"],
    "523-04": ["autonomia universitaria", "ldb ensino superior"],
    "523-05": ["gestao por competencias", "clima organizacional"],
    "523-06": ["financas publicas", "ppa", "ldo", "loa", "orcamento publico"],
    "523-07": ["almoxarifado", "estoque de seguranca"],
    "523-08": ["compras publicas", "contratacoes publicas", "licitacao"],
    "523-09": ["governo digital", "lgpd", "gestao documental"],
    "523-10": ["direitos do usuario", "servico publico atendimento"],
    "324-01": ["ldb educacao superior", "funcionamento universidade"],
    "324-02": ["rotinas academicas graduacao", "regulamento graduacao"],
    "324-03": ["calouro", "ingresso na graduacao", "documentos matricula"],
    "324-04": ["mestrado e doutorado", "pos graduacao stricto sensu"],
    "324-05": ["correspondencia oficial", "documentos oficiais"],
    "324-06": ["disciplina discente", "comportamento estudantil", "regulamento de conduta"],
    "324-07": ["rotina administrativa", "organizacao do trabalho"],
    "324-08": ["comunicacao interpessoal", "atendimento estudantes"],
    "324-09": ["controle de estoque", "patrimonio publico"],
}
DESCRIPTION = (
    "Índice derivado dos 23 blocos de config/topics.csv; offsets são intervalos "
    "exatos dentro de chunks, não alterações no edital."
)

def build(root=ROOT):
    manifest = json.loads((root / "edital/manifest.json").read_text(encoding="utf-8"))
    canonical = (root / SOURCE).read_text(encoding="utf-8")
    if manifest["source"] != SOURCE or manifest["source_git_blob_sha"] != blob_sha(canonical):
        raise ValueError("Fonte canônica diverge do manifesto")
    chunks = {c["id"]: c for c in load(root)}
    with (root / "config/topics.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    all_topics = {}
    for scope, ids in SCOPES.items():
        positions = []
        cursor = 0
        for ident in ids:
            chunk = chunks[ident]
            positions.append((ident, cursor, cursor + len(chunk["body"])))
            cursor += len(chunk["body"]) + 1
        source = "\n".join(chunks[ident]["body"] for ident in ids)
        if scope == "gerais":
            bounds = (source.find("1. CONHECIMENTOS GERAIS"),
                      source.find("2. CONHECIMENTOS ESPECÍFICOS"))
        elif scope == "523":
            bounds = (source.find("GESTÃO PÚBLICA (CÓDIGO 523)"),
                      source.find("GESTÃO PÚBLICA (CAMPUS)"))
        else:
            bounds = (source.find("ASSUNTOS ESTUDANTIS (CÓDIGOS 324 A 330)"),
                      len(source))
        if bounds[0] < 0 or bounds[1] <= bounds[0]:
            raise ValueError("Limites do programa não encontrados: " + scope)
        relevant = [row for row in rows if
                    (row["area"] == "gerais" if scope == "gerais"
                     else row["topic_id"].startswith(scope + "-"))]
        found = []
        for row in relevant:
            if scope == "gerais":
                expression = r"^\s*" + re.escape(GENERAL[row["topic_id"]]) + r"\s*$"
                pattern = re.compile(expression, re.M)
            else:
                pattern = re.compile(r"\b" + str(int(row["bloco"])) + r"\.\s+" +
                                     re.escape(row["titulo"].split()[0]))
            matches = [x for x in pattern.finditer(source)
                       if bounds[0] <= x.start() < bounds[1]]
            if len(matches) != 1:
                raise ValueError("Marcador não único: " + row["topic_id"])
            found.append((matches[0].start(), row))
        found.sort(key=lambda x: x[0])
        for i, (start, row) in enumerate(found):
            end = found[i + 1][0] if i + 1 < len(found) else bounds[1]
            locations = []
            for ident, base, finish in positions:
                a, b = max(start, base), min(end, finish)
                if a >= b:
                    continue
                meta = chunks[ident]
                local_start, local_end = a - base, b - base
                locations.append({
                    "chunk_id": ident, "path": meta["path"], "page": meta["page"],
                    "chunk_char_start": local_start, "chunk_char_end": local_end,
                    "page_char_start": meta["char_start"] + local_start,
                    "page_char_end": meta["char_start"] + local_end,
                })
            if not locations:
                raise ValueError("Tópico sem trecho: " + row["topic_id"])
            ident = row["topic_id"]
            all_topics[ident] = {
                "topic_id": ident, "title": row["titulo"], "area": row["area"],
                "cargo_ids": row["cargo_ids"].split("|"),
                "aliases": ALIASES[ident],
                "locations": locations,
            }
    if len(rows) != 23 or set(all_topics) != set(ALIASES):
        raise ValueError("Mapa de 23 tópicos incompleto ou incompatível")
    return {
        "schema_version": "1.0", "classification": "derived_non_normative",
        "source": manifest["source"],
        "source_git_blob_sha": manifest["source_git_blob_sha"],
        "source_pdf_sha256": manifest["source_pdf_sha256"],
        "description": DESCRIPTION,
        "topics": [all_topics[row["topic_id"]] for row in rows],
    }

def validate(root=ROOT):
    expected = build(root)
    actual = json.loads((root / "edital/topic_index.json").read_text(encoding="utf-8"))
    if actual != expected:
        raise ValueError("Índice de tópicos desatualizado, alterado ou incompatível")
    return len(actual["topics"])

def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = p.parse_args()
    if args.write:
        (ROOT / "edital/topic_index.json").write_text(
            json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OK: " + str(validate()) + " tópicos indexados e íntegros")

if __name__ == "__main__":
    main()
