#!/usr/bin/env python3
"""Mock-only tests for gated seven-arm orchestration and provisional envelopes."""

import json
import hashlib
import sys
import unittest
import re
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orchestrator import ARMS, ExperimentInput, run_seven_arms, serialize_provisional_envelope
from question_pipeline import PipelineSettings, PipelineState


def hypotheses(arm):
    return json.dumps({"arm": arm, "hypotheses": [
        {"id": f"H{i}", "text": f"{arm} hypothesis {i} predicts a measurable outcome."}
        for i in range(1, 7)
    ]})


def qh_output():
    questions = []
    number = 1
    for q in range(1, 4):
        questions.append({
            "id": f"Q{q}",
            "text": f"QH research question {q}?",
            "hypotheses": [
                {"id": f"H{number + offset}", "text": f"QH hypothesis {number + offset} predicts an outcome."}
                for offset in range(2)
            ],
        })
        number += 2
    return json.dumps({"arm": "QH", "questions": questions})


def hq_output():
    return json.dumps({
        "hypotheses": [
            {"id": f"H{i}", "text": f"HQ hypothesis {i} predicts an outcome."}
            for i in range(1, 7)
        ],
        "questions": [
            {"hypothesis_id": f"H{i}", "text": f"Question for HQ hypothesis {i}?"}
            for i in range(1, 7)
        ],
    })


def nested_selected_output(arm, questions):
    nested = []
    number = 1
    for index, question in enumerate(questions, start=1):
        nested.append({
            "id": f"Q{index}",
            "text": question["text"],
            "hypotheses": [
                {"id": f"H{number + offset}", "text": f"{arm} hypothesis {number + offset} tests an outcome."}
                for offset in range(2)
            ],
        })
        number += 2
    return json.dumps({"arm": arm, "questions": nested})


def selection_state():
    state = PipelineState()
    state.candidate_records = [
        {"candidate_id": f"CQ{i}", "text": f"Selected question {i}?", "validation_status": "valid"}
        for i in range(1, 4)
    ]
    state.selections = {
        "QH-sel": {"status": "ok", "selected_candidate_ids": ["CQ1", "CQ2", "CQ3"]},
        "QH-rand": {"status": "ok", "selected_candidate_ids": ["CQ3", "CQ1", "CQ2"]},
    }
    state.raw_responses = [{"stage": "selection_fixture", "raw": "fixture artifact"}]
    return state


def test_settings():
    return PipelineSettings.from_mapping({
        "candidate_count": 6,
        "qh_sel_ranking_weights": {"novelty": .30, "specificity": .25,
            "scientific_significance": .25, "evidence_grounding": .20},
        "qh_sel_tie_break_policy": "weighted_score_desc_then_generation_order",
        "random_seed": 2026, "random_sampler": "sha256_key_ascending_v1",
        "random_generator_and_version": "SHA256",
        "per_input_seed_derivation": "E6-QH-RAND-v1|2026|<input_set_id>|<question_id>",
        "clustering_policy": "complete_link_candidate_generation_order_v1",
        "representative_selection_policy": "earliest_candidate_generation_order",
        "selection_count": 3,
        "arm_hypothesis_max_attempts": 1,
        "arm_hypothesis_retry_policy": None,
        "selected_hypothesis_max_attempts": 1,
        "selected_hypothesis_retry_policy": None,
        "d_empty_task_evidence_policy": "test-only guard",
        "d_empty_evidence_fields": ["abstract", "reference_evidence"],
        "d_shuffled_donor_constraints": {"fixture_constraint": True},
        # No donor-selection method or seed is selected by this test fixture.
        "d_shuffled_assignment_algorithm": None,
        "d_shuffled_assignment_seed": None,
        "d_shuffled_within_split_only": None,
        "d_shuffled_donor_reuse_policy": None,
    })


class MockClient:
    def __init__(self, fail_stage=None):
        self.calls = []
        self.fail_stage = fail_stage

    def __call__(self, stage, prompt):
        self.calls.append((stage, prompt))
        if stage == self.fail_stage:
            return {"raw_response": "not valid JSON", "input_tokens": 10, "output_tokens": 2, "cost_usd": 0.01}
        if stage == "candidate_generation":
            raw = json.dumps({"questions": [
                {"id": f"Q{i}", "text": f"How does mechanism {i} affect outcome {i}?"}
                for i in range(1, 7)]})
        elif stage == "pairwise_deduplication_batch":
            rows = []
            for i in range(1, 7):
                for j in range(i + 1, 7):
                    rows.append({"question_a": f"CQ{i}", "question_b": f"CQ{j}",
                        "is_duplicate": False, "reason": "Distinct fixture questions."})
            raw = json.dumps({"pairwise_comparisons": rows})
        elif stage == "qh_sel_ranking":
            raw = json.dumps({"scores": [{"question_id": f"CQ{i}", "novelty": 3,
                "specificity": 3, "scientific_significance": 3, "evidence_grounding": 3}
                for i in range(1, 7)]})
        elif stage == "D_generation":
            raw = hypotheses("D")
        elif stage == "QH_generation":
            raw = qh_output()
        elif stage == "QH-sel_hypothesis_generation":
            selected = re.findall(r"^Q\d+: (.+)$", prompt, re.MULTILINE)
            raw = nested_selected_output("QH-sel", [{"text": text} for text in selected])
        elif stage == "QH-rand_hypothesis_generation":
            selected = re.findall(r"^Q\d+: (.+)$", prompt, re.MULTILINE)
            raw = nested_selected_output("QH-rand", [{"text": text} for text in selected])
        elif stage == "HQ_generation":
            raw = hq_output()
        elif stage == "D-empty_generation":
            raw = hypotheses("D-empty")
        elif stage == "D-shuffled_generation":
            raw = hypotheses("D-shuffled")
        else:
            raise AssertionError(f"unexpected model stage: {stage}")
        return {
            "raw_response": raw,
            "usage": {"input_tokens": 100, "output_tokens": 50},
            "cost": 0.025,
            "latency_seconds": 0.2,
        }

    def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
        reply = self(stage, prompt)
        # The budgeted test tokenizer counts fixture text. Discard canned usage
        # from this unmetered mock and let the controller compute exact counts.
        return {
            "raw_response": reply["raw_response"],
            "cost": reply.get("cost"),
            "latency_seconds": reply.get("latency_seconds"),
            "adapter_metadata": {
                "done_reason": "stop",
                "requested_output_token_limit": max_output_tokens,
            },
        }


def run_with_test_gate(client, **kwargs):
    token_budget_per_arm = kwargs.pop("token_budget_per_arm", 100000)
    token_counter = kwargs.pop("token_counter", lambda text: len(text.split()))
    input_record = ExperimentInput(
        paper_id="test-paper-001",
        domain_and_task="Mock domain task",
        evidence="Mock abstract evidence",
        provenance={"fixture": True}, split="DEVELOPMENT",
        reference_evidence=(),
    )
    with patch("orchestrator.validate_current_protocol", return_value=[]):
        return run_seven_arms(
            input_record, test_settings(), client,
            {"model": "mock-model", "version": "test-only"},
            d_empty_task_evidence_check=lambda *_: {"passed": True, "fixture": "empty-check"},
            token_budget_per_arm=token_budget_per_arm,
            token_counter=token_counter,
            **kwargs,
        )


class OrchestrationTests(unittest.TestCase):
    def test_development_profile_mode_rejects_bad_manifest_attestation_before_calls(self):
        from profile_development_token_budget import load_development_manifest

        manifest, manifest_sha = load_development_manifest()
        record = manifest["inputs"][0]
        task = "Generic development task"
        client = MockClient()
        experiment_input = ExperimentInput(
            paper_id=record["paper_id"], domain_and_task=task,
            evidence=record["abstract"],
            provenance={"source_record_sha256": record["source_record_sha256"]},
            split="DEVELOPMENT", reference_evidence=(),
        )
        result = run_seven_arms(
            experiment_input, test_settings(), client,
            {"model": "mock-development-profile"},
            execution_mode="development_profile", token_budget_per_arm=1000,
            development_profile_attestation={
                "scope": "e6_development_token_profile_only",
                "manifest_sha256": "0" * 64,
                "task_sha256": hashlib.sha256(task.encode()).hexdigest(),
                "operator_confirmed_task_is_not_paper_specific": True,
            },
        )
        self.assertEqual(result["experiment_status"], "blocked")
        self.assertTrue(result["development_profile_only"])
        self.assertEqual(client.calls, [])
        self.assertTrue(any("manifest hash is invalid" in error
                            for error in result["protocol_validation_errors"]))

    def test_complete_mock_run_covers_all_seven_arms_and_manifest_fields(self):
        client = MockClient()
        result = run_with_test_gate(client)
        self.assertEqual(result["experiment_status"], "partial_failure")
        self.assertEqual(result["execution_mode"], "development")
        self.assertEqual(result["schema_status"], "provisional_unapproved")
        self.assertEqual(set(result["arms"]), set(ARMS))
        self.assertEqual(len(result["execution_manifest"]), 7)

        self.assertEqual(len(client.calls), 8)

        for arm in ARMS:
            entry = result["arms"][arm]
            manifest = entry["manifest"]
            if arm in ("D-empty", "D-shuffled"):
                self.assertEqual(entry["execution_status"], "blocked")
                self.assertTrue(entry["missing_output"])
                continue
            self.assertEqual(entry["execution_status"], "succeeded")
            self.assertFalse(entry["missing_output"])
            self.assertEqual(len(entry["output"]["hypotheses"]), 6)
            self.assertTrue(manifest["paper_id"])
            self.assertEqual(manifest["arm"], arm)
            self.assertEqual(len(manifest["input_sha256"]), 64)
            self.assertEqual(len(manifest["evidence_sha256"]), 64)
            self.assertTrue(manifest["prompt_version"].startswith("prompts/e6/"))
            self.assertEqual(len(manifest["prompt_template_sha256"]), 64)
            self.assertEqual(len(manifest["prompt_sha256"]), 64)
            self.assertEqual(manifest["model_configuration"]["model"], "mock-model")
            if arm not in ("D-empty", "D-shuffled"):
                self.assertTrue(manifest["output_reference"].startswith("inline:"))

        self.assertIsNone(result["arms"]["D-shuffled"]["manifest"]["donor_paper_id"])
        self.assertIn("trusted production D-empty auditor is not configured",
            result["arms"]["D-empty"]["output"]["errors"][0])
        self.assertIn("verified development source records and expected hashes",
            result["arms"]["D-shuffled"]["output"]["errors"][0])
        self.assertEqual(
            result["arms"]["D-empty"]["manifest"]["evidence_sha256"],
            hashlib.sha256(b"").hexdigest(),
        )
        self.assertIn("question_selection_state", result["arms"]["QH-sel"]["intermediate_artifacts"])
        prep_state = result["arms"]["QH-sel"]["intermediate_artifacts"]["question_selection_state"]
        sel = prep_state["selections"]["QH-sel"]
        rand = prep_state["selections"]["QH-rand"]
        self.assertEqual(sel["representative_pool_sha256"], rand["representative_pool_sha256"])
        self.assertEqual(sel["representative_ids"], rand["representative_ids"])
        self.assertEqual(result["call_accounting"]["call_count"], 8)
        self.assertGreater(result["call_accounting"]["input_tokens"]["sum"], 0)
        self.assertGreater(result["call_accounting"]["output_tokens"]["sum"], 0)
        self.assertEqual(set(result["token_budget_accounting"]), set(ARMS))
        self.assertTrue(all(
            value["budget_status"] == "within_budget"
            for value in result["token_budget_accounting"].values()
        ))
        self.assertAlmostEqual(result["call_accounting"]["cost"]["sum"], 0.2)
        serialized = serialize_provisional_envelope(result)
        self.assertEqual(json.loads(serialized)["schema_status"], "provisional_unapproved")

    def test_small_shared_cap_blocks_calls_and_records_per_arm_exhaustion(self):
        client = MockClient()
        result = run_with_test_gate(client, token_budget_per_arm=1)
        self.assertEqual(client.calls, [])
        self.assertEqual(set(result["token_budget_accounting"]), set(ARMS))
        self.assertEqual(
            result["token_budget_accounting"]["D"]["budget_status"],
            "blocked_before_call",
        )
        self.assertEqual(
            result["token_budget_accounting"]["QH-rand"]["budget_status"],
            "blocked_before_call",
        )
        self.assertEqual(result["token_budget_accounting"]["D"]["tokens_used"], 0)
        self.assertTrue(all(row["missing_output"] for row in result["arms"].values()))

    def test_provisional_writer_rejects_approved_or_unknown_schema_labels(self):
        with self.assertRaises(ValueError):
            serialize_provisional_envelope({
                "schema_version": "e6-provisional-envelope-v1",
                "schema_status": "approved",
            })

    def test_current_unapproved_protocol_blocks_all_model_calls(self):
        client = MockClient()
        input_record = ExperimentInput("test-paper", "Task", "Evidence")
        result = run_seven_arms(input_record, test_settings(), client, {"model": "mock"})
        self.assertEqual(result["experiment_status"], "blocked")
        self.assertTrue(result["protocol_validation_errors"])
        self.assertEqual(client.calls, [])
        self.assertEqual(len(result["execution_manifest"]), 7)
        self.assertTrue(all(row["execution_status"] == "blocked" for row in result["execution_manifest"]))
        self.assertTrue(all(row["missing_output"] for row in result["execution_manifest"]))
        self.assertEqual(result["call_accounting"]["call_count"], 0)

    def test_explicit_development_mode_accepts_development_split(self):
        client = MockClient()
        result = run_with_test_gate(client, execution_mode="development")
        self.assertEqual(result["execution_mode"], "development")
        self.assertEqual(result["experiment_status"], "partial_failure")
        self.assertEqual(len(client.calls), 8)

    def test_development_mode_rejects_evaluation_split(self):
        client = MockClient()
        input_record = ExperimentInput(
            "evaluation-paper", "Task", "Evidence",
            split="EVALUATION",
        )
        with patch("orchestrator.validate_current_protocol", return_value=[]):
            result = run_seven_arms(
                input_record, test_settings(), client, {"model": "mock"},
                execution_mode="development",
            )
        self.assertEqual(result["execution_mode"], "development")
        self.assertEqual(result["experiment_status"], "blocked")
        self.assertTrue(any(
            "development modes accept only DEVELOPMENT split inputs" in error
            for error in result["protocol_validation_errors"]
        ))
        self.assertEqual(client.calls, [])

    def test_final_mode_is_fail_closed(self):
        client = MockClient()
        result = run_with_test_gate(client, execution_mode="final")
        self.assertEqual(result["execution_mode"], "final")
        self.assertEqual(result["experiment_status"], "blocked")
        self.assertTrue(any(
            "final execution is disabled" in error
            for error in result["protocol_validation_errors"]
        ))
        self.assertEqual(client.calls, [])

    def test_unknown_execution_mode_is_blocked(self):
        client = MockClient()
        result = run_with_test_gate(client, execution_mode="production")
        self.assertEqual(result["execution_mode"], "production")
        self.assertEqual(result["experiment_status"], "blocked")
        self.assertTrue(any(
            "execution_mode must be development, development_profile, or final" in error
            for error in result["protocol_validation_errors"]
        ))
        self.assertEqual(client.calls, [])

    def test_partial_arm_failure_is_recorded_without_losing_other_outputs(self):
        client = MockClient(fail_stage="QH_generation")
        result = run_with_test_gate(client)
        self.assertEqual(result["experiment_status"], "partial_failure")
        self.assertEqual(result["arms"]["QH"]["execution_status"], "failed")
        self.assertTrue(result["arms"]["QH"]["missing_output"])
        self.assertEqual(result["arms"]["QH"]["intermediate_artifacts"]["raw_responses"][0]["raw"],
                         "not valid JSON")
        self.assertEqual(result["arms"]["D"]["execution_status"], "succeeded")
        self.assertEqual(result["call_accounting"]["call_count"], 8)

    def test_invalid_preparation_blocks_selected_arm_generation(self):
        client = MockClient(fail_stage="candidate_generation")
        result = run_with_test_gate(client)
        self.assertEqual(result["arms"]["QH-sel"]["execution_status"], "blocked")
        self.assertEqual(result["arms"]["QH-rand"]["execution_status"], "blocked")
        self.assertFalse(any(stage.endswith("hypothesis_generation") for stage, _ in client.calls))
        self.assertIn("shared question preparation failed",
            result["arms"]["QH-sel"]["output"]["errors"][0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
