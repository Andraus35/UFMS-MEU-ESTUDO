"""Isolated C26 local-preview renderer. No real messaging or LLM credentials.

A TRUSTED policy supervisor (not the LLM) must pass the verified gate receipt to
OutputAuthority.issue(). Signer/renderer process isolation and mandatory channel
routing remain UNPROVEN until real integration. Only local_preview is supported.
"""
import hashlib
import hmac
import json
import secrets
import sqlite3
import threading
import uuid
from pathlib import Path

EXPECTED_FIELDS = frozenset((
    "release_id", "issuer_id", "run_id", "proposal_hash", "policy_sha",
    "state_revision", "source_set_sha", "actor_role", "channel", "recipient",
    "output_kind", "expires_at", "nonce", "authorization_epoch",
))
CONTEXT_FIELDS = (
    "run_id", "policy_sha", "state_revision", "source_set_sha",
    "actor_role", "channel", "recipient", "output_kind",
)


def canonical(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def proposal_hash(proposal):
    return hashlib.sha256(canonical(proposal)).hexdigest()


def _valid_proposal(proposal):
    return (
        type(proposal) is dict
        and set(proposal) == {"text", "effect_kind", "output_kind"}
        and type(proposal["text"]) is str
        and 0 < len(proposal["text"].encode("utf-8")) <= 65536
        and proposal["effect_kind"] == "NONE"
        and proposal["output_kind"] == "ORIENTACAO"
    )


def _valid_context(context):
    return (
        type(context) is dict
        and set(context) == set(CONTEXT_FIELDS)
        and all(type(context[k]) is str and 0 < len(context[k]) <= 256
                for k in CONTEXT_FIELDS)
        and context["actor_role"] in ("Tutor", "Coach")
        and context["channel"] == "local_preview"
        and context["output_kind"] == "ORIENTACAO"
    )


def _deny(code="OUTPUT_NOT_APPROVED"):
    return {"decision": "DENY", "reason_code": code, "local_emissions": 0}


class SharedLedger:
    """SQLite transaction serializes nonce consumption across renderer instances.

    In production, use a durable, independently secured store with atomic
    reservation and recipient-channel delivery reconciliation.
    """
    def __init__(self, filename):
        self.filename = str(Path(filename))
        with sqlite3.connect(self.filename, timeout=10) as db:
            db.execute("CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY CHECK (id=1), epoch INTEGER NOT NULL)")
            db.execute("INSERT OR IGNORE INTO meta(id,epoch) VALUES (1,0)")
            db.execute("CREATE TABLE IF NOT EXISTS consumed (release_id TEXT PRIMARY KEY, nonce TEXT UNIQUE NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS revoked (release_id TEXT PRIMARY KEY)")

    def epoch(self):
        with sqlite3.connect(self.filename, timeout=10) as db:
            return db.execute("SELECT epoch FROM meta WHERE id=1").fetchone()[0]

    def advance_epoch(self):
        with sqlite3.connect(self.filename, timeout=10) as db:
            db.execute("UPDATE meta SET epoch=epoch+1 WHERE id=1")

    def revoke(self, release_id):
        with sqlite3.connect(self.filename, timeout=10) as db:
            db.execute("INSERT OR IGNORE INTO revoked(release_id) VALUES (?)", (release_id,))

    def reserve(self, release_id, nonce, token_epoch):
        db = sqlite3.connect(self.filename, timeout=10, isolation_level=None)
        try:
            db.execute("BEGIN IMMEDIATE")
            epoch = db.execute("SELECT epoch FROM meta WHERE id=1").fetchone()[0]
            blocked = db.execute(
                "SELECT 1 FROM revoked WHERE release_id=?", (release_id,)
            ).fetchone()
            if epoch != token_epoch or blocked:
                db.execute("ROLLBACK")
                return False
            try:
                db.execute(
                    "INSERT INTO consumed (release_id,nonce) VALUES (?,?)",
                    (release_id,nonce)
                )
            except sqlite3.IntegrityError:
                db.execute("ROLLBACK")
                return False
            db.execute("COMMIT")
            return True
        finally:
            db.close()


class OutputAuthority:
    """Automatic internal issuer for ALLOW/NONE, NOT a human approval service."""
    def __init__(self, signing_key, ledger, issuer_id="trusted-local-policy"):
        if type(signing_key) is not bytes or len(signing_key) < 32:
            raise ValueError("Signing key must be 32+ bytes, kept outside LLM")
        self._key = signing_key
        self.ledger = ledger
        self.issuer_id = issuer_id

    def issue(self, proposal, context, gate_receipt, *, now, ttl=120):
        if not _valid_proposal(proposal) or not _valid_context(context):
            return None
        if type(now) is not int or type(ttl) is not int or not 0 < ttl <= 300:
            return None
        expected_gate = {
            "decision": "ALLOW", "effect_kind": "NONE",
            "proposal_hash": proposal_hash(proposal),
            "run_id": context["run_id"], "policy_sha": context["policy_sha"],
            "state_revision": context["state_revision"],
            "source_set_sha": context["source_set_sha"],
            "actor_role": context["actor_role"],
        }
        if type(gate_receipt) is not dict or gate_receipt != expected_gate:
            return None
        body = {
            **context,
            "release_id": uuid.uuid4().hex,
            "issuer_id": self.issuer_id,
            "proposal_hash": proposal_hash(proposal),
            "expires_at": now + ttl,
            "nonce": secrets.token_hex(16),
            "authorization_epoch": self.ledger.epoch(),
        }
        mac = hmac.new(self._key, canonical(body), hashlib.sha256).hexdigest()
        return {"body": body, "mac": mac}


class LocalPreviewSink:
    """No channel or network: an in-memory, thread-safe test-only sink."""
    def __init__(self):
        self._lock = threading.Lock()
        self.messages = []

    def emit(self, text):
        with self._lock:
            self.messages.append(text)


class SafeRenderer:
    def __init__(self, signing_key, ledger, sink, issuer_id="trusted-local-policy"):
        if type(signing_key) is not bytes or len(signing_key) < 32:
            raise ValueError("Invalid renderer key")
        self._key = signing_key
        self._ledger = ledger
        self._sink = sink
        self._issuer_id = issuer_id

    def render(self, proposal, context, token, *, now):
        if not _valid_proposal(proposal) or not _valid_context(context):
            return _deny()
        if type(now) is not int or type(token) is not dict or set(token) != {"body", "mac"}:
            return _deny()
        body, mac = token["body"], token["mac"]
        if type(body) is not dict or set(body) != EXPECTED_FIELDS or type(mac) is not str:
            return _deny()
        try:
            expected_mac = hmac.new(
                self._key, canonical(body), hashlib.sha256
            ).hexdigest()
        except (TypeError, ValueError, OverflowError):
            return _deny()
        if not hmac.compare_digest(mac, expected_mac):
            return _deny()
        if any(body[k] != context[k] for k in CONTEXT_FIELDS):
            return _deny()
        if (body["issuer_id"] != self._issuer_id
                or body["proposal_hash"] != proposal_hash(proposal)
                or type(body["expires_at"]) is not int
                or not now < body["expires_at"]
                or type(body["authorization_epoch"]) is not int
                or type(body["release_id"]) is not str
                or type(body["nonce"]) is not str
                or len(body["release_id"]) != 32
                or len(body["nonce"]) != 32):
            return _deny()
        try:
            consumed = self._ledger.reserve(
                body["release_id"], body["nonce"], body["authorization_epoch"]
            )
        except sqlite3.Error:
            return _deny("DEPENDENCY_FAILED")
        if not consumed:
            return _deny()
        try:
            self._sink.emit(proposal["text"])
        except Exception:
            # The sink may have emitted before error: no blind retry.
            return {
                "decision": "UNCONFIRMED",
                "reason_code": "EMISSION_UNCONFIRMED",
                "local_emissions": 0,
                "retry_allowed": False,
            }
        return {
            "decision": "COMPLETE",
            "reason_code": "LOCAL_PREVIEW_ONLY",
            "local_emissions": 1,
        }
