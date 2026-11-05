"""C25: narrow read-only check of curated critical claims; no publishing power.

A true citation is not proof of an arbitrary claim. This checks only the
structured fact IDs below, with independent-by-construction fact anchors
relative to the submitted claim. Not an independent audit or universal judge.
"""
import json
from pathlib import Path
from source_gate import ROOT, SOURCE, PINNED_SOURCE_BLOB, resolve_reference

FACTS = {
    "objective_minimum_percent": {
        "value": 50,
        "basis": ((10, "10.1. Serão considerados aprovados neste Concurso os candidatos que obtiverem o mínimo de 50%"),),
    },
    "zero_in_any_area_eliminates": {
        "value": True,
        "basis": ((10, "10.2. Será eliminado o candidato que obtiver nota zero em qualquer uma das cinco áreas de conhecimento."),),
    },
    "may_pass_with_zero_in_english": {
        "value": False,
        "basis": (
            (10, "10.2. Será eliminado o candidato que obtiver nota zero em qualquer uma das cinco áreas de conhecimento."),
            (10, "f) tiver maior pontuação na área de conhecimento: Língua Inglesa; e"),
        ),
    },
}
CONFLICT_ID = "heteroidentification_appeal_window"


def result(decision, reason, fact_id=None, *, references=()):
    return {
        "decision": decision,
        "reason_code": reason,
        "fact_id": fact_id,
        "source_refs": list(references),
        "semantic_support": "CURATED_FACT_MATCH_ONLY" if decision == "FACT_MATCHED" else "NOT_CHECKED",
        "publication_authorized": False,
        "external_effects": 0,
    }


def _conflict_still_exists(root):
    """An existing source conflict may not be auto-resolved by an LLM."""
    root = Path(root)
    state = json.loads((root / "edital/fontes_oficiais.json").read_text(encoding="utf-8"))
    alerts = state.get("open_alerts") or []
    a = next((x for x in alerts if x.get("id") == "ALERTA-DOC-01"), None)
    if not isinstance(a, dict) or (
        a.get("page") != 13
        or a.get("status") != "unresolved_source_inconsistency"
        or a.get("result_date_text") != "10/02/2027"
        or a.get("appeal_date_text") != "11 e 12/01/2027"
    ):
        raise ValueError("UNVERIFIABLE_SOURCE_CONFLICT")
    from chunk_edital import read_pages
    page = dict(read_pages((root / SOURCE).read_text(encoding="utf-8")))[13]
    if not all(value in page for value in ("10/02/2027", "11 e 12/01/2027")):
        raise ValueError("UNVERIFIABLE_SOURCE_CONFLICT")


def check_critical_claim(proposal, root=ROOT):
    """Compare typed structured claims with pinned source and curated fact anchors."""
    if not isinstance(proposal, dict):
        return result("NEEDS_EVIDENCE", "CLAIM_UNSUPPORTED")
    fact_id = proposal.get("fact_id")
    if not isinstance(fact_id, str) or fact_id not in FACTS and fact_id != CONFLICT_ID:
        return result("NEEDS_EVIDENCE", "CLAIM_UNSUPPORTED")
    citations = proposal.get("citations")
    if not isinstance(citations, list) or not 1 <= len(citations) <= 4:
        return result("NEEDS_EVIDENCE", "CLAIM_UNSUPPORTED", fact_id)
    for c in citations:
        checked = resolve_reference(c, root=root)
        if checked["decision"] == "DENY":
            return result("DENY", "BOOTSTRAP_INVALID", fact_id)
        if checked["decision"] != "EVIDENCE_RESOLVED":
            return result("NEEDS_EVIDENCE", "CLAIM_UNSUPPORTED", fact_id)
    if fact_id == CONFLICT_ID:
        try:
            _conflict_still_exists(root)
        except (ValueError, OSError, TypeError, UnicodeError, KeyError):
            return result("DENY", "BOOTSTRAP_INVALID", fact_id)
        return result("NEEDS_EVIDENCE", "SOURCE_CONFLICT", fact_id)
    fact = FACTS[fact_id]
    claim = proposal.get("claimed_value")
    if type(claim) is not type(fact["value"]) or claim != fact["value"]:
        return result("NEEDS_EVIDENCE", "CLAIM_UNSUPPORTED", fact_id)
    for page, anchor in fact["basis"]:
        if not any(
            c.get("source") == SOURCE and c.get("source_sha") == PINNED_SOURCE_BLOB
            and c.get("page") == page and anchor in c.get("quote", "")
            for c in citations
        ):
            return result("NEEDS_EVIDENCE", "CLAIM_UNSUPPORTED", fact_id)
    refs = [
        {"source": SOURCE, "source_sha": PINNED_SOURCE_BLOB, "page": page, "anchor": anchor}
        for page, anchor in fact["basis"]
    ]
    return result("FACT_MATCHED", "CURATED_FACT_ANCHORED", fact_id, references=refs)
