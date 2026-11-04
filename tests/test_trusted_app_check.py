"""Adversarial offline tests for a distinct, externally hosted GitHub App check."""
import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from trusted_app_check import (
    CHECK_NAME, app_jwt, installation_token, verify_one,
)
from trusted_governance import REPOSITORY

PR, HEAD, BASE = 9, "a"*40, "b"*40
APP_ID = "456789"


class ExternalAppTests(unittest.TestCase):
    def test_generated_jwt_is_cryptographically_verifiable_rsa256(self):
        with tempfile.TemporaryDirectory() as tmp:
            sk, pk = Path(tmp)/"app.pem", Path(tmp)/"pub.pem"
            subprocess.run(["openssl", "genpkey", "-algorithm", "RSA",
                            "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(sk)],
                           capture_output=True, check=True)
            subprocess.run(["openssl", "pkey", "-in", str(sk), "-pubout", "-out",
                            str(pk)], capture_output=True, check=True)
            token = app_jwt(APP_ID, sk, now=1760000000)
            header, payload, signature = token.split(".")
            self.assertEqual(json.loads(base64.urlsafe_b64decode(
                header + "="*(-len(header)%4)))["alg"], "RS256")
            claims = json.loads(base64.urlsafe_b64decode(
                payload + "="*(-len(payload)%4)))
            self.assertEqual(claims["iss"], APP_ID)
            self.assertLessEqual(claims["exp"]-claims["iat"], 600)
            message = (header+"."+payload).encode("ascii")
            rawsig = base64.urlsafe_b64decode(signature+"="*(-len(signature)%4))
            msg, sig = Path(tmp)/"msg", Path(tmp)/"sig"
            msg.write_bytes(message)
            sig.write_bytes(rawsig)
            proc = subprocess.run(["openssl", "dgst", "-sha256", "-verify", str(pk),
                                   "-signature", str(sig), str(msg)],
                                  capture_output=True)
            self.assertEqual(proc.returncode, 0)

    def test_missing_key_or_wrong_app_id_fails(self):
        with self.assertRaises(ValueError):
            app_jwt("not-an-id", "/missing", now=1)
        with self.assertRaises(ValueError):
            app_jwt(APP_ID, "/missing", now=1)

    def test_installation_must_match_app_id_and_scoped_permissions(self):
        seen = []
        def api(method, path, token, payload=None):
            seen.append((method, path, payload))
            if path == "app":
                return {"id": int(APP_ID)}
            if path.endswith("/installation"):
                return {"app_id": int(APP_ID), "id": 123}
            return {"token": "temporary-installation-token"}
        with mock.patch("trusted_app_check.api_json", side_effect=api):
            tok = installation_token("jwt", APP_ID)
        self.assertEqual(tok, "temporary-installation-token")
        self.assertEqual(seen[-1][0], "POST")
        self.assertEqual(seen[-1][2]["repositories"], ["UFMS-MEU-ESTUDO"])
        self.assertEqual(seen[-1][2]["permissions"], {
            "checks": "write", "pull_requests": "read", "issues": "read"})

    def test_wrong_app_identity_rejected(self):
        with mock.patch("trusted_app_check.api_json", return_value={"id": 999}):
            with self.assertRaisesRegex(ValueError, "expected GitHub App"):
                installation_token("jwt", APP_ID)

    def test_success_check_comes_from_separate_app_id(self):
        result, posts = self._simulate()
        self.assertEqual(result["conclusion"], "success")
        self.assertEqual(result["check_name"], CHECK_NAME)
        self.assertEqual(result["app_id"], int(APP_ID))
        self.assertEqual(posts[0]["head_sha"], HEAD)
        self.assertEqual(posts[0]["conclusion"], "success")

    def test_policy_denial_emits_failure_not_success(self):
        result, posts = self._simulate(policy_error=True)
        self.assertEqual(result["conclusion"], "failure")
        self.assertEqual(posts[0]["conclusion"], "failure")

    def test_head_race_forces_failure_check(self):
        result, _ = self._simulate(after_head="0"*40)
        self.assertEqual(result["conclusion"], "failure")

    def test_base_race_forces_failure_check(self):
        result, _ = self._simulate(after_base="0"*40)
        self.assertEqual(result["conclusion"], "failure")

    def test_check_spoofed_app_identity_fails_readback(self):
        with self.assertRaisesRegex(ValueError, "readback identity mismatch"):
            self._simulate(response_app_id=999)

    def test_readback_failure_of_pr_forces_failure(self):
        result, posts = self._simulate(after_read_error=True)
        self.assertEqual(result["conclusion"], "failure")
        self.assertEqual(posts[0]["conclusion"], "failure")

    def test_check_api_unavailable_must_not_claim_success(self):
        with self.assertRaisesRegex(ValueError, "cannot create check"):
            self._simulate(post_error=True)

    def _simulate(self, policy_error=False, after_head=None, after_base=None,
                  response_app_id=None, after_read_error=False, post_error=False):
        first = {"number": PR, "state": "open", "head": {"sha": HEAD},
                 "base": {"ref": "main", "sha": BASE}}
        after = {"number": PR, "state": "open",
                 "head": {"sha": after_head or HEAD},
                 "base": {"ref": "main", "sha": after_base or BASE}}
        hits = 0
        posts = []
        def fake_api(method, path, token, payload=None):
            nonlocal hits
            self.assertEqual(token, "installation")
            self.assertTrue(path.startswith("repos/"+REPOSITORY+"/"))
            if method == "GET":
                hits += 1
                if hits == 2 and after_read_error:
                    raise ValueError("network unavailable")
                return first if hits == 1 else after
            if method == "POST":
                posts.append(payload)
                if post_error:
                    raise ValueError("cannot create check")
                return {"app": {"id": response_app_id or int(APP_ID)},
                        "name": payload["name"], "head_sha": payload["head_sha"],
                        "conclusion": payload["conclusion"]}
            raise AssertionError("Unexpected method")
        with mock.patch("trusted_app_check.api_json", side_effect=fake_api):
            with mock.patch("trusted_app_check.enforce") as policy:
                if policy_error:
                    policy.side_effect = ValueError("no signed authorization")
                return verify_one(PR, "installation", APP_ID, "pubkey"), posts


if __name__ == "__main__":
    unittest.main()
