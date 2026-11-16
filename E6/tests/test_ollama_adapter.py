#!/usr/bin/env python3
"""Mock-only tests for the local E6 Ollama adapter."""

import json
import socket
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ollama_adapter import OllamaModelClient, OllamaRequestError
from orchestrator import _normalize_client_reply


class MockResponse:
    def __init__(self, body, status=200):
        self.body = body if isinstance(body, bytes) else body.encode("utf-8")
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body

    def getcode(self):
        return self.status


class OllamaAdapterTests(unittest.TestCase):
    def setUp(self):
        self.client = OllamaModelClient(
            model="gemma3:12b", timeout_seconds=12,
            generation_options={"temperature": 0.0, "num_predict": 777},
        )

    def test_large_context_count_probe_is_separate_from_generation_context(self):
        client = OllamaModelClient(generation_options={'num_ctx': 32768, 'num_predict': 2048},
                                   preflight_context_limit=131072)
        result = {'input_tokens': 100, 'output_tokens': 1, 'total_tokens': 101,
                  'adapter_metadata': {'done': True}}
        with patch.object(client, '_call', return_value=result) as caller:
            measured = client.count_prompt_tokens('D_generation', 'fixture')
        self.assertEqual(caller.call_args.args[2]['num_ctx'], 131072)
        self.assertEqual(client.generation_options['num_ctx'], 32768)
        self.assertTrue(measured['token_count_preflight']['bounded_probe_confirmed'])
        with patch.object(client, '_call') as caller:
            with self.assertRaisesRegex(ValueError, 'admission'):
                client.count_prompt_tokens('D_generation', 'x' * 131072)
            caller.assert_not_called()

    def test_success_captures_raw_text_identity_usage_settings_and_latency(self):
        body = {
            "model": "gemma3:12b",
            "created_at": "2026-01-02T03:04:05Z",
            "response": '{"ok": true}',
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 123,
            "eval_count": 9,
        }
        with patch("ollama_adapter.urllib.request.urlopen", return_value=MockResponse(json.dumps(body))) as open_url:
            result = self.client("D_generation", "fixture prompt")

        request = open_url.call_args.args[0]
        sent = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "http://localhost:11434/api/generate")
        self.assertEqual(open_url.call_args.kwargs["timeout"], 12.0)
        self.assertEqual(sent["model"], "gemma3:12b")
        self.assertEqual(sent["format"], "json")
        self.assertFalse(sent["stream"])
        self.assertEqual(sent["options"], {"temperature": 0.0, "num_predict": 777})
        self.assertEqual(result["raw_response"], '{"ok": true}')
        self.assertEqual(result["input_tokens"], 123)
        self.assertEqual(result["output_tokens"], 9)
        self.assertEqual(result["total_tokens"], 132)
        self.assertGreaterEqual(result["latency_seconds"], 0)
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(result["model_identity"]["reported_model"], "gemma3:12b")
        self.assertEqual(result["adapter_metadata"]["done_reason"], "stop")

    def test_call_with_token_limit_tightens_num_predict_per_request(self):
        body = {"response": "{}", "done": True, "done_reason": "stop",
                "prompt_eval_count": 2, "eval_count": 1}
        with patch("ollama_adapter.urllib.request.urlopen", return_value=MockResponse(json.dumps(body))) as open_url:
            result = self.client.call_with_token_limit(
                "D_generation", "fixture prompt", max_output_tokens=20,
            )
        request = json.loads(open_url.call_args.args[0].data.decode("utf-8"))
        self.assertEqual(request["options"]["num_predict"], 20)
        self.assertEqual(result["adapter_metadata"]["requested_output_token_limit"], 20)

    def test_prompt_count_uses_same_format_with_one_token_probe(self):
        body = {"response": "x", "done": True, "done_reason": "length",
                "prompt_eval_count": 17, "eval_count": 1}
        with patch("ollama_adapter.urllib.request.urlopen", return_value=MockResponse(json.dumps(body))) as open_url:
            result = self.client.count_prompt_tokens("D_generation", "same prompt")
        request = json.loads(open_url.call_args.args[0].data.decode("utf-8"))
        self.assertEqual(request["prompt"], "same prompt")
        self.assertEqual(request["format"], "json")
        self.assertEqual(request["options"], {"temperature": 0.0, "num_predict": 1})
        self.assertEqual(result["input_tokens"], 17)
        self.assertEqual(result["output_tokens"], 1)
        self.assertTrue(result["token_count_preflight"]["bounded_probe_confirmed"])

    def test_prompt_count_rejects_unbounded_probe_usage_metadata(self):
        body = {"response": "too much", "done": True,
                "prompt_eval_count": 17, "eval_count": 2}
        with patch("ollama_adapter.urllib.request.urlopen", return_value=MockResponse(json.dumps(body))):
            result = self.client.count_prompt_tokens("D_generation", "same prompt")
        self.assertFalse(result["token_count_preflight"]["bounded_probe_confirmed"])

    def test_malformed_model_json_is_returned_unchanged_for_pipeline_validation(self):
        body = {"response": "{not valid JSON", "prompt_eval_count": 3, "eval_count": 4}
        with patch("ollama_adapter.urllib.request.urlopen", return_value=MockResponse(json.dumps(body))):
            result = self.client("D_generation", "fixture prompt")
        self.assertEqual(result["raw_response"], "{not valid JSON")

    def test_malformed_http_json_preserves_body_and_status(self):
        with patch("ollama_adapter.urllib.request.urlopen", return_value=MockResponse("{broken", 200)):
            with self.assertRaises(OllamaRequestError) as caught:
                self.client("D_generation", "fixture prompt")
        self.assertEqual(caught.exception.category, "malformed_http_json")
        self.assertEqual(caught.exception.status_code, 200)
        self.assertEqual(caught.exception.response_body, "{broken")
        self.assertEqual(caught.exception.audit_metadata["http_status"], 200)

    def test_http_error_preserves_status_and_response_body(self):
        error = urllib.error.HTTPError(
            "http://localhost:11434/api/generate", 503, "Unavailable", {},
            __import__("io").BytesIO(b"local server unavailable"),
        )
        with patch("ollama_adapter.urllib.request.urlopen", side_effect=error):
            with self.assertRaises(OllamaRequestError) as caught:
                self.client("D_generation", "fixture prompt")
        self.assertEqual(caught.exception.category, "http_error")
        self.assertEqual(caught.exception.status_code, 503)
        self.assertEqual(caught.exception.response_body, "local server unavailable")

    def test_connection_failure_is_classified_and_retained(self):
        with patch("ollama_adapter.urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
            with self.assertRaises(OllamaRequestError) as caught:
                self.client("D_generation", "fixture prompt")
        self.assertEqual(caught.exception.category, "connection_error")
        self.assertIn("refused", caught.exception.audit_metadata["error"])

    def test_timeout_is_classified(self):
        with patch("ollama_adapter.urllib.request.urlopen", side_effect=socket.timeout("late")):
            with self.assertRaises(OllamaRequestError) as caught:
                self.client("D_generation", "fixture prompt")
        self.assertEqual(caught.exception.category, "timeout")

    def test_missing_usage_metadata_is_explicitly_unavailable(self):
        with patch("ollama_adapter.urllib.request.urlopen", return_value=MockResponse(
            json.dumps({"response": "{}", "model": "gemma3:12b"})
        )):
            result = self.client("D_generation", "fixture prompt")
        self.assertIsNone(result["input_tokens"])
        self.assertIsNone(result["output_tokens"])
        self.assertIsNone(result["total_tokens"])
        self.assertFalse(result["adapter_metadata"]["usage_metadata_available"])

    def test_orchestrator_accounting_retains_adapter_metadata(self):
        reply = {
            "raw_response": "{}", "input_tokens": 4, "output_tokens": 5,
            "latency_seconds": 0.25,
            "adapter_metadata": {"http_status": 200, "model": "gemma3:12b"},
        }
        raw, accounting, metadata = _normalize_client_reply(reply)
        self.assertEqual(raw, "{}")
        self.assertEqual(accounting["total_tokens"], 9)
        self.assertEqual(accounting["latency_seconds"], 0.25)
        self.assertEqual(metadata, {"http_status": 200, "model": "gemma3:12b"})

    def test_accepts_explicit_qwen_model_selection(self):
        client = OllamaModelClient(model="qwen3:8b")
        self.assertEqual(client.model, "qwen3:8b")
        self.assertEqual(client.model_configuration["model"], "qwen3:8b")

    def test_rejects_empty_model_selection(self):
        for model in ("", "   ", None):
            with self.subTest(model=model):
                with self.assertRaises(ValueError):
                    OllamaModelClient(model=model)


if __name__ == "__main__":
    unittest.main(verbosity=2)
