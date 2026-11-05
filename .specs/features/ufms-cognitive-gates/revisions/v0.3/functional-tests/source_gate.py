"""Deterministic C2/C3 *reference-resolution* gate, without publishing authority.

This module is usable only in a composed checkout containing the harness and
the unchanged canonical edital. Source text provenance != semantic support.
It neither calls an LLM nor owns outbound messaging, tokens or state writes.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "scripts"))
from chunk_edital import blob_sha, read_pages, validate as validate_chunks

SOURCE = "EDITAL_UFMS_152_2026.md"
PINNED_SOURCE_BLOB = "a4129cceabd20fc119625d71b1c1599b3ce644e1"
MAX_SPAN_CHARS = 1000


def _result(decision, code, **values):
    return {
        "decision": decision,
        "reason_code": code,
        "source_refs": [],
        "semantic_support": "NOT_CHECKED",
        "publication_authorized": False,
        "external_effects": 0,
        **values,
    }


def _checked_source(root):
    """Reject divergent original, manifest, and any chunk *before* resolving."""
    root = Path(root)
    raw = (root / SOURCE).read_bytes()
    original = raw.decode("utf-8")
    if blob_sha(original) != PINNED_SOURCE_BLOB:
        raise ValueError("SOURCE_HASH_DRIFT")
    manifest = json.loads((root / "edital/manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("source") != SOURCE
            or manifest.get("source_git_blob_sha") != PINNED_SOURCE_BLOB
            or manifest.get("page_count") != 47):
        raise ValueError("MANIFEST_SOURCE_DRIFT")
    if validate_chunks(root) != 81:
        raise ValueError("CHUNK_COUNT_DRIFT")
    pages = dict(read_pages(original))
    if len(pages) != 47:
        raise ValueError("PAGE_COUNT_DRIFT")
    return pages, manifest


def resolve_reference(proposal, root=ROOT):
    """Validate exact page-relative [start,end) and literal quote of the original.

    Validity proves only that the cited bytes exist in the pinned source.
    C25 must separately test whether those bytes support a particular claim.
    Any failure keeps publication disabled.
    """
    if not isinstance(proposal, dict):
        return _result("NEEDS_EVIDENCE", "SOURCE_NOT_FOUND")
    if (proposal.get("source") != SOURCE
            or proposal.get("source_sha") != PINNED_SOURCE_BLOB):
        return _result("NEEDS_EVIDENCE", "SOURCE_NOT_FOUND")
    page, span, quote = proposal.get("page"), proposal.get("span"), proposal.get("quote")
    if (type(page) is not int or not 1 <= page <= 47
            or not isinstance(span, dict)
            or type(span.get("start")) is not int
            or type(span.get("end")) is not int
            or not isinstance(quote, str)):
        return _result("NEEDS_EVIDENCE", "SOURCE_NOT_FOUND")
    start, end = span["start"], span["end"]
    if start < 0 or end <= start or end - start > MAX_SPAN_CHARS:
        return _result("NEEDS_EVIDENCE", "SOURCE_NOT_FOUND")
    try:
        pages, manifest = _checked_source(root)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return _result("DENY", "BOOTSTRAP_INVALID")
    body = pages[page]
    if end > len(body) or body[start:end] != quote or not quote.strip():
        return _result("NEEDS_EVIDENCE", "SOURCE_NOT_FOUND")
    overlapping = [
        item["id"] for item in manifest["chunks"]
        if item["page"] == page
        and item["char_start"] < end
        and item["char_end"] > start
    ]
    if not overlapping:
        return _result("DENY", "BOOTSTRAP_INVALID")
    reference = {
        "source": SOURCE,
        "source_sha": PINNED_SOURCE_BLOB,
        "page": page,
        "span": {"start": start, "end": end},
        "chunk_ids": overlapping,
    }
    return _result(
        "EVIDENCE_RESOLVED", "EXACT_SPAN_MATCH",
        source_refs=[reference],
        quote=quote,
    )
