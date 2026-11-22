import io
import json
import unittest
import urllib.error
from unittest.mock import patch

import config
from analyzer import LEAD_ANALYSIS_SCHEMA, PostAnalyzer
from gemini_client import GeminiAPIError, GeminiClient, GeminiInteraction


class _FakeHTTPResponse:
    def __init__(self, payload, status=200):
        self._body = json.dumps(payload).encode("utf-8")
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestGeminiClient(unittest.TestCase):
    def test_default_model_is_free_tier_friendly(self):
        self.assertEqual(config.GEMINI_MODEL, "gemini-3.5-flash-lite")
        self.assertEqual(config.GEMINI_API_VERSION, "v1")

    def test_create_interaction_sends_v1_rest_request_with_header_auth(self):
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            captured["method"] = req.get_method()
            captured["headers"] = {k.lower(): v for k, v in req.header_items()}
            captured["body"] = json.loads(req.data.decode("utf-8"))
            captured["timeout"] = timeout
            return _FakeHTTPResponse(
                {
                    "id": "v1_test_123",
                    "status": "completed",
                    "model": "gemini-4-hydrogen",
                    "steps": [
                        {"type": "user_input", "content": [{"type": "text", "text": "Hi"}]},
                        {"type": "thought", "summary": "Thinking..."},
                        {
                            "type": "model_output",
                            "content": [
                                {"type": "text", "text": "Hello "},
                                {"type": "text", "text": "ServiceApp!"},
                            ],
                        },
                    ],
                    "usage": {"total_tokens": 25},
                }
            )

        client = GeminiClient(api_key="test-secret-key", default_model="gemini-4-hydrogen")
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            interaction = client.create_interaction(
                input_data="Hi",
                system_instruction="Be concise.",
                store=False,
            )

        self.assertEqual(
            captured["url"],
            "https://generativelanguage.googleapis.com/v1/interactions",
        )
        self.assertNotIn("test-secret-key", captured["url"])
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["headers"]["x-goog-api-key"], "test-secret-key")
        self.assertEqual(captured["headers"]["content-type"], "application/json")
        self.assertEqual(captured["body"]["model"], "gemini-4-hydrogen")
        self.assertEqual(captured["body"]["input"], "Hi")
        self.assertEqual(captured["body"]["system_instruction"], "Be concise.")
        self.assertFalse(captured["body"]["store"])
        self.assertEqual(interaction.id, "v1_test_123")
        self.assertEqual(interaction.output_text, "Hello ServiceApp!")

    def test_output_text_uses_only_trailing_model_output_steps(self):
        interaction = GeminiInteraction(
            {
                "id": "v1_multi",
                "status": "completed",
                "steps": [
                    {"type": "model_output", "content": [{"type": "text", "text": "Earlier "}]},
                    {"type": "google_search_call", "arguments": {"queries": ["test"]}},
                    {"type": "model_output", "content": [{"type": "text", "text": "Final "}]},
                    {"type": "model_output", "content": [{"type": "text", "text": "Answer"}]},
                ],
            }
        )
        self.assertEqual(interaction.output_text, "Final Answer")

    def test_create_structured_json_sets_response_format_schema(self):
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return _FakeHTTPResponse(
                {
                    "id": "v1_json_1",
                    "status": "completed",
                    "steps": [
                        {
                            "type": "model_output",
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(
                                        {
                                            "intent": "SERVICE_SEEKER",
                                            "draft_reply": "Olá! Vale conferir o ServiceApp.",
                                        }
                                    ),
                                }
                            ],
                        }
                    ],
                }
            )

        client = GeminiClient(api_key="test-key")
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            data, interaction = client.create_structured_json(
                input_data="Preciso de encanador",
                schema=LEAD_ANALYSIS_SCHEMA,
                temperature=0.4,
                store=False,
            )

        self.assertEqual(captured["body"]["response_format"]["type"], "text")
        self.assertEqual(captured["body"]["response_format"]["mime_type"], "application/json")
        self.assertEqual(captured["body"]["response_format"]["schema"], LEAD_ANALYSIS_SCHEMA)
        self.assertEqual(captured["body"]["generation_config"]["temperature"], 0.4)
        self.assertEqual(data["intent"], "SERVICE_SEEKER")
        self.assertEqual(interaction.status, "completed")

    def test_create_decision_targets_v1beta_decisions_endpoint(self):
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return _FakeHTTPResponse(
                {
                    "answers": {
                        "is_lead": {"type": "noul", "noul": 0.94, "confidence": 0.91}
                    }
                }
            )

        client = GeminiClient(api_key="test-key")
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            res = client.create_decision(
                input_data="Busco plomero urgente en CDMX",
                questions={
                    "is_lead": {
                        "type": "noul",
                        "instructions": "Is the user looking to hire a local service worker?",
                    }
                },
            )

        self.assertEqual(
            captured["url"],
            "https://generativelanguage.googleapis.com/v1beta/decisions",
        )
        self.assertEqual(captured["body"]["model"], "gemini-decision-1")
        self.assertAlmostEqual(res["answers"]["is_lead"]["noul"], 0.94)

    def test_missing_api_key_raises_clean_error(self):
        client = GeminiClient(api_key="")
        self.assertFalse(client.is_configured())
        with self.assertRaises(GeminiAPIError):
            client.health_check()

    def test_http_error_surfaces_api_message_without_key_leak(self):
        err_payload = json.dumps(
            {"error": {"code": 401, "status": "UNAUTHENTICATED", "message": "API key not valid."}}
        ).encode("utf-8")
        http_err = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1/interactions",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(err_payload),
        )
        client = GeminiClient(api_key="super-secret-value", max_retries=0)
        with patch("urllib.request.urlopen", side_effect=http_err):
            with self.assertRaises(GeminiAPIError) as ctx:
                client.health_check()

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("API key not valid.", str(ctx.exception))
        self.assertNotIn("super-secret-value", str(ctx.exception))

    def test_list_wrapped_http_error_parses_clean_message(self):
        err_payload = json.dumps(
            [{"error": {"code": 402, "status": "RESOURCE_EXHAUSTED", "message": "Credits depleted."}}]
        ).encode("utf-8")
        http_err = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1/interactions",
            code=402,
            msg="Payment Required",
            hdrs={},
            fp=io.BytesIO(err_payload),
        )
        client = GeminiClient(api_key="test-key", max_retries=0)
        with patch("urllib.request.urlopen", side_effect=http_err):
            with self.assertRaises(GeminiAPIError) as ctx:
                client.health_check()

        self.assertEqual(ctx.exception.status_code, 402)
        self.assertEqual(ctx.exception.error_code, "RESOURCE_EXHAUSTED")
        self.assertIn("Credits depleted.", str(ctx.exception))


class TestPostAnalyzerIntegration(unittest.TestCase):
    def test_analyzer_uses_gemini_interactions_api_when_configured(self):
        def fake_urlopen(req, timeout=None):
            return _FakeHTTPResponse(
                {
                    "id": "v1_lead_1",
                    "status": "completed",
                    "steps": [
                        {
                            "type": "model_output",
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(
                                        {
                                            "intent": "SERVICE_SEEKER",
                                            "draft_reply": "Oi! Dá uma olhada no ServiceApp para achar encanadores avaliados.",
                                        }
                                    ),
                                }
                            ],
                        }
                    ],
                }
            )

        analyzer = PostAnalyzer(api_key="test-key")
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            lead_type, draft = analyzer.analyze_post(
                title="Preciso de encanador em São Paulo",
                content="Vazamento urgente na cozinha, alguém indica?",
                country="BR",
            )

        self.assertEqual(lead_type, "SERVICE_SEEKER")
        self.assertIn("ServiceApp", draft)

    def test_analyzer_falls_back_to_heuristics_on_api_error(self):
        http_err = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1/interactions",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=io.BytesIO(b'{"error": {"message": "temporary outage"}}'),
        )
        client = GeminiClient(api_key="test-key", max_retries=0)
        analyzer = PostAnalyzer(gemini_client=client)
        with patch("urllib.request.urlopen", side_effect=http_err):
            lead_type, draft = analyzer.analyze_post(
                title="Busco plomero en Monterrey",
                content="Necesito cotización para reparación hoy.",
                country="MX",
            )

        self.assertEqual(lead_type, "SERVICE_SEEKER")
        self.assertIn("ServiceApp", draft)


if __name__ == "__main__":
    unittest.main()
