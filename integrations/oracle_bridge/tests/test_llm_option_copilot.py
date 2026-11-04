"""LLM-ALT-01: opção Copilot SDK documentada, mas incapaz de sair do modo OFF.

Sem instalar/importar SDK, sem autenticação, sem chaves reais, sem HTTP.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from bridge.agents import configured_agent, GeminiAgentBridge
from bridge.gateway import Store


class CopilotCandidateSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(str(Path(self.tmp.name) / "llm-options.sqlite3"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_copilot_cannot_activate_even_with_multiple_fake_tokens(self):
        vars = {
            "UFMS_LLM_ENABLED": "1",
            "UFMS_LLM_PROVIDER": "copilot_sdk",
            "COPILOT_GITHUB_TOKEN": "test-placeholder",
            "GH_TOKEN": "test-placeholder",
            "GITHUB_TOKEN": "test-placeholder",
            "UFMS_COPILOT_ENABLED": "1",
        }
        with patch.dict(os.environ, vars, clear=True):
            self.assertIsNone(configured_agent(self.store))

    def test_copilot_alias_and_byok_fail_closed(self):
        for provider in ("copilot", "github-copilot", "copilot_sdk", "byok"):
            vars = {
                "UFMS_LLM_ENABLED": "1",
                "UFMS_LLM_PROVIDER": provider,
                "UFMS_GEMINI_API_KEY": "test-placeholder",
                "UFMS_GEMINI_FREE_PROJECT_ATTESTED": "1",
                "UFMS_GEMINI_PRIVACY_REVIEWED": "1",
                "UFMS_GEMINI_MODEL": "gemini-3.5-flash-lite",
            }
            with self.subTest(provider=provider), patch.dict(os.environ, vars, clear=True):
                self.assertIsNone(configured_agent(self.store))

    def test_existing_gemini_candidate_remains_separately_selectable(self):
        vars = {
            "UFMS_LLM_ENABLED": "1",
            "UFMS_LLM_PROVIDER": "gemini",
            "UFMS_GEMINI_API_KEY": "test-placeholder",
            "UFMS_GEMINI_FREE_PROJECT_ATTESTED": "1",
            "UFMS_GEMINI_PRIVACY_REVIEWED": "1",
            "UFMS_GEMINI_MODEL": "gemini-3.5-flash-lite",
        }
        with patch.dict(os.environ, vars, clear=True):
            self.assertIsInstance(configured_agent(self.store), GeminiAgentBridge)

    def test_neither_candidate_is_enabled_without_explicit_switch(self):
        with patch.dict(os.environ, {
            "UFMS_LLM_PROVIDER": "copilot_sdk",
            "COPILOT_GITHUB_TOKEN": "test-placeholder",
        }, clear=True):
            self.assertIsNone(configured_agent(self.store))


if __name__ == "__main__":
    unittest.main()
