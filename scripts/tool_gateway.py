"""Fail-closed, offline tool gateway prototype.

This module has no network clients. The caller supplies an adapter only after the
authorization, binding, nonce, rate-limit and state checks pass. Production use
requires a separately isolated approval issuer and secret store.
"""
import base64
import hashlib
import hmac
import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

MAX_INPUT_BYTES = 65536
DEFAULT_RATE_LIMIT = 5
DEFAULT_RATE_WINDOW_SECONDS = 60
EXIT_CODES = {
    "COMMITTED": 0,
    "DENIED": 1,
    "STALE_STATE": 1,
    "NEEDS_APPROVAL": 2,
    "NEEDS_EVIDENCE": 2,
    "DEPENDENCY_FAILED": 3,
    "UNCONFIRMED": 3,
}


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _parse_time(value):
    if not isinstance(value, str):
        raise ValueError("timestamp ausente")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("timestamp sem fuso")
    return parsed


def _b64(data):
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def action_hash(request):
    return _sha({
        "tool": request.get("tool"),
        "recipient": request.get("recipient"),
        "parameters": request.get("parameters"),
        "output_kind": request.get("output_kind"),
    })


def sign_approval_receipt(payload, approval_key):
    """Test/approval-service helper. Never expose approval_key to the model process."""
    signature = hmac.new(approval_key, _canonical(payload), hashlib.sha256).digest()
    return {"payload": payload, "signature": _b64(signature)}


def _verify_signed(signed, key):
    if not isinstance(signed, dict) or not isinstance(signed.get("payload"), dict):
        return None
    expected = hmac.new(key, _canonical(signed["payload"]), hashlib.sha256).digest()
    try:
        supplied = _unb64(signed.get("signature", ""))
    except Exception:
        return None
    return signed["payload"] if hmac.compare_digest(expected, supplied) else None


def issue_authorization(request, approval_receipt, *, approval_key, gateway_key, now=None):
    """Exchange a separately signed exact-action approval for a short-lived gateway token."""
    now = now or datetime.now(timezone.utc)
    approval = _verify_signed(approval_receipt, approval_key)
    if not approval:
        raise ValueError("NEEDS_APPROVAL: invalid approval signature")
    if approval.get("approved") is not True:
        raise ValueError("NEEDS_APPROVAL: approval absent")
    if approval.get("approver_id") == request.get("actor_id"):
        raise ValueError("NEEDS_APPROVAL: approver and actor must differ")
    required = (
        "approval_id", "approver_id", "actor_id", "tool", "recipient",
        "action_hash", "policy_sha", "state_revision", "run_id",
        "proposal_hash", "source_set_sha", "output_kind",
        "authorization_epoch", "nonce", "expires_at",
    )
    if any(not approval.get(field) for field in required):
        raise ValueError("NEEDS_APPROVAL: incomplete approval binding")
    expected = {
        "actor_id": request.get("actor_id"),
        "tool": request.get("tool"),
        "recipient": request.get("recipient"),
        "action_hash": action_hash(request),
        "policy_sha": request.get("policy_sha"),
        "state_revision": request.get("state_revision"),
        "run_id": request.get("run_id"),
        "proposal_hash": request.get("proposal_hash"),
        "source_set_sha": request.get("source_set_sha"),
        "output_kind": request.get("output_kind"),
        "authorization_epoch": request.get("authorization_epoch"),
    }
    for field, value in expected.items():
        if approval.get(field) != value:
            raise ValueError("DENY:AUTH_MISMATCH:" + field)
    expires = _parse_time(approval["expires_at"])
    if expires <= now:
        raise ValueError("NEEDS_APPROVAL: approval expired")
    token_payload = {**expected,
        "approval_id": approval["approval_id"],
        "approver_id": approval["approver_id"],
        "nonce": approval["nonce"],
        "expires_at": approval["expires_at"],
        "event_id": request.get("event_id"),
    }
    signature = hmac.new(gateway_key, _canonical(token_payload), hashlib.sha256).digest()
    return _b64(_canonical(token_payload)) + "." + _b64(signature)


class SQLiteLedger:
    """Atomic nonce, event-id and rate-limit ledger."""
    def __init__(self, connection=None):
        self.connection = connection or sqlite3.connect(":memory:", isolation_level=None, check_same_thread=False)
        self.lock = threading.Lock()
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS nonces (
                nonce TEXT PRIMARY KEY, event_id TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY, request_hash TEXT NOT NULL,
                status TEXT NOT NULL, created_at TEXT NOT NULL, receipt_json TEXT
            );
        """)

    def reserve(self, *, event_id, nonce, request_hash, actor_id, tool,
                now, rate_limit, rate_window_seconds):
        now_dt = _parse_time(now)
        cutoff = (now_dt - timedelta(seconds=rate_window_seconds)).isoformat()
        with self.lock:
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self.connection.execute(
                    "SELECT request_hash,status,receipt_json FROM events WHERE event_id=?",
                    (event_id,),
                ).fetchone()
                if existing:
                    self.connection.execute("COMMIT")
                    if existing[0] != request_hash:
                        return "EVENT_ID_CONFLICT", None
                    return "IDEMPOTENT_REPLAY", json.loads(existing[2]) if existing[2] else None
                used = self.connection.execute(
                    "SELECT event_id FROM nonces WHERE nonce=?", (nonce,)
                ).fetchone()
                if used:
                    self.connection.execute("ROLLBACK")
                    return "AUTH_REPLAY", None
                # Rate events are kept in a dedicated table to avoid reading payloads.
                self.connection.execute("""
                    CREATE TABLE IF NOT EXISTS rate_events (
                        actor_id TEXT NOT NULL, tool TEXT NOT NULL, created_at TEXT NOT NULL
                    )
                """)
                recent = self.connection.execute(
                    "SELECT COUNT(*) FROM rate_events WHERE actor_id=? AND tool=? AND created_at>=?",
                    (actor_id, tool, cutoff),
                ).fetchone()[0]
                if recent >= rate_limit:
                    self.connection.execute("ROLLBACK")
                    return "RATE_LIMITED", None
                self.connection.execute(
                    "INSERT INTO nonces(nonce,event_id,created_at) VALUES(?,?,?)",
                    (nonce, event_id, now),
                )
                self.connection.execute(
                    "INSERT INTO events(event_id,request_hash,status,created_at,receipt_json) VALUES(?,?,?,?,NULL)",
                    (event_id, request_hash, "RESERVED", now),
                )
                self.connection.execute(
                    "INSERT INTO rate_events(actor_id,tool,created_at) VALUES(?,?,?)",
                    (actor_id, tool, now),
                )
                self.connection.execute("COMMIT")
                return "RESERVED", None
            except Exception:
                self.connection.execute("ROLLBACK")
                raise

    def finish(self, event_id, status, receipt):
        with self.lock:
            self.connection.execute(
                "UPDATE events SET status=?, receipt_json=? WHERE event_id=?",
                (status, json.dumps(receipt, ensure_ascii=False, sort_keys=True), event_id),
            )

    def status(self, event_id):
        row = self.connection.execute(
            "SELECT status,receipt_json FROM events WHERE event_id=?", (event_id,)
        ).fetchone()
        return None if not row else {"status": row[0], "receipt": json.loads(row[1]) if row[1] else None}


class ToolGateway:
    def __init__(self, *, gateway_key, ledger=None, allowlist=None,
                 rate_limit=DEFAULT_RATE_LIMIT, rate_window_seconds=DEFAULT_RATE_WINDOW_SECONDS,
                 max_input_bytes=MAX_INPUT_BYTES):
        if not isinstance(gateway_key, bytes) or len(gateway_key) < 32:
            raise ValueError("gateway_key deve ter ao menos 32 bytes")
        self.gateway_key = gateway_key
        self.ledger = ledger or SQLiteLedger()
        self.allowlist = set(allowlist or ())
        self.rate_limit = rate_limit
        self.rate_window_seconds = rate_window_seconds
        self.max_input_bytes = max_input_bytes

    def _receipt(self, request, decision, reasons, **extra):
        return {
            "run_id": request.get("run_id"),
            "event_id": request.get("event_id"),
            "decision": decision,
            "reason_codes": reasons,
            "policy_sha": request.get("policy_sha"),
            "source_refs": [request.get("source_set_sha")] if request.get("source_set_sha") else [],
            "action_hash": action_hash(request),
            "effect_performed": False,
            **extra,
        }

    def execute(self, request, token, *, current_state_revision, current_policy_sha,
                current_authorization_epoch, caller_identity, adapter,
                dependency_status="READY", now=None):
        now = now or datetime.now(timezone.utc)
        if not isinstance(request, dict) or not isinstance(request.get("parameters"), dict):
            receipt = self._receipt(request if isinstance(request, dict) else {}, "DENIED", ["INVALID_REQUEST"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        if len(_canonical(request)) > self.max_input_bytes:
            receipt = self._receipt(request, "DENIED", ["INPUT_TOO_LARGE"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        required = ("event_id", "actor_id", "tool", "recipient", "policy_sha",
                    "state_revision", "run_id", "proposal_hash", "source_set_sha",
                    "output_kind", "authorization_epoch")
        if any(request.get(field) in (None, "") for field in required):
            missing_source = not request.get("source_set_sha") or not request.get("proposal_hash")
            decision = "NEEDS_EVIDENCE" if missing_source else "DENIED"
            code = "SOURCE_OR_PROPOSAL_MISSING" if missing_source else "REQUEST_BINDING_MISSING"
            receipt = self._receipt(request, decision, [code])
            return {"status": decision, "exit_code": EXIT_CODES[decision], "receipt": receipt}
        if caller_identity != "trusted_supervisor":
            receipt = self._receipt(request, "DENIED", ["CALLER_NOT_AUTHORIZED"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        if dependency_status != "READY":
            receipt = self._receipt(request, "DEPENDENCY_FAILED", ["DEPENDENCY_FAILED"])
            return {"status": "DEPENDENCY_FAILED", "exit_code": EXIT_CODES["DEPENDENCY_FAILED"], "receipt": receipt}
        if request.get("tool") not in self.allowlist:
            receipt = self._receipt(request, "DENIED", ["TOOL_NOT_AUTHORIZED"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        if request.get("policy_sha") != current_policy_sha:
            receipt = self._receipt(request, "DENIED", ["POLICY_MISMATCH"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        if request.get("state_revision") != current_state_revision:
            receipt = self._receipt(request, "STALE_STATE", ["STALE_STATE"])
            return {"status": "STALE_STATE", "exit_code": EXIT_CODES["STALE_STATE"], "receipt": receipt}
        if request.get("authorization_epoch") != current_authorization_epoch:
            receipt = self._receipt(request, "DENIED", ["AUTHORIZATION_REVOKED"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        try:
            encoded, signature = token.split(".", 1)
            payload = json.loads(_unb64(encoded))
            expected = hmac.new(self.gateway_key, _canonical(payload), hashlib.sha256).digest()
            if not hmac.compare_digest(expected, _unb64(signature)):
                raise ValueError("signature")
        except Exception:
            receipt = self._receipt(request, "DENIED", ["INVALID_TOKEN"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        expected_fields = {
            "actor_id": request.get("actor_id"),
            "tool": request.get("tool"),
            "recipient": request.get("recipient"),
            "action_hash": action_hash(request),
            "policy_sha": request.get("policy_sha"),
            "state_revision": request.get("state_revision"),
            "run_id": request.get("run_id"),
            "proposal_hash": request.get("proposal_hash"),
            "source_set_sha": request.get("source_set_sha"),
            "output_kind": request.get("output_kind"),
            "authorization_epoch": request.get("authorization_epoch"),
            "event_id": request.get("event_id"),
        }
        if any(payload.get(k) != v for k, v in expected_fields.items()):
            receipt = self._receipt(request, "DENIED", ["AUTH_MISMATCH"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        try:
            if _parse_time(payload["expires_at"]) <= now:
                raise ValueError("expired")
        except Exception:
            receipt = self._receipt(request, "DENIED", ["TOKEN_EXPIRED"])
            return {"status": "DENIED", "exit_code": EXIT_CODES["DENIED"], "receipt": receipt}
        if not payload.get("approval_id") or not payload.get("approver_id"):
            receipt = self._receipt(request, "NEEDS_APPROVAL", ["APPROVAL_BINDING_MISSING"])
            return {"status": "NEEDS_APPROVAL", "exit_code": EXIT_CODES["NEEDS_APPROVAL"], "receipt": receipt}

        now_iso = now.isoformat()
        request_hash = _sha(request)
        reservation, previous = self.ledger.reserve(
            event_id=request["event_id"], nonce=payload["nonce"],
            request_hash=request_hash, actor_id=request["actor_id"],
            tool=request["tool"], now=now_iso,
            rate_limit=self.rate_limit, rate_window_seconds=self.rate_window_seconds,
        )
        if reservation == "IDEMPOTENT_REPLAY":
            receipt = previous or self._receipt(request, "UNCONFIRMED", ["REPLAY_NO_READBACK"])
            return {"status": receipt["decision"], "exit_code": EXIT_CODES.get(receipt["decision"], 3),
                    "receipt": receipt, "replayed": True}
        if reservation != "RESERVED":
            decision = "DENIED"
            code = "AUTH_REPLAY" if reservation == "AUTH_REPLAY" else reservation
            receipt = self._receipt(request, decision, [code])
            return {"status": decision, "exit_code": EXIT_CODES[decision], "receipt": receipt}

        try:
            if not callable(adapter):
                raise RuntimeError("DEPENDENCY_FAILED")
            result = adapter(request["parameters"])
            receipt = self._receipt(request, "COMMITTED", [], result_hash=_sha(result))
            receipt["effect_performed"] = True
            self.ledger.finish(request["event_id"], "COMMITTED", receipt)
            return {"status": "COMMITTED", "exit_code": EXIT_CODES["COMMITTED"],
                    "receipt": receipt, "result": result, "replayed": False}
        except TimeoutError:
            receipt = self._receipt(request, "UNCONFIRMED", ["TIMEOUT_NO_READBACK"])
            self.ledger.finish(request["event_id"], "UNCONFIRMED", receipt)
            return {"status": "UNCONFIRMED", "exit_code": EXIT_CODES["UNCONFIRMED"],
                    "receipt": receipt, "replayed": False}
        except Exception:
            receipt = self._receipt(request, "UNCONFIRMED", ["EXECUTION_RESULT_UNKNOWN"])
            self.ledger.finish(request["event_id"], "UNCONFIRMED", receipt)
            return {"status": "UNCONFIRMED", "exit_code": EXIT_CODES["UNCONFIRMED"],
                    "receipt": receipt, "replayed": False}
