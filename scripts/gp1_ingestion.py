"""Versioned GP-1 ingestion adapter; pure, offline and synthetic-testable.

This module does not persist events, authenticate platforms or authorize personal writes.
"""
from datetime import datetime

ATTEMPT_TYPES = {"attempt_recorded", "attempt_corrected"}
ANSWERED_CONVENTIONS = {
    "answered_excludes_unanswered",
    "answered_includes_unanswered",
}


def _date(value, label):
    if not isinstance(value, str):
        raise ValueError(label + " deve ser string ISO 8601")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(label + " inválido") from exc
    if parsed.utcoffset() is None:
        raise ValueError(label + " precisa informar fuso horário")
    return parsed


def _count(value, label):
    if type(value) is not int or value < 0:
        raise ValueError(label + " deve ser inteiro não negativo")
    return value


def normalize_external_report(report, answered_convention=None):
    """Normalize only when the column convention is explicitly supplied.

    The convention is a trusted caller decision, never read from the report itself.
    No identifiers are generated and no event is persisted.
    """
    if not isinstance(report, dict):
        raise ValueError("Relatório externo inválido")
    if answered_convention not in ANSWERED_CONVENTIONS:
        return {
            "decision": "pending_clarification",
            "canonical_event_created": False,
            "reason": "Semântica de respondidas não confirmada",
        }
    answered_reported = _count(report.get("reported_answered"), "reported_answered")
    unanswered = _count(report.get("reported_unanswered"), "reported_unanswered")
    correct = _count(report.get("correct"), "correct")
    incorrect = _count(report.get("incorrect"), "incorrect")
    if answered_convention == "answered_excludes_unanswered":
        answered = answered_reported
        total = answered + unanswered
    else:
        total = answered_reported
        if unanswered > total:
            raise ValueError("Não respondidas supera total informado")
        answered = total - unanswered
    if correct + incorrect != answered:
        raise ValueError("Corretas e incorretas não correspondem às respondidas")
    required = ("event_id", "attempt_id", "recommendation_id", "recorded_at")
    if any(not isinstance(report.get(k), str) or not report[k].strip() for k in required):
        raise ValueError("Identidades e recorded_at devem ser fornecidos, não gerados")
    recorded = _date(report["recorded_at"], "recorded_at")
    attempt_at = report.get("attempt_at")
    if attempt_at is not None:
        if not isinstance(attempt_at, str) or not attempt_at.strip():
            raise ValueError("attempt_at deve ser data ISO ou null")
        if _date(attempt_at, "attempt_at") > recorded:
            raise ValueError("attempt_at posterior a recorded_at")
    platform_id = report.get("platform_notebook_id")
    if platform_id is not None and (not isinstance(platform_id, str) or not platform_id.strip()):
        raise ValueError("platform_notebook_id deve ser string não vazia ou null")
    event = {
        "event_id": report["event_id"],
        "type": "attempt_recorded",
        "attempt_id": report["attempt_id"],
        "recommendation_id": report["recommendation_id"],
        "platform_notebook_id": platform_id,
        "recorded_at": report["recorded_at"],
        "attempt_at": attempt_at,
        "total": total,
        "acertos": correct,
        "erros": incorrect,
        "nao_respondidas": unanswered,
        "topic_results": report.get("topic_results", []),
    }
    return {
        "decision": "normalized",
        "canonical_event_created": True,
        "event": event,
        "normalization": {
            "answered_convention": answered_convention,
            "reported_answered": answered_reported,
            "answered": answered,
            "unanswered": unanswered,
            "total": total,
        },
    }


def validate_attempt_events(events, topics, allow_private=False):
    """Validate the additive attempt schema while preserving legacy events."""
    topic_ids = {row["topic_id"] for row in topics}
    seen_event_ids = set()
    recommendation_ids = set()
    latest_by_attempt = {}
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Evento deve ser objeto")
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id.strip() or event_id in seen_event_ids:
            raise ValueError("event_id ausente ou duplicado")
        seen_event_ids.add(event_id)
        kind = event.get("type")
        if kind == "caderno_recomendado":
            rec_id = event.get("recommendation_id")
            if rec_id is not None:
                if not isinstance(rec_id, str) or not rec_id.strip() or rec_id in recommendation_ids:
                    raise ValueError("recommendation_id inválido ou duplicado")
                recommendation_ids.add(rec_id)
            continue
        if kind not in ATTEMPT_TYPES:
            continue
        if not allow_private:
            raise ValueError("Resultados individuais bloqueados até confirmar repositório privado")
        attempt_id = event.get("attempt_id")
        rec_id = event.get("recommendation_id")
        if not isinstance(attempt_id, str) or not attempt_id.strip():
            raise ValueError("attempt_id ausente")
        if not isinstance(rec_id, str) or rec_id not in recommendation_ids:
            raise ValueError("recommendation_id sem recomendação anterior")
        platform_id = event.get("platform_notebook_id")
        if platform_id is not None and (not isinstance(platform_id, str) or not platform_id.strip()):
            raise ValueError("platform_notebook_id inválido")
        recorded = _date(event.get("recorded_at"), "recorded_at")
        attempt_at = event.get("attempt_at")
        if attempt_at is not None and _date(attempt_at, "attempt_at") > recorded:
            raise ValueError("attempt_at posterior a recorded_at")
        total = _count(event.get("total"), "total")
        correct = _count(event.get("acertos"), "acertos")
        errors = _count(event.get("erros"), "erros")
        unanswered = _count(event.get("nao_respondidas", 0), "nao_respondidas")
        if correct + errors + unanswered != total:
            raise ValueError("Totais inconsistentes em " + event_id)
        breakdown = event.get("topic_results", [])
        if not isinstance(breakdown, list):
            raise ValueError("topic_results inválido")
        assigned = set()
        for item in breakdown:
            topic = item.get("topic_id") if isinstance(item, dict) else None
            if topic not in topic_ids or topic in assigned:
                raise ValueError("topic_results com tópico inválido/duplicado")
            assigned.add(topic)
            attempted = _count(item.get("attempted"), "attempted")
            item_correct = _count(item.get("correct"), "correct")
            if item_correct > attempted:
                raise ValueError("Mais acertos que tentativas")
        if kind == "attempt_recorded":
            if attempt_id in latest_by_attempt:
                raise ValueError("attempt_id duplicado; use attempt_corrected")
        else:
            if attempt_id not in latest_by_attempt or event.get("corrects_event_id") != latest_by_attempt[attempt_id]:
                raise ValueError("Correção sem vínculo com último evento da tentativa")
        latest_by_attempt[attempt_id] = event_id
    return True


def rebuild_attempts(events, topics):
    """Project latest value per attempt; independent attempts are never overwritten."""
    progress = {row["topic_id"]: {"attempted": 0, "correct": 0} for row in topics}
    attempts = {}
    for event in events:
        kind = event.get("type")
        if kind == "attempt_recorded":
            attempts[event["attempt_id"]] = event
        elif kind == "attempt_corrected":
            attempts[event["attempt_id"]] = event
    for event in attempts.values():
        for item in event.get("topic_results", []):
            row = progress[item["topic_id"]]
            row["attempted"] += item["attempted"]
            row["correct"] += item["correct"]
    return {
        "attempts_count": len(attempts),
        "last_attempt_id": next(reversed(attempts), None),
        "progress": progress,
    }
