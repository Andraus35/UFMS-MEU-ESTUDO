"""Deterministic informational evidence levels E0-E4.

Levels describe information quality, never student mastery or probability of success.
"""
from datetime import datetime

INDEPENDENCE = {"without_consultation", "with_consultation", "mixed", "unknown"}
FAMILIARITY = {"new", "repeated", "mixed", "unknown"}
DIVERSITY = {"varied", "homogeneous", "unknown"}
CONFIDENCE = {"secure", "insecure", "unknown"}
SOURCE_KIND = {"platform_export", "manual_report", "file_extract", "unknown"}


def _parse(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.utcoffset() is not None else None


def derive_evidence_level(events):
    """Derive E0-E4 from verified fields; missing context remains unknown."""
    legacy = {}
    attempts = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if kind in ("resultado_recebido", "resultado_corrigido"):
            legacy[event.get("caderno_id")] = event
        elif kind in ("attempt_recorded", "attempt_corrected"):
            attempts[event.get("attempt_id")] = event

    results = list(legacy.values()) + list(attempts.values())
    if not results:
        return {
            "level": "E0",
            "dimensions": {
                "granularity": "none", "independence": "unknown",
                "familiarity": "unknown", "temporality": "unknown",
                "diversity": "unknown", "provenance": "unknown",
                "confidence": "unknown",
            },
            "uncertainties": ["no_assessment"],
            "knowledge_status": "unknown_until_evidence",
        }

    topic_level = any(
        isinstance(event.get("topic_results"), list)
        and any(
            isinstance(row, dict)
            and type(row.get("attempted")) is int
            and row["attempted"] > 0
            for row in event["topic_results"]
        )
        for event in results
    )
    level = "E2" if topic_level else "E1"
    contextual = []
    for event in attempts.values():
        at = _parse(event.get("attempt_at"))
        dimensions = (
            event.get("independence", "unknown"),
            event.get("familiarity", "unknown"),
            event.get("diversity", "unknown"),
            event.get("source_kind", "unknown"),
            event.get("confidence", "unknown"),
        )
        if at and all(value != "unknown" for value in dimensions):
            contextual.append((event, at, dimensions))
    if contextual:
        level = "E3"

    independent = [
        (event, at) for event, at, dims in contextual
        if dims[0] == "without_consultation"
        and dims[1] == "new"
        and dims[2] == "varied"
        and dims[3] in {"platform_export", "manual_report", "file_extract"}
        and isinstance(event.get("item_set_id"), str)
        and event["item_set_id"].strip()
    ]
    distinct_sets = {event["item_set_id"] for event, _ in independent}
    distinct_dates = {at.date() for _, at in independent}
    if len(independent) >= 2 and len(distinct_sets) >= 2 and len(distinct_dates) >= 2:
        level = "E4"

    latest_context = contextual[-1][0] if contextual else {}
    dimensions = {
        "granularity": "topic" if topic_level else "aggregate",
        "independence": latest_context.get("independence", "unknown"),
        "familiarity": latest_context.get("familiarity", "unknown"),
        "temporality": "known" if contextual else "unknown",
        "diversity": latest_context.get("diversity", "unknown"),
        "provenance": latest_context.get("source_kind", "unknown"),
        "confidence": latest_context.get("confidence", "unknown"),
    }
    uncertainties = []
    if not topic_level:
        uncertainties.append("aggregate_only_no_topic_breakdown")
    if not contextual:
        uncertainties.extend([
            "attempt_time_unknown",
            "independence_unknown",
            "familiarity_unknown",
            "diversity_unknown",
            "provenance_unknown",
            "confidence_unknown",
        ])
    if level != "E4":
        uncertainties.append("insufficient_independent_recoveries_on_distinct_dates_and_item_sets")
    return {
        "level": level,
        "dimensions": dimensions,
        "uncertainties": sorted(set(uncertainties)),
        "knowledge_status": "unknown_until_evidence",
    }
