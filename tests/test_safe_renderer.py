"""Adversarial C26 tests: output tokens, release replay and no per-message user approval."""
import copy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from safe_renderer import (
    LocalPreviewSink, OutputAuthority, SafeRenderer, SharedLedger, proposal_hash,
)

SECRET = b"unit-test-key-not-a-deployment-secret-123456789"
NOW = 1730000000


def proposal():
    return {"text": "Revisar o item 10.2 do edital.", "effect_kind": "NONE",
            "output_kind": "ORIENTACAO"}


def context():
    return {"run_id": "run-01", "policy_sha": "p" * 40,
            "state_revision": "rev-7", "source_set_sha": "s" * 40,
            "actor_role": "Tutor", "channel": "local_preview",
            "recipient": "owner-only", "output_kind": "ORIENTACAO"}


def gate(p, c):
    return {"decision": "ALLOW", "effect_kind": "NONE",
            "proposal_hash": proposal_hash(p), "run_id": c["run_id"],
            "policy_sha": c["policy_sha"],
            "state_revision": c["state_revision"],
            "source_set_sha": c["source_set_sha"],
            "actor_role": c["actor_role"]}


class C26SafeRendererTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db = str(Path(temp.name) / "shared-releases.sqlite")
        self.ledger = SharedLedger(self.db)
        self.sink = LocalPreviewSink()
        self.authority = OutputAuthority(SECRET, self.ledger)
        self.renderer = SafeRenderer(SECRET, self.ledger, self.sink)
        self.p = proposal()
        self.c = context()

    def signed(self, p=None, c=None, receipt=None):
        p = self.p if p is None else p
        c = self.c if c is None else c
        return self.authority.issue(p, c, gate(p, c) if receipt is None else receipt,
                                    now=NOW, ttl=60)

    def denied(self, p=None, c=None, token=None, now=NOW):
        p = self.p if p is None else p
        c = self.c if c is None else c
        ret = self.renderer.render(p, c, token, now=now)
        self.assertEqual(ret["decision"], "DENY", ret)
        self.assertEqual(ret["local_emissions"], 0)
        self.assertEqual(self.sink.messages, [])

    def test_automatic_tutor_orientation_no_human_approval(self):
        token = self.signed()
        self.assertIsNotNone(token)
        self.assertNotIn("approver_id", token["body"])
        result = self.renderer.render(self.p, self.c, token, now=NOW)
        self.assertEqual(result["decision"], "COMPLETE")
        self.assertEqual(self.sink.messages, [self.p["text"]])

    def test_automatic_coach_orientation(self):
        c = dict(self.c, actor_role="Coach")
        self.assertEqual(
            self.renderer.render(self.p, c, self.signed(c=c), now=NOW)["decision"],
            "COMPLETE",
        )

    def test_missing_or_forged_token_denied(self):
        for token in (None, {}, {"body": {}, "mac": "0" * 64}, "fake-token"):
            with self.subTest(token=token):
                self.denied(token=token)

    def test_tampered_body_mac_or_unknown_key_denied(self):
        original = self.signed()
        for mutate in (
            lambda t: t["body"].__setitem__("recipient", "outsider"),
            lambda t: t.__setitem__("mac", "0" * 64),
            lambda t: t["body"].__setitem__("extra", "payload"),
            lambda t: t.__setitem__("extra", "payload"),
        ):
            token = copy.deepcopy(original)
            mutate(token)
            with self.subTest(token=token):
                self.denied(token=token)

    def test_changes_of_all_bound_context_fields_denied(self):
        replacement = {
            "run_id": "run-02", "policy_sha": "q" * 40,
            "state_revision": "rev-8", "source_set_sha": "t" * 40,
            "actor_role": "Coach", "channel": "zapia",
            "recipient": "third-party", "output_kind": "TOOL",
        }
        token = self.signed()
        for key, value in replacement.items():
            with self.subTest(key=key):
                self.denied(c=dict(self.c, **{key: value}), token=token)

    def test_changed_text_after_authorization_denied(self):
        token = self.signed()
        changed = dict(self.p, text="A prova não tem exigência mínima.")
        self.denied(p=changed, token=token)

    def test_tool_output_and_external_channel_never_issued(self):
        for p, c in (
            (dict(self.p, effect_kind="TOOL"), self.c),
            (dict(self.p, output_kind="TOOL"), self.c),
            (self.p, dict(self.c, channel="zapia")),
            (self.p, dict(self.c, recipient="")),
            (self.p, dict(self.c, actor_role="anonymous")),
        ):
            with self.subTest(proposal=p, context=c):
                self.assertIsNone(self.signed(p=p, c=c))

    def test_gate_must_be_exact_allow_none_from_trusted_caller(self):
        for receipt in (
            {},
            dict(gate(self.p, self.c), decision="NEEDS_EVIDENCE"),
            dict(gate(self.p, self.c), effect_kind="TOOL"),
            dict(gate(self.p, self.c), policy_sha="z" * 40),
            dict(gate(self.p, self.c), injected_approval="yes"),
        ):
            with self.subTest(receipt=receipt):
                self.assertIsNone(self.signed(receipt=receipt))

    def test_missing_token_does_not_call_sink(self):
        self.denied()

    def test_replay_same_token_denied_after_one_local_emission(self):
        token = self.signed()
        first = self.renderer.render(self.p, self.c, token, now=NOW)
        second = self.renderer.render(self.p, self.c, token, now=NOW)
        self.assertEqual(first["decision"], "COMPLETE")
        self.assertEqual(second["decision"], "DENY")
        self.assertEqual(self.sink.messages, [self.p["text"]])

    def test_expiration_exact_boundary(self):
        token = self.signed()
        self.denied(token=token, now=NOW + 60)

    def test_epoch_revocation_without_state_revision_change(self):
        token = self.signed()
        self.ledger.advance_epoch()
        self.denied(token=token)

    def test_explicit_release_revocation_denied(self):
        token = self.signed()
        self.ledger.revoke(token["body"]["release_id"])
        self.denied(token=token)

    def test_parallel_renderers_share_atomic_nonce_reservation(self):
        token = self.signed()
        other_sink = LocalPreviewSink()
        other_renderer = SafeRenderer(SECRET, SharedLedger(self.db), other_sink)
        def attempt(renderer):
            return renderer.render(self.p, self.c, token, now=NOW)["decision"]
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, (self.renderer, other_renderer)))
        self.assertCountEqual(results, ["COMPLETE", "DENY"])
        self.assertEqual(len(self.sink.messages) + len(other_sink.messages), 1)

    def test_suspected_transport_delivery_no_blind_retry(self):
        class AmbiguousSink:
            def __init__(self):
                self.messages = []
            def emit(self, text):
                self.messages.append(text)
                raise RuntimeError("readback lost after local effect")
        sink = AmbiguousSink()
        renderer = SafeRenderer(SECRET, self.ledger, sink)
        token = self.signed()
        first = renderer.render(self.p, self.c, token, now=NOW)
        self.assertEqual(first["decision"], "UNCONFIRMED")
        self.assertFalse(first["retry_allowed"])
        second = renderer.render(self.p, self.c, token, now=NOW)
        self.assertEqual(second["decision"], "DENY")
        self.assertEqual(sink.messages, [self.p["text"]])

    def test_wrong_signing_key_rejected(self):
        renderer = SafeRenderer(b"different-signing-key-1234567890123456", self.ledger, self.sink)
        ret = renderer.render(self.p, self.c, self.signed(), now=NOW)
        self.assertEqual(ret["decision"], "DENY")
        self.assertEqual(self.sink.messages, [])

    def test_different_release_can_emit_separately(self):
        one = self.signed()
        two = self.signed()
        self.assertEqual(self.renderer.render(self.p, self.c, one, now=NOW)["decision"], "COMPLETE")
        self.assertEqual(self.renderer.render(self.p, self.c, two, now=NOW)["decision"], "COMPLETE")
        self.assertEqual(len(self.sink.messages), 2)

    def test_malformed_proposal_and_overlarge_text_denied(self):
        for p in (
            {"text": "", "effect_kind": "NONE", "output_kind": "ORIENTACAO"},
            {"text": "a" * 65537, "effect_kind": "NONE", "output_kind": "ORIENTACAO"},
            dict(self.p, hidden_direct_tool_call="send"),
            {"text": "help", "effect_kind": "TOOL", "output_kind": "ORIENTACAO"},
        ):
            with self.subTest(proposal=str(p)[:70]):
                self.assertIsNone(self.signed(p=p))


if __name__ == "__main__":
    unittest.main()
