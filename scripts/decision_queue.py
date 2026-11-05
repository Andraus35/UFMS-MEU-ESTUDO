"""Deterministic adaptive queue: explicit snapshot, policy and auditable ranking."""
import hashlib
import json
import re
from datetime import datetime

FACTOR_WEIGHTS = {
    "elimination_risk": 3,
    "learning_need": 1,
    "coverage_gap": 1,
    "retention_signal": 1,
    "exam_impact": 1,
    "uncertainty_reduction": 1,
    "cross_cargo_benefit": 1,
    "freshness_diversity": 1,
    "feasibility": 1,
    "opportunity_cost": -1,
}
FACTOR_NAMES = tuple(FACTOR_WEIGHTS)
ELIGIBILITY = {
    "eligible", "needs_evidence", "pending_confirmation",
    "temporarily_deferred", "blocked", "completed_observation",
}
RANKABLE = {"eligible", "needs_evidence"}


def _validate_as_of(value):
    if not isinstance(value, str):
        raise ValueError("as_of deve ser ISO 8601 com fuso")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("as_of inválido") from exc
    if parsed.utcoffset() is None:
        raise ValueError("as_of precisa informar fuso")
    return value


def _policy(policy):
    if policy is None:
        return {"version": "rm04-v1", "weights": dict(FACTOR_WEIGHTS)}
    if not isinstance(policy, dict) or not isinstance(policy.get("version"), str) or not policy["version"]:
        raise ValueError("Política precisa de versão explícita")
    weights = policy.get("weights")
    if not isinstance(weights, dict) or set(weights) != set(FACTOR_NAMES):
        raise ValueError("Pesos da política incompletos ou desconhecidos")
    if any(type(value) is not int or value < -5 or value > 5 for value in weights.values()):
        raise ValueError("Pesos devem ser inteiros entre -5 e 5")
    return {"version": policy["version"], "weights": dict(weights)}


def _candidate(candidate):
    if not isinstance(candidate, dict):
        raise ValueError("Candidato deve ser objeto")
    cid = candidate.get("candidate_id")
    if not isinstance(cid, str) or not cid.strip():
        raise ValueError("candidate_id ausente")
    status = candidate.get("eligibility")
    if status not in ELIGIBILITY:
        raise ValueError("Estado de elegibilidade inválido: " + str(cid))
    topics = candidate.get("topic_ids")
    cargos = candidate.get("cargo_ids")
    if not isinstance(topics, list) or not topics or len(set(topics)) != len(topics):
        raise ValueError("topic_ids ausentes ou duplicados: " + cid)
    if not isinstance(cargos, list) or not cargos or len(set(cargos)) != len(cargos):
        raise ValueError("cargo_ids ausentes ou duplicados: " + cid)
    if any(value not in {"523", "324"} for value in cargos):
        raise ValueError("Cargo fora do escopo: " + cid)
    factors = candidate.get("priority_factors")
    if not isinstance(factors, dict) or set(factors) != set(FACTOR_NAMES):
        raise ValueError("Fatores incompletos ou desconhecidos: " + cid)
    for name, value in factors.items():
        if value is not None and (type(value) is not int or value < 0 or value > 3):
            raise ValueError("Fator deve ser null ou inteiro 0..3: " + name)
    justification = candidate.get("justification")
    if not isinstance(justification, str) or not justification.strip():
        raise ValueError("Justificativa ausente: " + cid)
    return candidate


def rank_candidates(candidates, *, as_of, source_commit, edital_version, policy=None):
    """Return an immutable-style snapshot; no clock, network, random or persistence."""
    _validate_as_of(as_of)
    if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source_commit deve ser SHA Git de 40 caracteres")
    if not isinstance(edital_version, str) or not edital_version.strip():
        raise ValueError("edital_version ausente")
    if not isinstance(candidates, list):
        raise ValueError("candidates deve ser lista")
    selected_policy = _policy(policy)
    seen = set()
    ranked = []
    excluded = []
    for raw in candidates:
        item = _candidate(raw)
        cid = item["candidate_id"]
        if cid in seen:
            raise ValueError("candidate_id duplicado: " + cid)
        seen.add(cid)
        status = item["eligibility"]
        if status not in RANKABLE:
            excluded.append({"candidate_id": cid, "eligibility": status,
                             "reason": item.get("blocked_reason") or status})
            continue
        factors = item["priority_factors"]
        if factors["feasibility"] == 0:
            excluded.append({"candidate_id": cid, "eligibility": status,
                             "reason": "feasibility_zero"})
            continue
        breakdown = {}
        score = 0
        unknown = []
        for name in FACTOR_NAMES:
            value = factors[name]
            if value is None:
                unknown.append(name)
                contribution = 0
            else:
                contribution = value * selected_policy["weights"][name]
            breakdown[name] = {"value": value, "weight": selected_policy["weights"][name],
                               "contribution": contribution}
            score += contribution
        ranked.append({
            "candidate_id": cid,
            "eligibility": status,
            "topic_ids": list(item["topic_ids"]),
            "cargo_ids": list(item["cargo_ids"]),
            "score": score,
            "score_breakdown": breakdown,
            "unknown_factors": unknown,
            "justification": item["justification"],
            "deferred_alternative": item.get("deferred_alternative"),
        })
    ranked.sort(key=lambda row: (-row["score"], row["candidate_id"]))
    payload = {
        "as_of": as_of,
        "source_commit": source_commit,
        "edital_version": edital_version,
        "policy": selected_policy,
        "ranked": ranked,
        "excluded": sorted(excluded, key=lambda row: row["candidate_id"]),
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["snapshot_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    payload["selected_candidate_id"] = ranked[0]["candidate_id"] if ranked else None
    payload["alternative_candidate_ids"] = [row["candidate_id"] for row in ranked[1:4]]
    payload["probability_claims"] = False
    return payload
