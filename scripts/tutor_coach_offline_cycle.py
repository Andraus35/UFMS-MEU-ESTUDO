"""Pure offline preparation of a Tutor-Coach cycle using synthetic fixtures only.

This module does not contact TEC/Qconcursos, write events, update CURRENT.json,
or persist recommendation/result data. Every identifier and source must be synthetic.
"""
from copy import deepcopy

try:
    from decision_queue import rank_candidates
    from notebook_prescriber import prescribe_notebook
    from gp1_ingestion import normalize_external_report, validate_attempt_events, rebuild_attempts
    from evidence_projection import derive_evidence_level
except ModuleNotFoundError:
    from scripts.decision_queue import rank_candidates
    from scripts.notebook_prescriber import prescribe_notebook
    from scripts.gp1_ingestion import normalize_external_report, validate_attempt_events, rebuild_attempts
    from scripts.evidence_projection import derive_evidence_level


SYNTHETIC_ORIGIN = "synthetic_fixture"
SYNTHETIC_REF_PREFIX = "synthetic-fixture://"
SYNTHETIC_ID_PREFIX = "SYNTH-"
OFFLINE_PLATFORM = "manual_search"

REPORT_FIELDS = {
    "data_origin", "platform", "event_id", "attempt_id", "recommendation_id",
    "platform_notebook_id", "recorded_at", "attempt_at", "source_ref",
    "answered_convention", "reported_answered", "reported_unanswered",
    "correct", "incorrect", "independence", "familiarity", "diversity",
    "confidence", "source_kind", "item_set_id", "topic_results", "execution_ref",
}
EXECUTION_FIELDS = {"data_origin", "status", "execution_ref", "candidate_id"}


def _synthetic_identifier(value, label):
    if not isinstance(value, str) or not value.startswith(SYNTHETIC_ID_PREFIX):
        raise ValueError(label + " deve usar identificador SYNTH-")


def _synthetic_candidates(candidates, label):
    if not isinstance(candidates, list):
        raise ValueError(label + " deve ser uma lista")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError(label + " contém candidato inválido")
        _synthetic_identifier(candidate.get("candidate_id"), label + ".candidate_id")


def _execution(execution, selected_candidate_id):
    if not isinstance(execution, dict) or set(execution) - EXECUTION_FIELDS:
        raise ValueError("Execução simulada contém campos inválidos")
    if execution.get("data_origin") != SYNTHETIC_ORIGIN:
        raise ValueError("Execução precisa ser marcada como synthetic_fixture")
    if execution.get("status") != "simulated":
        raise ValueError("Esta preparação aceita somente execução simulada")
    candidate_id = execution.get("candidate_id")
    _synthetic_identifier(candidate_id, "execution.candidate_id")
    if candidate_id != selected_candidate_id:
        raise ValueError("Execução simulada não corresponde ao candidato recomendado")
    ref = execution.get("execution_ref")
    if not isinstance(ref, str) or not ref.startswith(SYNTHETIC_REF_PREFIX):
        raise ValueError("execution_ref deve apontar para fixture sintética")
    return {
        "data_origin": SYNTHETIC_ORIGIN,
        "status": "simulated",
        "execution_ref": ref,
        "candidate_id": candidate_id,
    }


def _result_report(report, recommendation_id, execution_ref):
    if not isinstance(report, dict) or set(report) - REPORT_FIELDS:
        raise ValueError("Relatório sintético contém campos inválidos ou não previstos")
    if report.get("data_origin") != SYNTHETIC_ORIGIN:
        raise ValueError("Resultado precisa ser marcado como synthetic_fixture")
    if report.get("platform") != OFFLINE_PLATFORM:
        raise ValueError("Plataforma externa não é permitida no ciclo offline")
    supplied_rec = report.get("recommendation_id")
    if supplied_rec is not None and supplied_rec != recommendation_id:
        raise ValueError("Resultado vinculado a recommendation_id diferente")
    if report.get("execution_ref") != execution_ref:
        raise ValueError("Resultado não corresponde à execução simulada")
    if report.get("platform_notebook_id") is not None:
        raise ValueError("ID de caderno externo não é permitido no ciclo offline")

    for field in ("event_id", "attempt_id"):
        _synthetic_identifier(report.get(field), field)
    source_ref = report.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.startswith(SYNTHETIC_REF_PREFIX):
        raise ValueError("source_ref deve apontar para fixture sintética")
    item_set_id = report.get("item_set_id")
    if item_set_id is not None:
        _synthetic_identifier(item_set_id, "item_set_id")

    normalized_input = {
        key: value for key, value in report.items()
        if key not in {"data_origin", "platform", "answered_convention"}
    }
    normalized_input["recommendation_id"] = recommendation_id
    normalized = normalize_external_report(normalized_input, report.get("answered_convention"))
    if normalized.get("decision") != "normalized":
        raise ValueError("Convenção do relatório precisa ser explícita")
    return normalized


def run_offline_cycle(
    *,
    candidates,
    next_candidates,
    topics,
    as_of,
    reevaluation_as_of,
    source_commit,
    edital_version,
    execution_simulation,
    result_report,
    objective,
    intervention="diagnostic",
    question_target=None,
    policy=None,
    next_policy=None,
):
    """Run recommendation → simulated execution → synthetic result → re-evaluation.

    All result validation and reconstruction happens in memory. The second queue
    consumes explicitly supplied candidate factors; it does not infer mastery,
    retention, or new priority-factor values from an aggregate score.
    """
    _synthetic_candidates(candidates, "candidates")
    _synthetic_candidates(next_candidates, "next_candidates")
    if not isinstance(topics, list) or not topics:
        raise ValueError("topics precisa conter os tópicos conhecidos")
    topic_ids = {
        row.get("topic_id") for row in topics
        if isinstance(row, dict) and isinstance(row.get("topic_id"), str)
    }
    if not topic_ids:
        raise ValueError("topics sem topic_id válido")

    first_queue = rank_candidates(
        candidates, as_of=as_of, source_commit=source_commit,
        edital_version=edital_version, policy=policy,
    )
    selected_id = first_queue.get("selected_candidate_id")
    if selected_id is None:
        raise ValueError("Não há candidato elegível para recomendação sintética")

    recommendation = prescribe_notebook(
        first_queue,
        candidate_id=selected_id,
        intervention=intervention,
        objective=objective,
        platform=OFFLINE_PLATFORM,
        availability={"status": "unknown"},
        question_target=question_target,
        execution_mode="independent",
    )
    execution = _execution(execution_simulation, recommendation["candidate_id"])
    normalized = _result_report(
        result_report, recommendation["recommendation_id"], execution["execution_ref"]
    )
    attempt_event = normalized["event"]
    attempt_event["execution_ref"] = execution["execution_ref"]

    unknown_topics = set(recommendation["topic_ids"]) - topic_ids
    if unknown_topics:
        raise ValueError("Recomendação contém tópico ausente do catálogo")
    recommendation_event = {
        "event_id": "SYNTH-REC-" + recommendation["recommendation_id"].removeprefix("rec-"),
        "type": "caderno_recomendado",
        "recommendation_id": recommendation["recommendation_id"],
        "topic_ids": list(recommendation["topic_ids"]),
    }
    events_in_memory = [recommendation_event, attempt_event]

    # True enables schema validation only inside this ephemeral synthetic sandbox.
    # No write API, event log, CURRENT.json, or progress projection is touched.
    validate_attempt_events(events_in_memory, topics, allow_private=True)
    reconstruction = rebuild_attempts(events_in_memory, topics)
    evidence = derive_evidence_level(events_in_memory)
    next_queue = rank_candidates(
        next_candidates, as_of=reevaluation_as_of, source_commit=source_commit,
        edital_version=edital_version, policy=next_policy,
    )
    return {
        "data_origin": SYNTHETIC_ORIGIN,
        "recommendation": recommendation,
        "execution_simulation": execution,
        "result": {
            "decision": normalized["decision"],
            "normalization": normalized["normalization"],
            "event": deepcopy(attempt_event),
        },
        "validation": {
            "schema_valid": True,
            "in_memory_only": True,
            "persistence_authorized": False,
        },
        "reconstruction": reconstruction,
        "evidence": evidence,
        "reevaluation": {
            "next_queue_snapshot": next_queue,
            "candidate_factors_source": "explicit_synthetic_inputs",
            "automatic_factor_updates": False,
            "probability_claims": False,
        },
        "side_effects_performed": False,
        "external_integrations_used": False,
        "persisted": False,
    }
