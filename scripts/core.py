"""Rotinas puras para validar e reconstruir evidências de aprendizagem.

Sem acesso de rede e sem dependências externas. Não infere conhecimento por tópico
quando o relatório só fornece métricas agregadas.
"""
import csv
import json
from datetime import datetime

from gp1_ingestion import ATTEMPT_TYPES, validate_attempt_events, rebuild_attempts
from evidence_projection import derive_evidence_level
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_TYPES = {
    "caderno_recomendado", "resultado_recebido", "resultado_corrigido",
    "revisao_agendada", "revisao_concluida", "decisao",
    "attempt_recorded", "attempt_corrected",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def topic_rows(root=ROOT):
    with (root / "config/topics.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def event_rows(root=ROOT):
    events = []
    for path in sorted((root / "state/events").glob("*.jsonl")):
        for line_number, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not text.strip():
                continue
            try:
                event = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSONL inválido {path.name}:{line_number}: {exc}") from exc
            if not isinstance(event, dict):
                raise ValueError(f"Evento não é objeto {path.name}:{line_number}")
            events.append(event)
    return events


def iso_date(value, label):
    if not isinstance(value, str):
        raise ValueError(f"{label} deve ser string ISO 8601")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} inválido: {value}") from exc
    if parsed.utcoffset() is None:
        raise ValueError(f"{label} precisa informar fuso horário")
    return parsed


def count_integer(value, label):
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} deve ser inteiro não negativo")
    return value


def validate_events(events, topics, allow_private=False):
    if any(isinstance(event, dict) and event.get("type") in ATTEMPT_TYPES for event in events):
        legacy = [event for event in events if event.get("type") not in ATTEMPT_TYPES]
        if legacy:
            validate_events(legacy, topics, allow_private=allow_private)
        return validate_attempt_events(events, topics, allow_private=allow_private)
    ids = {row["topic_id"] for row in topics}
    seen = {}
    results = {}
    recommendations = set()
    recommendation_topics = {}
    for event in events:
        eid = event.get("event_id")
        kind = event.get("type")
        if not isinstance(eid, str) or not eid.strip() or eid in seen:
            raise ValueError(f"event_id ausente ou duplicado: {eid}")
        if kind not in VALID_TYPES:
            raise ValueError(f"Tipo de evento inválido: {kind}")
        iso_date(event.get("timestamp"), f"timestamp {eid}")
        if not allow_private and kind in {"resultado_recebido", "resultado_corrigido"}:
            raise ValueError("Resultados individuais bloqueados até confirmar repositório privado")
        selected = event.get("topic_ids", [])
        if not isinstance(selected, list) or len(set(selected)) != len(selected):
            raise ValueError(f"topic_ids inválidos em {eid}")
        if any(t not in ids for t in selected):
            raise ValueError(f"Tópico não cadastrado em {eid}")
        cid = event.get("caderno_id")
        if kind in {"caderno_recomendado", "resultado_recebido", "resultado_corrigido"}:
            if not isinstance(cid, str) or not cid.strip():
                raise ValueError(f"caderno_id ausente em {eid}")
        if kind == "caderno_recomendado":
            if cid in recommendations:
                raise ValueError(f"Caderno recomendado duas vezes: {cid}")
            recommendations.add(cid)
            recommendation_topics[cid] = set(selected)
        if kind in {"resultado_recebido", "resultado_corrigido"}:
            total = count_integer(event.get("total"), f"total {eid}")
            correct = count_integer(event.get("acertos"), f"acertos {eid}")
            errors = count_integer(event.get("erros"), f"erros {eid}")
            unanswered = count_integer(event.get("nao_respondidas", 0), f"não respondidas {eid}")
            if correct + errors + unanswered != total:
                raise ValueError(f"Totais inconsistentes em {eid}")
            breakdown = event.get("topic_results", [])
            if not isinstance(breakdown, list):
                raise ValueError(f"topic_results inválido em {eid}")
            assigned = set()
            summed = 0
            summed_correct = 0
            summed_errors = 0
            for entry in breakdown:
                if not isinstance(entry, dict):
                    raise ValueError(f"Entrada topic_results inválida em {eid}")
                topic_id = entry.get("topic_id")
                if topic_id not in ids or topic_id in assigned:
                    raise ValueError(f"Tópico inválido/repetido em topic_results de {eid}")
                assigned.add(topic_id)
                attempted = count_integer(entry.get("attempted"), "attempted")
                topic_correct = count_integer(entry.get("correct"), "correct")
                if topic_correct > attempted:
                    raise ValueError(f"Mais acertos que tentativas em {eid}")
                summed += attempted
                summed_correct += topic_correct
                summed_errors += attempted - topic_correct
            if summed > correct + errors:
                raise ValueError(f"Soma de tentativas por tópico supera questões respondidas em {eid}")
            if summed_correct > correct:
                raise ValueError(f"Acertos por tópico superam acertos totais em {eid}")
            if summed_errors > errors:
                raise ValueError(f"Erros por tópico superam erros totais em {eid}")
            # Quando o caderno tem recomendação registrada, não aceitar tópicos
            # estranhos ao escopo recomendado. Resultados sem recomendação prévia
            # seguem permitidos, mas não ganham escopo inferido automaticamente.
            if cid in recommendation_topics:
                authorized = recommendation_topics[cid]
                if not assigned.issubset(authorized) or (selected and not set(selected).issubset(authorized)):
                    raise ValueError(f"Tópico fora da recomendação do caderno {cid}")
            if kind == "resultado_recebido":
                if cid in results:
                    raise ValueError(f"Resultado duplicado para caderno {cid}; use correção")
            else:
                previous_id = event.get("corrects_event_id")
                if cid not in results or previous_id != results[cid]:
                    raise ValueError(f"Correção sem vínculo com último resultado de {cid}")
            results[cid] = eid
        if kind in {"revisao_agendada", "revisao_concluida"}:
            if event.get("topic_id") not in ids:
                raise ValueError(f"Tópico de revisão desconhecido em {eid}")
            if kind == "revisao_agendada":
                iso_date(event.get("due_at"), f"due_at {eid}")
        seen[eid] = event
    return True


def rebuild(events, topics, schema_version="0.2.0"):
    if any(event.get("type") in ATTEMPT_TYPES for event in events):
        legacy = [event for event in events if event.get("type") not in ATTEMPT_TYPES]
        state, rows = rebuild(legacy, topics, schema_version=schema_version)
        attempts = rebuild_attempts(events, topics)
        for row in rows:
            extra = attempts["progress"][row["topic_id"]]
            row["attempted"] += extra["attempted"]
            row["correct"] += extra["correct"]
            row["accuracy"] = (f'{row["correct"]/row["attempted"]:.4f}' if row["attempted"] else "")
        state["event_count"] = len(events)
        state["event_cursor"] = events[-1]["event_id"] if events else None
        last = events[-1] if events else {}
        state["last_event_at"] = last.get("timestamp", last.get("recorded_at"))
        state["results_count"] += attempts["attempts_count"]
        state["last_attempt_id"] = attempts["last_attempt_id"]
        completed = set(attempts["recommendation_ids"])
        completed_cadernos = {
            event.get("caderno_id") for event in legacy
            if event.get("type") == "caderno_recomendado"
            and event.get("recommendation_id") in completed
        }
        state["pending_cadernos"] = [
            cid for cid in state["pending_cadernos"] if cid not in completed_cadernos
        ]
        evidence = derive_evidence_level(events)
        state["evidence_schema_version"] = "1.0"
        state["evidence_level"] = evidence["level"]
        state["evidence_dimensions"] = evidence["dimensions"]
        state["evidence_uncertainties"] = evidence["uncertainties"]
        state["knowledge_status"] = evidence["knowledge_status"]
        return state, rows
    progress = {row["topic_id"]: {"attempted": 0, "correct": 0, "revision_due_at": ""} for row in topics}
    recommended = {}
    results = {}
    reviews = {}
    last_result = None
    for event in events:
        kind = event["type"]
        cid = event.get("caderno_id")
        if kind == "caderno_recomendado":
            recommended[cid] = event
        elif kind in {"resultado_recebido", "resultado_corrigido"}:
            results[cid] = event  # Correção substitui o resultado agregado anterior.
            recommended.pop(cid, None)
            last_result = cid
        elif kind == "revisao_agendada":
            reviews[event["topic_id"]] = event["due_at"]
        elif kind == "revisao_concluida":
            reviews.pop(event["topic_id"], None)
    for result in results.values():
        # Somente valores desagregados fornecidos, nunca projeção por assunto.
        for entry in result.get("topic_results", []):
            p = progress[entry["topic_id"]]
            p["attempted"] += entry["attempted"]
            p["correct"] += entry["correct"]
    for topic_id, due_at in reviews.items():
        progress[topic_id]["revision_due_at"] = due_at
    current = {
        "schema_version": schema_version,
        "event_count": len(events),
        "event_cursor": events[-1]["event_id"] if events else None,
        "last_event_at": events[-1]["timestamp"] if events else None,
        "last_result_caderno_id": last_result,
        "results_count": len(results),
        "pending_cadernos": list(recommended)[-10:],
        "pending_reviews": reviews,
        "knowledge_status": "unknown_until_evidence",
    }
    evidence = derive_evidence_level(events)
    current["evidence_schema_version"] = "1.0"
    current["evidence_level"] = evidence["level"]
    current["evidence_dimensions"] = evidence["dimensions"]
    current["evidence_uncertainties"] = evidence["uncertainties"]
    current["knowledge_status"] = evidence["knowledge_status"]
    rows = []
    for topic in topics:
        tid = topic["topic_id"]
        p = progress[tid]
        accuracy = f'{p["correct"]/p["attempted"]:.4f}' if p["attempted"] else ""
        rows.append({"topic_id": tid, "attempted": p["attempted"], "correct": p["correct"], "accuracy": accuracy, "revision_due_at": p["revision_due_at"]})
    return current, rows
