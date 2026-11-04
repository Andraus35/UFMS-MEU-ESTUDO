"""Testes offline: Gemini Developer API sem API key real ou tráfego externo."""
import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from bridge.agents import GeminiAgentBridge, configured_agent
from bridge.gateway import Store


class Reply:
    def __init__(self, result):
        self.data = json.dumps(result).encode()

    def __enter__(self):
        return io.BytesIO(self.data)

    def __exit__(self, *args):
        return False


class GeminiPoCTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(str(Path(self.temp.name) / "poc.sqlite"))
        self.now = datetime(2026, 11, 4, tzinfo=timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def agent(self, limit=10):
        return GeminiAgentBridge("synthetic-not-real", "gemini-3.5-flash-lite",
                                 self.store, max_per_day=limit)

    def consent(self, gemini=True, general=True):
        with self.store.connect() as db:
            for key, allowed in [("llm_consent", general),
                                 ("gemini_data_consent", gemini)]:
                db.execute("""INSERT INTO settings(key,value) VALUES(?,?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                    (key, "1" if allowed else "0"))

    def test_default_off_and_openai_paid_not_selected(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(configured_agent(self.store))
        with patch.dict(os.environ, {
            "UFMS_LLM_ENABLED":"1", "UFMS_LLM_PROVIDER":"openai",
            "UFMS_OPENAI_API_KEY":"fake", "UFMS_OPENAI_MODEL":"some-model"
        }, clear=True):
            self.assertIsNone(configured_agent(self.store))

    def test_missing_attestation_blocks_agent(self):
        env={"UFMS_LLM_ENABLED":"1", "UFMS_LLM_PROVIDER":"gemini",
             "UFMS_GEMINI_API_KEY":"synthetic", "UFMS_GEMINI_MODEL":"gemini-3.5-flash-lite"}
        with patch.dict(os.environ,env,clear=True):
            self.assertIsNone(configured_agent(self.store))
            os.environ["UFMS_GEMINI_FREE_PROJECT_ATTESTED"]="1"
            self.assertIsNone(configured_agent(self.store))
            os.environ["UFMS_GEMINI_PRIVACY_REVIEWED"]="1"
            self.assertIsInstance(configured_agent(self.store),GeminiAgentBridge)

    def test_only_free_allowlisted_model(self):
        with self.assertRaises(ValueError):
            GeminiAgentBridge("fake", "arbitrary-paid-model", self.store)
        env={"UFMS_LLM_ENABLED":"1", "UFMS_LLM_PROVIDER":"gemini",
             "UFMS_GEMINI_API_KEY":"fake", "UFMS_GEMINI_MODEL":"not-confirmed-free",
             "UFMS_GEMINI_FREE_PROJECT_ATTESTED":"1","UFMS_GEMINI_PRIVACY_REVIEWED":"1"}
        with patch.dict(os.environ,env,clear=True):
            self.assertIsNone(configured_agent(self.store))

    def test_legacy_consent_does_not_authorize_google(self):
        self.consent(gemini=False, general=True)
        agent=self.agent()
        with patch("bridge.agents.request.urlopen") as outbound:
            reply=agent.answer("tutor","Questão sintética","tutor:1",now=self.now)
            outbound.assert_not_called()
        self.assertIn("/ativar_gemini",reply)

    def test_specific_consent_required_transactionally(self):
        self.consent(gemini=True, general=False)
        with patch("bridge.agents.request.urlopen") as outbound:
            reply=self.agent().answer("tutor","Questão","tutor:2",now=self.now)
            outbound.assert_not_called()
        self.assertIn("/ativar_ia",reply)

    def test_schema_roles_no_model_tools(self):
        agent=self.agent()
        tutor=agent._make_payload("tutor","Questão pública?")
        coach=agent._make_payload("coach","Como estudar?")
        self.assertIn("Tutor UFMS",tutor["systemInstruction"]["parts"][0]["text"])
        self.assertIn("Coach UFMS",coach["systemInstruction"]["parts"][0]["text"])
        self.assertEqual(tutor["contents"][0]["role"],"user")
        for forbidden in ("tools","store","googleSearch","functionDeclarations"):
            self.assertNotIn(forbidden,tutor)

    def test_synthetic_http_round_trip_and_key_only_in_header(self):
        self.consent()
        ok={"candidates":[{"finishReason":"STOP","content":{
            "parts":[{"text":"Resposta simulada"}]}}]}
        with patch("bridge.agents.request.urlopen",return_value=Reply(ok)) as outbound:
            self.assertEqual(self.agent().answer("tutor","Pergunta pública",
                                                "tutor:3",now=self.now),
                             "Resposta simulada")
        req=outbound.call_args.args[0]
        self.assertTrue(req.full_url.endswith("gemini-3.5-flash-lite:generateContent"))
        self.assertNotIn("synthetic-not-real",req.full_url)
        self.assertEqual(req.get_header("X-goog-api-key"),"synthetic-not-real")
        body=json.loads(req.data)
        self.assertEqual(body["contents"][0]["parts"][0]["text"],"Pergunta pública")

    def test_quota_shared_and_replay(self):
        self.consent()
        ok={"candidates":[{"finishReason":"STOP","content":{
            "parts":[{"text":"ok"}]}}]}
        agent=self.agent(limit=1)
        with patch("bridge.agents.request.urlopen",return_value=Reply(ok)) as outbound:
            self.assertEqual(agent.answer("tutor","Olá","tutor:5",now=self.now),"ok")
            self.assertIn("já foi processada",
                          agent.answer("tutor","Olá","tutor:5",now=self.now))
            self.assertIn("Limite diário",
                          agent.answer("coach","Olá","coach:6",now=self.now))
            self.assertEqual(outbound.call_count,1)

    def test_429_does_not_leak_key_or_retry(self):
        self.consent()
        http=HTTPError("https://generativelanguage.googleapis.com",
                       429,"RESOURCE_EXHAUSTED",{},io.BytesIO(b""))
        with patch("bridge.agents.request.urlopen",side_effect=http) as outbound:
            with self.assertRaises(RuntimeError) as cm:
                self.agent().answer("tutor","Olá","tutor:8",now=self.now)
            self.assertEqual(outbound.call_count,1)
        self.assertNotIn("synthetic-not-real",str(cm.exception))

    def test_no_hallucinated_response_on_empty_or_blocked(self):
        agent=self.agent()
        for result in ({"candidates":[]},
                       {"candidates":[{"finishReason":"SAFETY",
                                       "content":{"parts":[{"text":"blocked"}]}}]},
                       {"candidates":[{"finishReason":"STOP","content":{"parts":[]}}]}):
            with self.assertRaises(RuntimeError):
                agent.extract_text(result)

    def test_revocation_prevents_new_send(self):
        self.consent()
        self.consent(gemini=False)
        with patch("bridge.agents.request.urlopen") as outbound:
            self.assertIn("/ativar_gemini",
                          self.agent().answer("coach","Olá","coach:9",now=self.now))
            outbound.assert_not_called()


if __name__=="__main__":
    unittest.main()
