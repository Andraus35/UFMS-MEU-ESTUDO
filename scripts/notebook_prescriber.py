"""Offline notebook prescription plan; never creates platform notebooks or IDs."""
import hashlib
import json

INTERVENTIONS = {
    "diagnostic", "guided_learning", "fixation", "active_retrieval",
    "spaced_review", "focused_correction", "interleaving", "transfer", "simulation",
}
PLATFORMS = {"TEC", "Qconcursos", "student_choice", "manual_search"}
CAPABILITIES = {
    "topic_filter", "cargo_filter", "bank_filter", "year_filter",
    "difficulty_filter", "novelty_filter", "comment_filter",
}


def _confirmed(value, label):
    if not isinstance(value, dict):
        raise ValueError(label + " deve ser objeto")
    status = value.get("status", "unknown")
    if status not in {"confirmed", "unknown", "unsupported", "unavailable"}:
        raise ValueError(label + " status inválido")
    if status == "confirmed":
        if not isinstance(value.get("evidence_ref"), str) or not value["evidence_ref"].strip():
            raise ValueError(label + " confirmado sem evidence_ref")
    return {**value, "status": status}


def prescribe_notebook(queue_snapshot, *, candidate_id, intervention, objective,
                       platform, platform_capabilities=None, availability=None,
                       question_target=None, execution_mode="independent",
                       selection_override_reason=None):
    """Create an auditable instruction plan, not an external notebook."""
    if not isinstance(queue_snapshot, dict) or not queue_snapshot.get("snapshot_id"):
        raise ValueError("Snapshot de fila ausente")
    ranked = queue_snapshot.get("ranked")
    if not isinstance(ranked, list):
        raise ValueError("Snapshot sem candidatos ranqueados")
    candidate = next((row for row in ranked if row.get("candidate_id") == candidate_id), None)
    if candidate is None:
        raise ValueError("Candidato não consta do snapshot")
    selected = queue_snapshot.get("selected_candidate_id")
    if candidate_id != selected and (not isinstance(selection_override_reason, str) or not selection_override_reason.strip()):
        raise ValueError("Alternativa exige justificativa explícita")
    if intervention not in INTERVENTIONS:
        raise ValueError("Intervenção inválida")
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("Objetivo ausente")
    if platform not in PLATFORMS:
        raise ValueError("Plataforma não reconhecida; não presumir integração")
    if execution_mode not in {"independent", "guided"}:
        raise ValueError("execution_mode inválido")
    if question_target is not None and (type(question_target) is not int or question_target <= 0):
        raise ValueError("question_target deve ser inteiro positivo ou null")

    capabilities = platform_capabilities or {}
    if not isinstance(capabilities, dict) or set(capabilities) - CAPABILITIES:
        raise ValueError("Capacidade de plataforma desconhecida")
    normalized_capabilities = {}
    for name in sorted(CAPABILITIES):
        item = _confirmed(capabilities.get(name, {"status": "unknown"}), "capability." + name)
        normalized_capabilities[name] = {
            "status": item.get("status", "unknown"),
            "evidence_ref": item.get("evidence_ref"),
        }

    availability = _confirmed(availability or {"status": "unknown"}, "availability")
    count = availability.get("available_count")
    if availability["status"] == "confirmed":
        if type(count) is not int or count < 0:
            raise ValueError("Disponibilidade confirmada exige available_count")
    elif count is not None:
        raise ValueError("available_count só pode existir quando confirmado")

    suggested_count = None
    if availability["status"] == "confirmed" and count and question_target:
        suggested_count = min(count, question_target)
    availability_status = (
        "confirmed" if availability["status"] == "confirmed" and count and count > 0
        else "unavailable_or_unverified"
    )

    topic_ids = list(candidate["topic_ids"])
    cargo_ids = list(candidate["cargo_ids"])
    filters = {
        "layer_0_scope": {
            "required": True,
            "cargo_ids": cargo_ids,
            "topic_ids": topic_ids,
            "status": "confirmed" if (
                normalized_capabilities["topic_filter"]["status"] == "confirmed"
                and normalized_capabilities["cargo_filter"]["status"] == "confirmed"
            ) else "pending_confirmation",
        },
        "layer_1_pedagogical": {
            "novelty": "prefer_new_when_independent",
            "diversity": "prefer_varied",
            "status": "proposed",
        },
        "layer_2_exam_similarity": {
            "bank": "FAPEC",
            "status": normalized_capabilities["bank_filter"]["status"],
            "note": "Usar somente se houver amostra e filtro realmente disponíveis",
        },
        "layer_3_optional": {
            "year": normalized_capabilities["year_filter"]["status"],
            "difficulty": normalized_capabilities["difficulty_filter"]["status"],
            "novelty": normalized_capabilities["novelty_filter"]["status"],
            "comments": normalized_capabilities["comment_filter"]["status"],
        },
    }
    fallback = [
        {"step": 1, "action": "remove_optional_refinements", "preserve": ["cargo_ids", "topic_ids"]},
        {"step": 2, "action": "widen_year_period", "preserve": ["cargo_ids", "topic_ids"]},
        {"step": 3, "action": "consider_comparable_banks", "preserve": ["cargo_ids", "topic_ids"],
         "caveat": "comparabilidade deve ser rotulada"},
        {"step": 4, "action": "widen_level_or_question_type", "preserve": ["cargo_ids", "topic_ids"],
         "caveat": "não usar como equivalente oficial sem validação"},
        {"step": 5, "action": "combine_topics_only_if_justified", "preserve": ["verified_scope_only"]},
    ]
    identity = {
        "snapshot_id": queue_snapshot["snapshot_id"],
        "candidate_id": candidate_id,
        "platform": platform,
        "intervention": intervention,
        "objective": objective,
        "filters": filters,
    }
    recommendation_id = "rec-" + hashlib.sha256(
        json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:20]
    return {
        "recommendation_id": recommendation_id,
        "source_snapshot": {
            "snapshot_id": queue_snapshot["snapshot_id"],
            "as_of": queue_snapshot.get("as_of"),
            "source_commit": queue_snapshot.get("source_commit"),
            "edital_version": queue_snapshot.get("edital_version"),
            "policy_version": queue_snapshot.get("policy", {}).get("version"),
        },
        "candidate_id": candidate_id,
        "cargo_ids": cargo_ids,
        "topic_ids": topic_ids,
        "intervention": intervention,
        "objective": objective,
        "platform": platform,
        "platform_capabilities": normalized_capabilities,
        "filters": filters,
        "questions_suggested": suggested_count,
        "question_target_requested": question_target,
        "availability_status": availability_status,
        "availability_evidence_ref": availability.get("evidence_ref"),
        "execution_mode": execution_mode,
        "expected_return": {
            "minimum": ["platform", "recommendation_id", "date", "presented", "correct", "incorrect", "unanswered"],
            "optional": ["attempt_at", "independence", "familiarity", "time_spent", "topic_results", "confidence"],
        },
        "rationale": candidate["justification"],
        "deferred_alternative": candidate.get("deferred_alternative"),
        "selection_override_reason": selection_override_reason,
        "fallback": fallback,
        "status": "recommended",
        "creation_status": "not_created",
        "platform_notebook_id": None,
        "platform_notebook_id_status": "unknown",
        "side_effects_performed": False,
    }
