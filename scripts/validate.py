"""Validação determinística mínima do harness; não escreve arquivos."""
import csv
import json
import sys
from pathlib import Path

try:
    from core import ROOT, event_rows, load_json, rebuild, topic_rows, validate_events
except ModuleNotFoundError:
    from scripts.core import ROOT, event_rows, load_json, rebuild, topic_rows, validate_events


def validate(root=ROOT):
    settings = load_json(root / "settings.json")
    for filename in settings["bootstrap"]["mandatory"]:
        path = root / filename
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            raise ValueError(f"Arquivo obrigatório ausente ou vazio: {filename}")
    data = load_json(root / "config/concursos.json")
    if sorted(c["codigo"] for c in data["cargos"]) != ["324", "523"]:
        raise ValueError("Cargos configurados não correspondem a 324 e 523")
    if sum(x["questions"] for x in data["areas"]) != 60 or sum(x["points"] for x in data["areas"]) != 100:
        raise ValueError("Pesos/questões inconsistentes com edital")
    topics = topic_rows(root)
    if len(topics) != 23 or len({t["topic_id"] for t in topics}) != 23:
        raise ValueError("Mapa inicial deveria conter quatro gerais, dez tópicos 523 e nove tópicos 324")
    if sum(t["area"] == "gerais" for t in topics) != 4:
        raise ValueError("São necessárias quatro matérias gerais")
    for t in topics:
        if t["cargo_ids"] not in ("523|324", "523", "324"):
            raise ValueError(f"Cargo inválido no tópico {t['topic_id']}")
    events = event_rows(root)
    validate_events(events, topics, allow_private=settings["storage"].get("personal_results_writes_enabled", False))
    current, rows = rebuild(events, topics, settings["schema_version"])
    if load_json(root / "state/CURRENT.json") != current:
        raise ValueError("CURRENT.json divergente do histórico; usar rebuild.py --write e revisar mudanças")
    with (root / "state/PROGRESS.csv").open(encoding="utf-8", newline="") as f:
        actual_rows = list(csv.DictReader(f))
    expected_rows = [{k: str(v) for k, v in row.items()} for row in rows]
    if actual_rows != expected_rows:
        raise ValueError("PROGRESS.csv divergente do histórico; usar rebuild.py --write")
    try:
        from chunk_edital import validate as check_edital
    except ModuleNotFoundError:
        from scripts.chunk_edital import validate as check_edital
    chunks = check_edital(root)
    try:
        from index_edital import validate as check_topic_index
    except ModuleNotFoundError:
        from scripts.index_edital import validate as check_topic_index
    indexed = check_topic_index(root)
    return f"OK: {len(topics)} blocos; {len(events)} eventos; {current['results_count']} cadernos concluídos; {chunks} chunks verificados; {indexed} tópicos indexados"


if __name__ == "__main__":
    try:
        print(validate())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(f"FALHA: {exc}", file=sys.stderr)
        sys.exit(1)
