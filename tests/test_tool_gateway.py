"""Adversarial offline tests for authorization, replay and fail-closed execution."""
import sys
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from tool_gateway import (
    ToolGateway, SQLiteLedger, sign_approval_receipt, issue_authorization,
    action_hash, EXIT_CODES,
)

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
APPROVAL_KEY = b"a" * 32
GATEWAY_KEY = b"g" * 32


def request(event_id="evt-1", nonce="nonce-1", text="hello"):
    return {
        "event_id": event_id, "actor_id": "llm-session-7",
        "tool": "send_message", "recipient": "zapia:private-chat",
        "parameters": {"text": text}, "policy_sha": "b" * 64,
        "state_revision": "rev-12", "run_id": "run-3",
        "proposal_hash": "c" * 64, "source_set_sha": "d" * 64,
        "output_kind": "MESSAGE", "authorization_epoch": 4,
    }


def token_for(req, *, nonce=None, expires="2026-11-05T12:01:00+00:00"):
    payload = {
        "approval_id": "approval-" + req["event_id"],
        "approver_id": "human-supervisor-1", "approved": True,
        "actor_id": req["actor_id"], "tool": req["tool"],
        "recipient": req["recipient"], "action_hash": action_hash(req),
        "policy_sha": req["policy_sha"], "state_revision": req["state_revision"],
        "run_id": req["run_id"], "proposal_hash": req["proposal_hash"],
        "source_set_sha": req["source_set_sha"], "output_kind": req["output_kind"],
        "authorization_epoch": req["authorization_epoch"],
        "nonce": nonce or ("nonce-" + req["event_id"]), "expires_at": expires,
    }
    approval = sign_approval_receipt(payload, APPROVAL_KEY)
    return issue_authorization(req, approval, approval_key=APPROVAL_KEY,
                               gateway_key=GATEWAY_KEY, now=NOW)


def gateway(**kwargs):
    return ToolGateway(gateway_key=GATEWAY_KEY, allowlist={"send_message"}, **kwargs)


class ToolGatewayTests(unittest.TestCase):
    def test_missing_approval_returns_needs_approval_without_call(self):
        calls = []
        result = gateway().execute(request(), None, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "NEEDS_APPROVAL")
        self.assertEqual(result["exit_code"], 2)
        self.assertEqual(calls, [])

    def test_approval_binds_actor_tool_recipient_parameters_and_policy(self):
        req = request()
        tok = token_for(req)
        calls = []
        result = gateway().execute(req, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p) or {"ok": True},
            now=NOW)
        self.assertEqual(result["status"], "COMMITTED")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(len(calls), 1)
        self.assertTrue(result["receipt"]["effect_performed"])

    def test_altered_recipient_rejected_before_call(self):
        req = request()
        tok = token_for(req)
        changed = dict(req, recipient="zapia:other-chat")
        calls = []
        result = gateway().execute(changed, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertIn("AUTH_MISMATCH", result["receipt"]["reason_codes"])
        self.assertEqual(calls, [])

    def test_altered_parameters_rejected_before_call(self):
        req = request()
        tok = token_for(req)
        changed = request(text="changed after approval")
        calls = []
        result = gateway().execute(changed, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertEqual(calls, [])

    def test_invalid_approval_signature_rejected(self):
        req = request()
        approval = sign_approval_receipt({
            "approval_id": "a", "approver_id": "human", "approved": True,
        }, APPROVAL_KEY)
        approval["signature"] = "invalid"
        with self.assertRaisesRegex(ValueError, "invalid approval signature"):
            issue_authorization(req, approval, approval_key=APPROVAL_KEY,
                                gateway_key=GATEWAY_KEY, now=NOW)

    def test_actor_cannot_approve_own_action(self):
        req = request()
        payload = {
            "approval_id": "a", "approver_id": req["actor_id"], "approved": True,
            "actor_id": req["actor_id"], "tool": req["tool"], "recipient": req["recipient"],
            "action_hash": action_hash(req), "policy_sha": req["policy_sha"],
            "state_revision": req["state_revision"], "run_id": req["run_id"],
            "proposal_hash": req["proposal_hash"], "source_set_sha": req["source_set_sha"],
            "output_kind": req["output_kind"], "authorization_epoch": req["authorization_epoch"],
            "nonce": "n", "expires_at": "2026-11-05T12:01:00+00:00",
        }
        approval = sign_approval_receipt(payload, APPROVAL_KEY)
        with self.assertRaisesRegex(ValueError, "approver and actor must differ"):
            issue_authorization(req, approval, approval_key=APPROVAL_KEY,
                                gateway_key=GATEWAY_KEY, now=NOW)

    def test_expired_token_rejected(self):
        req = request()
        tok = token_for(req, expires="2026-11-05T11:59:00+00:00")
        calls = []
        result = gateway().execute(req, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertIn("TOKEN_EXPIRED", result["receipt"]["reason_codes"])
        self.assertEqual(calls, [])

    def test_direct_caller_bypass_denied(self):
        req = request()
        calls = []
        result = gateway().execute(req, token_for(req), current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="llm_direct", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertIn("CALLER_NOT_AUTHORIZED", result["receipt"]["reason_codes"])
        self.assertEqual(calls, [])

    def test_tool_outside_allowlist_denied(self):
        req = request()
        req["tool"] = "delete_account"
        tok = token_for(req)
        calls = []
        result = gateway().execute(req, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertIn("TOOL_NOT_AUTHORIZED", result["receipt"]["reason_codes"])
        self.assertEqual(calls, [])

    def test_stale_state_denied(self):
        req = request()
        calls = []
        result = gateway().execute(req, token_for(req), current_state_revision="rev-13",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "STALE_STATE")
        self.assertEqual(calls, [])

    def test_policy_mismatch_denied(self):
        req = request()
        calls = []
        result = gateway().execute(req, token_for(req), current_state_revision="rev-12",
            current_policy_sha="e" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertIn("POLICY_MISMATCH", result["receipt"]["reason_codes"])
        self.assertEqual(calls, [])

    def test_revoked_authorization_epoch_denied(self):
        req = request()
        calls = []
        result = gateway().execute(req, token_for(req), current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=5,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertIn("AUTHORIZATION_REVOKED", result["receipt"]["reason_codes"])
        self.assertEqual(calls, [])

    def test_missing_source_proof_needs_evidence(self):
        req = request()
        req["source_set_sha"] = None
        calls = []
        result = gateway().execute(req, None, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "NEEDS_EVIDENCE")
        self.assertEqual(result["exit_code"], 2)
        self.assertEqual(calls, [])

    def test_dependency_failure_precedes_execution(self):
        req = request()
        calls = []
        result = gateway().execute(req, token_for(req), current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p),
            dependency_status="UNAVAILABLE", now=NOW)
        self.assertEqual(result["status"], "DEPENDENCY_FAILED")
        self.assertEqual(result["exit_code"], 3)
        self.assertEqual(calls, [])

    def test_input_over_limit_rejected_before_execution(self):
        req = request(text="x" * 1000)
        calls = []
        result = gateway(max_input_bytes=200).execute(req, token_for(req),
            current_state_revision="rev-12", current_policy_sha="b" * 64,
            current_authorization_epoch=4, caller_identity="trusted_supervisor",
            adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertIn("INPUT_TOO_LARGE", result["receipt"]["reason_codes"])
        self.assertEqual(calls, [])

    def test_idempotent_replay_does_not_repeat_effect(self):
        req = request()
        calls = []
        gw = gateway()
        tok = token_for(req)
        first = gw.execute(req, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p) or {"ok": True}, now=NOW)
        second = gw.execute(req, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p) or {"ok": True}, now=NOW)
        self.assertEqual(first["status"], "COMMITTED")
        self.assertTrue(second["replayed"])
        self.assertEqual(len(calls), 1)

    def test_nonce_replay_with_new_event_id_denied(self):
        first_req = request("evt-a")
        second_req = request("evt-b")
        shared_nonce = "same-nonce"
        first_tok = token_for(first_req, nonce=shared_nonce)
        second_tok = token_for(second_req, nonce=shared_nonce)
        calls = []
        gw = gateway()
        gw.execute(first_req, first_tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        second = gw.execute(second_req, second_tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(second["status"], "DENIED")
        self.assertIn("AUTH_REPLAY", second["receipt"]["reason_codes"])
        self.assertEqual(len(calls), 1)

    def test_rate_limit_is_atomic_and_denies_before_second_call(self):
        calls = []
        gw = gateway(rate_limit=1, rate_window_seconds=60)
        for event_id in ("evt-a", "evt-b"):
            req = request(event_id)
            result = gw.execute(req, token_for(req), current_state_revision="rev-12",
                current_policy_sha="b" * 64, current_authorization_epoch=4,
                caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p), now=NOW)
        self.assertEqual(result["status"], "DENIED")
        self.assertIn("RATE_LIMITED", result["receipt"]["reason_codes"])
        self.assertEqual(len(calls), 1)

    def test_timeout_is_unconfirmed_and_not_retried(self):
        req = request()
        calls = []
        gw = gateway()
        def timeout(_):
            calls.append(1)
            raise TimeoutError()
        tok = token_for(req)
        first = gw.execute(req, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=timeout, now=NOW)
        second = gw.execute(req, tok, current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=timeout, now=NOW)
        self.assertEqual(first["status"], "UNCONFIRMED")
        self.assertEqual(first["exit_code"], 3)
        self.assertTrue(second["replayed"])
        self.assertEqual(len(calls), 1)

    def test_receipt_does_not_include_raw_parameters(self):
        req = request(text="PRIVATE-USER-TEXT")
        result = gateway().execute(req, token_for(req), current_state_revision="rev-12",
            current_policy_sha="b" * 64, current_authorization_epoch=4,
            caller_identity="trusted_supervisor", adapter=lambda p: {"ok": True}, now=NOW)
        self.assertNotIn("PRIVATE-USER-TEXT", str(result["receipt"]))
        self.assertIn("policy_sha", result["receipt"])
        self.assertIn("reason_codes", result["receipt"])

    def test_exit_codes_cover_four_required_classes(self):
        self.assertEqual(EXIT_CODES["COMMITTED"], 0)
        self.assertEqual(EXIT_CODES["DENIED"], 1)
        self.assertEqual(EXIT_CODES["NEEDS_APPROVAL"], 2)
        self.assertEqual(EXIT_CODES["DEPENDENCY_FAILED"], 3)


if __name__ == "__main__":
    unittest.main()
