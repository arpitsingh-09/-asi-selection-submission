"""Offline unit tests for the normal-Terminal Gemma verification helper."""

import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_gemma3_local import (  # noqa: E402
    DigestMismatchError,
    local_model_row,
    main,
    output_limit_result,
    inspect_local_manifest,
    run_verification,
    tokenizer_metadata_summary,
    verify_api_tag_digest,
)


class Gemma3VerificationHelperTests(unittest.TestCase):
    def test_saved_runtime_report_is_referenced_by_governing_gemma_configs(self):
        root = Path(__file__).resolve().parents[1]
        report_path = root / "data/gemma3_local_verification_v1.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        config = json.loads((root / "config.json").read_text(encoding="utf-8"))
        evaluation = json.loads((root / "evaluation_config.json").read_text(encoding="utf-8"))
        literature = json.loads((root / "literature_testbed_config.json").read_text(encoding="utf-8"))
        self.assertEqual(report["verification_status"], "verified_local_runtime")
        self.assertEqual(config["generation"]["tokenizer_metadata_fingerprint_sha256"],
                         report["tokenizer_metadata_fingerprint_sha256"])
        self.assertEqual(evaluation["generator_runtime_verification"]["report_sha256"],
                         literature["generator_runtime_verification"]["report_sha256"])
        self.assertTrue(evaluation["generator_runtime_verification"]["protocol_generator_selection_approved"])
        self.assertTrue(literature["generator_runtime_verification"]["protocol_generator_selection_approved"])
        self.assertEqual(config["protocol"]["status"], "approved")
        self.assertTrue(config["protocol"]["execution_authorized"])
        self.assertFalse(report["e6_ready_for_budgeted_execution"])
        self.assertEqual(config["inference_budget"]["tokens_per_input_set_arm"], 8192)

    def test_cli_reports_tokenizer_status_false_when_local_service_is_unavailable(self):
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "verification.json"
            with patch("verify_gemma3_local._request_json", side_effect=RuntimeError("service unavailable")), \
                 redirect_stdout(output):
                exit_code = main(["--probe-output-limit", "32", "--output", str(report_path)])
            saved = json.loads(report_path.read_text(encoding="utf-8"))
        result = json.loads(output.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(saved, result)
        self.assertEqual(result["verification_status"], "failed")
        self.assertFalse(result["exact_token_counter_available"])
        self.assertFalse(result["tokenizer_accounting_consistent_with_e6_preflight"])
        self.assertFalse(result["e6_ready_for_budgeted_execution"])

    def test_cli_saves_actual_runtime_result_and_tokenizer_fingerprint(self):
        output = io.StringIO()
        result = {
            "digest_verification": {"api_tags_matches_verified_manifest_artifact": True},
            "exact_token_counter_available": True,
            "tokenizer_accounting_consistent_with_e6_preflight": True,
            "tokenizer": {"metadata_sha256": "f" * 64},
            "smoke": {"passed": True},
            "output_limit_probe": {"honored_under_limit_pressure": True},
            "e6_ready_for_budgeted_execution": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "gemma_report.json"
            with patch("verify_gemma3_local.run_verification", return_value=result), redirect_stdout(output):
                code = main(["--probe-output-limit", "32", "--output", str(report_path)])
            saved = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(code, 0)
            self.assertEqual(saved["verification_status"], "verified_local_runtime")
            self.assertEqual(saved["tokenizer_metadata_fingerprint_sha256"], "f" * 64)
            self.assertFalse(saved["e6_ready_for_budgeted_execution"])
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(["--probe-output-limit", "32", "--output", str(report_path)])

    def test_ollama_04015_bare_tags_digest_is_selected_by_exact_model_tag(self):
        row = local_model_row({"models": [
            {"name": "gemma3:12b", "digest": "a" * 64, "size": 4},
            {"name": "qwen3:8b", "digest": "b" * 64},
        ]})
        self.assertEqual(row["name"], "gemma3:12b")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            local_model_row({"models": []})

    def test_missing_api_digest_has_endpoint_and_field_diagnostic(self):
        with self.assertRaisesRegex(ValueError, r"/api/tags models\['gemma3:12b'\]\.digest is missing"):
            local_model_row({"models": [{"name": "gemma3:12b"}]})

    def test_invalid_api_digest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid"):
            local_model_row({"models": [{"name": "gemma3:12b", "digest": "not-a-digest"}]})

    def test_api_manifest_digest_matches_only_manifest_expected_value(self):
        manifest_sha = "c" * 64
        layer_digest = "sha256:" + "a" * 64
        row = {"name": "gemma3:12b", "digest": manifest_sha}
        result = verify_api_tag_digest(
            row, api_manifest_sha256=manifest_sha, api_manifest_path="/test/selected-manifest",
            installed_manifest_sha256=manifest_sha,
            installed_model_layer_digest=layer_digest,
            inventory_manifest_sha256=manifest_sha,
            inventory_model_layer_digest=layer_digest,
        )
        self.assertTrue(result["api_tags_matches_ollama_selected_tag_manifest"])
        self.assertEqual(
            result["api_tags_digest_type"],
            "ollama_model_tag_manifest_digest_bare_sha256_hex",
        )

    def test_incorrect_manifest_digest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "differs from the locally resolved"):
            verify_api_tag_digest(
                {"digest": "d" * 64}, api_manifest_sha256="c" * 64,
                api_manifest_path="/test/selected-manifest", installed_manifest_sha256="c" * 64,
                installed_model_layer_digest="sha256:" + "a" * 64,
                inventory_manifest_sha256="c" * 64,
                inventory_model_layer_digest="sha256:" + "a" * 64,
            )

    def test_layer_digest_is_not_accepted_as_manifest_digest(self):
        layer = "a" * 64
        with self.assertRaises(DigestMismatchError) as caught:
            verify_api_tag_digest(
                {"digest": layer}, api_manifest_sha256="c" * 64,
                api_manifest_path="/test/selected-manifest", installed_manifest_sha256="c" * 64,
                installed_model_layer_digest="sha256:" + layer,
                inventory_manifest_sha256="c" * 64,
                inventory_model_layer_digest="sha256:" + layer,
            )
        diagnostic = caught.exception.diagnostic
        self.assertEqual(diagnostic["api_tags_digest_sha256"], layer)
        self.assertEqual(diagnostic["installed_model_layer_digest"], "sha256:" + layer)
        self.assertFalse(diagnostic["api_tags_matches_verified_manifest_artifact"])
        with self.assertRaisesRegex(ValueError, "without a prefix"):
            verify_api_tag_digest(
                {"digest": "c" * 64}, api_manifest_sha256="c" * 64,
                api_manifest_path="/test/selected-manifest",
                installed_manifest_sha256="sha256:" + "c" * 64,
                installed_model_layer_digest="sha256:" + layer,
                inventory_manifest_sha256="c" * 64,
                inventory_model_layer_digest="sha256:" + layer,
            )

    def test_local_manifest_hash_is_exact_file_bytes_and_layer_is_separate(self):
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "layers": [{
                "mediaType": "application/vnd.ollama.image.model",
                "digest": "sha256:" + "a" * 64,
            }],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "manifests/registry.ollama.ai/library/gemma3/12b"
            path.parent.mkdir(parents=True)
            raw = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
            path.write_bytes(raw)
            # Use the same expected location shape by setting OLLAMA_MODELS.
            import os
            previous = os.environ.get("OLLAMA_MODELS")
            os.environ["OLLAMA_MODELS"] = tmp
            try:
                result = inspect_local_manifest()
            finally:
                if previous is None:
                    os.environ.pop("OLLAMA_MODELS", None)
                else:
                    os.environ["OLLAMA_MODELS"] = previous
        self.assertEqual(result["manifest_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["model_layer_digest"], "sha256:" + "a" * 64)
        self.assertNotEqual(result["manifest_sha256"], "a" * 64)

    def test_ollama_v2_tag_symlink_is_preferred_and_hash_checked(self):
        model_layer_digest = "sha256:" + "a" * 64
        source_manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "layers": [{
                "mediaType": "application/vnd.ollama.image.model",
                "digest": model_layer_digest,
            }],
        }
        source_bytes = json.dumps(source_manifest, separators=(",", ":")).encode("utf-8")
        source_sha = hashlib.sha256(source_bytes).hexdigest()
        legacy_manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "layers": [
                {"mediaType": "application/vnd.ollama.image.model", "digest": model_layer_digest},
                {
                    "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                    "digest": "sha256:" + source_sha,
                    "size": len(source_bytes),
                },
            ],
        }
        legacy_bytes = json.dumps(legacy_manifest, separators=(",", ":")).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blob_path = root / "blobs" / ("sha256-" + source_sha)
            blob_path.parent.mkdir(parents=True)
            blob_path.write_bytes(source_bytes)
            v2_path = root / "manifests-v2/ollama.com/library/gemma3/12b"
            v2_path.parent.mkdir(parents=True)
            v2_path.symlink_to(blob_path)
            legacy_path = root / "manifests/registry.ollama.ai/library/gemma3/12b"
            legacy_path.parent.mkdir(parents=True)
            legacy_path.write_bytes(legacy_bytes)
            import os
            previous = os.environ.get("OLLAMA_MODELS")
            os.environ["OLLAMA_MODELS"] = tmp
            try:
                result = inspect_local_manifest()
            finally:
                if previous is None:
                    os.environ.pop("OLLAMA_MODELS", None)
                else:
                    os.environ["OLLAMA_MODELS"] = previous
        self.assertEqual(result["api_manifest_sha256"], source_sha)
        self.assertEqual(result["api_manifest_symlink_blob_sha256"], source_sha)
        self.assertEqual(result["api_manifest_representation"], "ollama_manifests_v2_tag_target_bytes")
        self.assertEqual(result["manifest_sha256"], hashlib.sha256(legacy_bytes).hexdigest())
        self.assertEqual(result["model_layer_digest"], model_layer_digest)
        self.assertEqual(result["embedded_source_manifest"]["blob_sha256"], source_sha)

    def test_three_observed_gemma_digests_keep_their_distinct_artifact_types(self):
        api_and_embedded_source_manifest = (
            "b92b218582c521ba287f38f1d6057dcd3c6cbff036f13cac97b5d861f5e58ec3"
        )
        outer_manifest_file = (
            "c0b76384be40635ad28390e0fd2386390838ead3e95ac5dbfcec1be652057ffa"
        )
        model_layer = "sha256:13576eb6dd8d9d04b4da04d015ff343968628d3c2984195569d9d3585651d4f1"
        result = verify_api_tag_digest(
            {"digest": api_and_embedded_source_manifest},
            api_manifest_sha256=api_and_embedded_source_manifest,
            api_manifest_path="/test/model-manifests-v2/gemma3/12b",
            installed_manifest_sha256=outer_manifest_file,
            installed_model_layer_digest=model_layer,
            inventory_manifest_sha256=outer_manifest_file,
            inventory_model_layer_digest=model_layer,
            source_manifest_layer_digest="sha256:" + api_and_embedded_source_manifest,
            source_manifest_blob_sha256=api_and_embedded_source_manifest,
        )
        self.assertEqual(result["api_tags_digest_match_kind"], "ollama_selected_tag_manifest_bytes")
        self.assertTrue(result["api_tags_matches_verified_manifest_artifact"])
        self.assertFalse(result["api_tags_matches_legacy_named_manifest"])
        self.assertEqual(result["legacy_named_manifest_sha256"], outer_manifest_file)
        self.assertEqual(result["installed_model_layer_digest"], model_layer)

    def test_api_digest_that_only_matches_model_weights_is_rejected_as_wrong_type(self):
        layer_hex = "1" * 64
        with self.assertRaises(DigestMismatchError) as caught:
            verify_api_tag_digest(
                {"digest": layer_hex}, api_manifest_sha256="2" * 64,
                api_manifest_path="/test/selected-manifest", installed_manifest_sha256="2" * 64,
                installed_model_layer_digest="sha256:" + layer_hex,
                inventory_manifest_sha256="2" * 64,
                inventory_model_layer_digest="sha256:" + layer_hex,
            )
        self.assertEqual(
            caught.exception.diagnostic["failure_reason"],
            "API digest matches model weight layer, not an accepted manifest artifact",
        )

    def test_verified_digest_continues_to_adapter_smoke_and_num_predict_probe(self):
        api_digest = "b92b218582c521ba287f38f1d6057dcd3c6cbff036f13cac97b5d861f5e58ec3"
        layer = "sha256:13576eb6dd8d9d04b4da04d015ff343968628d3c2984195569d9d3585651d4f1"
        manifest_sha = "c0b76384be40635ad28390e0fd2386390838ead3e95ac5dbfcec1be652057ffa"
        verified_manifest = {
            "manifest_path": "/model-store/manifests/gemma3/12b",
            "manifest_sha256": manifest_sha,
            "api_manifest_path": "/model-store/manifests-v2/gemma3/12b",
            "api_manifest_sha256": api_digest,
            "model_layer_digest": layer,
            "embedded_source_manifest": {
                "layer_digest": "sha256:" + api_digest,
                "blob_sha256": api_digest,
            },
        }
        fake_client = Mock()
        fake_client.count_prompt_tokens.return_value = {
            "raw_response": "x", "input_tokens": 3, "output_tokens": 1,
            "total_tokens": 4,
            "token_count_preflight": {
                "method": "ollama_prompt_eval_count_with_num_predict_one",
                "requested_num_predict": 1, "bounded_probe_confirmed": True,
                "prompt_eval_count": 3, "eval_count": 1,
            },
        }
        fake_client.return_value = {
            "raw_response": '{"result":"E6 READY"}',
            "input_tokens": 3, "output_tokens": 1, "total_tokens": 4,
            "adapter_metadata": {"done_reason": "stop", "done": True},
        }
        fake_client.call_with_token_limit.return_value = {
            "raw_response": '{"items":[]}',
            "output_tokens": 32,
            "adapter_metadata": {"done_reason": "length", "done": True},
        }
        responses = {
            "/api/version": {"version": "0.40.15"},
            "/api/tags": {"models": [{"name": "gemma3:12b", "digest": api_digest}]},
            "/api/show": {"model_info": {
                "tokenizer.ggml.model": "gpt2",
                "tokenizer.ggml.pre": "gemma3",
                "tokenizer.ggml.tokens": ["x"],
            }},
        }
        with patch("verify_gemma3_local._request_json", side_effect=lambda path, *_: responses[path]), \
             patch("verify_gemma3_local.expected_local_model_metadata", return_value={
                 "manifest_sha256": manifest_sha, "model_layer_digest": layer,
             }), \
             patch("verify_gemma3_local.inspect_local_manifest", return_value=verified_manifest), \
             patch("verify_gemma3_local.OllamaModelClient", return_value=fake_client):
            result = run_verification(32)
        self.assertTrue(result["digest_verification"]["api_tags_matches_verified_manifest_artifact"])
        self.assertTrue(result["exact_token_counter_available"])
        self.assertTrue(result["tokenizer_accounting_consistent_with_e6_preflight"])
        self.assertTrue(result["e6_ready_for_budgeted_execution"])
        self.assertTrue(result["protocol_execution_gate_open"])
        self.assertEqual(result["configured_arm_token_cap"], 8192)
        self.assertEqual(result["scope"], "development_only_no_experiment")
        fake_client.assert_called_once()
        fake_client.count_prompt_tokens.assert_called_once()
        fake_client.call_with_token_limit.assert_called_once()
        self.assertTrue(result["smoke"]["passed"])
        self.assertTrue(result["output_limit_probe"]["honored_under_limit_pressure"])

    def test_stale_inventory_is_reported_even_when_api_matches_live_manifest(self):
        live_manifest = "c" * 64
        layer = "sha256:" + "a" * 64
        with self.assertRaises(DigestMismatchError) as caught:
            verify_api_tag_digest(
                {"digest": live_manifest}, api_manifest_sha256=live_manifest,
                api_manifest_path="/test/selected-manifest", installed_manifest_sha256=live_manifest,
                installed_model_layer_digest=layer,
                inventory_manifest_sha256="d" * 64,
                inventory_model_layer_digest=layer,
            )
        self.assertTrue(caught.exception.diagnostic["api_tags_matches_ollama_selected_tag_manifest"])
        self.assertFalse(caught.exception.diagnostic["installed_manifest_matches_recorded_inventory"])

    def test_tokenizer_metadata_is_fingerprinted_without_emitting_vocabulary(self):
        fields = {
            "tokenizer.ggml.model": "gpt2",
            "tokenizer.ggml.pre": "gemma3",
            "tokenizer.ggml.tokens": ["a", "b", "c"],
            "tokenizer.ggml.merges": ["a b"],
            "general.architecture": "gemma3",
        }
        result = tokenizer_metadata_summary({"model_info": fields})
        expected = hashlib.sha256(json.dumps(
            {key: value for key, value in fields.items() if key.startswith("tokenizer.ggml.")},
            sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")).hexdigest()
        self.assertEqual(result["metadata_sha256"], expected)
        self.assertEqual(result["model"], "gpt2")
        self.assertEqual(result["pre"], "gemma3")
        self.assertEqual(result["vocabulary_size"], 3)
        self.assertTrue(result["metadata_fingerprint_is_not_a_token_count"])
        self.assertIn("installed Ollama llama.cpp runner", result["tokenization_delegated_to"])
        self.assertNotIn("a", result)

    def test_runtime_output_limit_check_requires_limit_pressure_and_bounded_eval_count(self):
        result = output_limit_result({
            "output_tokens": 8,
            "adapter_metadata": {"done_reason": "length"},
        }, 8)
        self.assertTrue(result["honored_under_limit_pressure"])
        too_many = output_limit_result({
            "output_tokens": 9,
            "adapter_metadata": {"done_reason": "length"},
        }, 8)
        self.assertFalse(too_many["honored_under_limit_pressure"])
        early_stop = output_limit_result({
            "output_tokens": 3,
            "adapter_metadata": {"done_reason": "stop"},
        }, 8)
        self.assertFalse(early_stop["honored_under_limit_pressure"])


if __name__ == "__main__":
    unittest.main()
