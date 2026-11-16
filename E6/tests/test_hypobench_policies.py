"""Mock-only tests for fixed Gemma HypoBench evaluation policies."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation import (  # noqa: E402
    evaluate_hypobench_explanation_on_heldout,
    prepare_hypobench_data_explanation_input,
)
from hypobench_policies import (  # noqa: E402
    make_hypobench_prediction_policy,
    make_hypobench_recovery_policy,
)


class FakeGemmaClient:
    model = "gemma3:12b"
    generation_options = {"temperature": 0.0, "seed": 2026}

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
        self.calls.append((stage, prompt, max_output_tokens))
        return {"raw_response": self.responses.pop(0), "adapter_metadata": {
            "prompt_eval_count": 99, "eval_count": 8, "total_tokens": 107,
            "done_reason": "stop",
        }}


class HypoBenchPolicyTests(unittest.TestCase):
    def prepared_input(self):
        return prepare_hypobench_data_explanation_input(
            "row-1", {"task": "Predict the outcome.", "observation": "Feature X is present."},
            [f"Rule {index}: Feature X predicts outcome Y." for index in range(1, 7)],
            dataset_id="fixture", split="TEST", dataset_provenance={"source": "fixture"},
        )

    def test_prediction_is_deterministic_and_never_receives_heldout_label(self):
        raw = json.dumps({"predicted_label": "likely republican voter",
                          "supporting_hypothesis_ids": ["H1"]})
        client = FakeGemmaClient([raw, raw])
        policy = make_hypobench_prediction_policy(client, [
            "likely democratic voter", "likely third-party/abstain voter",
            "likely republican voter",
        ])
        prepared = self.prepared_input()
        secret_label = "HELD_OUT_LABEL_CANARY_927"
        first = evaluate_hypobench_explanation_on_heldout(
            prepared, [secret_label], policy,
            predictor_policy_id="e6-hypobench-generated-hypothesis-application-v1",
        )
        second_prediction = policy(prepared)
        self.assertEqual(first["parsed_output"]["invalid_prediction_count"], 0)
        self.assertEqual(first["parsed_output"]["accuracy"], 0.0)
        self.assertEqual(second_prediction["predicted_labels"], ["likely republican voter"])
        self.assertEqual(client.calls[0][1], client.calls[1][1])
        self.assertNotIn(secret_label, client.calls[0][1])
        self.assertIn("Feature X predicts outcome Y", client.calls[0][1])
        self.assertEqual(client.calls[0][2], 32)
        self.assertFalse(first["provenance"]["heldout_label_in_prediction_input"])

    def test_invalid_or_out_of_set_predictions_are_null_and_score_incorrect(self):
        client = FakeGemmaClient([json.dumps({
            "predicted_label": "not a declared class", "supporting_hypothesis_ids": ["H1"],
        })])
        policy = make_hypobench_prediction_policy(client, ["A", "B"])
        result = evaluate_hypobench_explanation_on_heldout(
            self.prepared_input(), ["A"], policy, predictor_policy_id="fixture",
            valid_labels=["A", "B"],
        )
        self.assertEqual(result["raw_output"]["predicted_labels"], [None])
        self.assertEqual(result["parsed_output"]["accuracy"], 0.0)
        self.assertEqual(result["parsed_output"]["invalid_prediction_count"], 1)

    def test_recovery_policy_uses_stable_6_by_14_matrix_and_fixed_settings(self):
        matrix = [["NO_MATCH"] * 14 for _ in range(6)]
        matrix[0][2] = "MATCH"
        reverse = [list(row) for row in matrix]
        reverse[1][4] = "MATCH"
        raw = json.dumps({"generated_first": matrix, "planted_first": reverse})
        client = FakeGemmaClient([raw])
        policy = make_hypobench_recovery_policy(client)
        result = policy([f"generated-{i}" for i in range(6)],
                        [f"planted-{i}" for i in range(14)])
        expected = [list(row) for row in matrix]
        expected[1][4] = "AMBIGUOUS"
        self.assertEqual(result["judgments"], expected)
        self.assertEqual(client.calls[0][0], "hypobench_dataset_level_recovery")
        self.assertEqual(client.calls[0][2], 512)
        self.assertIn("dataset-level planted hypotheses", client.calls[0][1].lower())
        self.assertEqual(result["prediction_provenance"]["seed"], 2026)
        self.assertTrue(result["prediction_provenance"]["blinded_to_arm_identity"])
        self.assertEqual(result["order_disagreement_cell_count"], 1)

    def test_policy_rejects_non_deterministic_model_configuration(self):
        client = FakeGemmaClient([])
        client.generation_options = {"temperature": 0.7, "seed": 2026}
        with self.assertRaisesRegex(ValueError, "temperature=0"):
            make_hypobench_prediction_policy(client, ["A", "B"])


if __name__ == "__main__":
    unittest.main()
