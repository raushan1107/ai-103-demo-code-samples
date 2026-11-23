"""Mock-based configuration validation. No Azure calls are made."""

import unittest
import sys
from pathlib import Path
from unittest.mock import ANY, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Settings
from app.services.translation import translate


class ServiceTests(unittest.TestCase):
    @patch("app.services.translation.TextTranslationClient")
    def test_translate_requires_target_language(self, client) -> None:
        with self.assertRaises(ValueError):
            translate("hello", [], "en", Settings(translator_key="key", translator_region="eastus"))
        client.assert_not_called()

    @patch("app.services.translation.TextTranslationClient")
    def test_translate_returns_all_targets(self, client_type) -> None:
        instance = client_type.return_value
        item = type("Translation", (), {"to":"hi", "text":"नमस्ते"})()
        result = type("Result", (), {"translations":[item]})()
        instance.translate.return_value = [result]
        settings = Settings(translator_key="key", translator_region="eastus")
        self.assertEqual(translate("hello", ["hi"], "en", settings), [{"language":"hi","text":"नमस्ते"}])
        client_type.assert_called_once_with(endpoint=settings.translator_endpoint, credential=ANY, region="eastus")
        instance.close.assert_called_once()

    def test_foundry_agent_requires_endpoint_and_deployment(self) -> None:
        from app.agents.foundry_agent import respond

        with self.assertRaisesRegex(RuntimeError, "GC_FOUNDRY_PROJECT_ENDPOINT"):
            respond("synthetic", Settings(project_endpoint="", model_deployment=""))

    def test_error_classification_keeps_request_id(self) -> None:
        from app.diagnostics import classify_error

        class Response:
            headers = {"x-ms-request-id": "synthetic-request-id"}

        class Forbidden(Exception):
            status_code = 403
            response = Response()

        result = classify_error(Forbidden("role missing"))
        self.assertEqual(result["classification"], "Authorization/RBAC failure")
        self.assertEqual(result["request_id"], "synthetic-request-id")

    @patch("app.services.workflow.foundry_respond", return_value=("Reception is open 08:00–18:00.", [{"tool":"get_opening_hours"}]))
    @patch("app.services.workflow.analyze")
    def test_integrated_english_flow_uses_redacted_input(self, analyze_mock, agent_mock) -> None:
        from app.services.workflow import run_integrated
        from app.tools.knowledge_base import KnowledgeBase

        analyze_mock.return_value = {"language":{"code":"en"}, "redacted_text":"My name is ********."}
        result = run_integrated("My name is Asha Rao.", Settings(), KnowledgeBase())
        agent_mock.assert_called_once()
        self.assertEqual(agent_mock.call_args.args[0], "My name is ********.")
        self.assertEqual(result["answer"], "Reception is open 08:00–18:00.")
        self.assertEqual(result["stages"][-1]["tools"], [{"tool":"get_opening_hours"}])


if __name__ == "__main__":
    unittest.main()
