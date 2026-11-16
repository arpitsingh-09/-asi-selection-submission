#!/usr/bin/env python3
"""Mock-only tests for the policy-gated E6 question pipeline."""

import json
import itertools
import hashlib
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from question_pipeline import (  # noqa: E402
    PipelineSettings,
    PipelineState,
    D_SHUFFLED_ALGORITHM,
    D_SHUFFLED_SEED,
    TrustedDEmptyAuditResult,
    TrustedDEmptyEvidenceAuditor,
    _d_empty_audit_validation_errors,
    assign_d_shuffled_donors,
    compare_candidates,
    compare_candidates_batch,
    cluster_and_choose_representatives,
    cluster_candidates_complete_link,
    generate_d_empty,
    generate_d_shuffled,
    generate_candidates,
    generate_direct_arm,
    generate_question_hypotheses,
    prepare_qh_selection_arms,
    select_qh_rand_sha256,
    selected_questions_for_arm,
    validate_d_shuffled_assignment_batch,
    select_qh_rand,
    select_qh_sel,
)


def candidate_response(count=4):
    return json.dumps({"questions": [
        {"id": f"Q{i}", "text": f"How does mechanism {i} affect outcome {i}?"}
        for i in range(1, count + 1)
    ]})


def batch_dedup_response(duplicate_pairs=()):
    duplicates = {frozenset(pair) for pair in duplicate_pairs}
    rows = []
    for left, right in itertools.combinations([f"CQ{i}" for i in range(1, 7)], 2):
        rows.append({
            "question_a": left,
            "question_b": right,
            "is_duplicate": frozenset((left, right)) in duplicates,
            "reason": "Fixture comparison reason.",
        })
    return json.dumps({"pairwise_comparisons": rows})


def ranking_response(question_ids, scores=None):
    scores = scores or {}
    dimensions = ("novelty", "specificity", "scientific_significance", "evidence_grounding")
    return json.dumps({"scores": [
        {"question_id": question_id, **{
            dimension: scores.get((question_id, dimension), 3) for dimension in dimensions
        }}
        for question_id in question_ids
    ]})


class MockModel:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, stage, prompt):
        self.calls.append((stage, prompt))
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


class FixtureDEmptyAuditor(TrustedDEmptyEvidenceAuditor):
    """Untrusted fixture provider; its result is explicitly marked mock-only."""

    def __init__(self, result):
        self.result = result
        self.calls = []

    def audit(self, recipient_id, retained_task_text, original_evidence, policy):
        self.calls.append((recipient_id, retained_task_text, original_evidence, policy))
        return self.result


class QuestionPipelineTests(unittest.TestCase):
    def configured(self, **overrides):
        data = {
            "candidate_count": 4,
            "deduplication_threshold": None,
            "clustering_policy": "test-fixture-policy",
            "representative_selection_policy": "test-fixture-policy",
            "qh_sel_ranking_weights": {"fixture_dimension": 1.0},
            "qh_sel_tie_break_policy": "test-fixture-order",
            "random_seed": 1937,
            "selected_hypothesis_max_attempts": 1,
            "selected_hypothesis_retry_policy": None,
            "arm_hypothesis_max_attempts": 1,
            "arm_hypothesis_retry_policy": None,
            "d_empty_task_evidence_policy": "fixture-only evidence audit",
            "d_empty_evidence_fields": ["abstract", "reference_evidence"],
            "d_shuffled_donor_constraints": {"eligible_split": "DEVELOPMENT"},
            "d_shuffled_assignment_algorithm": D_SHUFFLED_ALGORITHM,
            "d_shuffled_assignment_seed": D_SHUFFLED_SEED,
            "d_shuffled_within_split_only": True,
            "d_shuffled_donor_reuse_policy": "prohibited_within_assignment_batch",
            "selection_count": 3,
        }
        data.update(overrides)
        return PipelineSettings.from_mapping(data)

    def qh_preparation_settings(self):
        return self.configured(
            candidate_count=6,
            clustering_policy="complete_link_candidate_generation_order_v1",
            representative_selection_policy="earliest_candidate_generation_order",
            qh_sel_ranking_weights={
                "novelty": 0.30, "specificity": 0.25,
                "scientific_significance": 0.25, "evidence_grounding": 0.20,
            },
            qh_sel_tie_break_policy="weighted_score_desc_then_generation_order",
            random_seed=2026,
            random_sampler="sha256_key_ascending_v1",
            random_generator_and_version="SHA256",
            per_input_seed_derivation="E6-QH-RAND-v1|2026|<input_set_id>|<question_id>",
        )

    def make_candidates(self, settings=None, response=None):
        state = PipelineState()
        settings = settings or self.configured()
        model = MockModel([response or candidate_response(settings.candidate_count)])
        generate_candidates(state, settings, model, "Mock domain/task", "Mock abstract")
        return state, model

    def test_candidate_generation_renders_prompt_and_preserves_raw_and_candidates(self):
        settings = self.configured()
        raw = candidate_response()
        state, model = self.make_candidates(settings, raw)
        self.assertEqual(len(model.calls), 1)
        self.assertIn("Generate exactly 4", model.calls[0][1])
        self.assertIn("Mock abstract", model.calls[0][1])
        self.assertEqual(state.raw_responses[0]["raw"], raw)
        self.assertTrue(state.candidate_generation_complete)
        self.assertEqual([x["candidate_id"] for x in state.candidate_records], ["CQ1", "CQ2", "CQ3", "CQ4"])
        self.assertEqual(state.status, "ok")

    def test_unresolved_candidate_count_blocks_call(self):
        state = PipelineState()
        model = MockModel([])
        generate_candidates(state, PipelineSettings(), model, "task", "evidence")
        self.assertEqual(model.calls, [])
        self.assertEqual(state.errors[0]["stage"], "candidate_generation")

    def test_candidate_count_error_does_not_discard_candidates_or_raw_response(self):
        state, _ = self.make_candidates(self.configured(), candidate_response(3))
        self.assertEqual(len(state.candidate_records), 3)
        self.assertEqual(len(state.raw_responses), 1)
        self.assertFalse(state.candidate_generation_complete)
        self.assertIn("candidate count does not match", state.errors[0]["error"])

    def test_invalid_candidate_ids_are_retained_and_block_pairwise_stage(self):
        raw = json.dumps({"questions": [
            {"id": "Q1", "text": "Question one?"},
            {"id": "Q1", "text": "Question two?"},
            {"id": "Q3", "text": "Question three?"},
            {"id": "Q4", "text": "Question four?"},
        ]})
        state, _ = self.make_candidates(self.configured(), raw)
        self.assertEqual(len(state.candidate_records), 4)
        self.assertFalse(state.candidate_generation_complete)
        model = MockModel([])
        compare_candidates(state, self.configured(), model)
        self.assertEqual(model.calls, [])
        self.assertEqual(len(state.candidate_records), 4)

    def test_pairwise_dedup_runs_all_pairs_and_retains_duplicate_candidates(self):
        state, _ = self.make_candidates()
        # Six pairwise decisions, with the first two marked equivalent.
        replies = [json.dumps({"same_question": i == 0}) for i in range(6)]
        model = MockModel(replies)
        compare_candidates(state, self.configured(), model)
        self.assertEqual(len(model.calls), 6)
        self.assertEqual(len(state.pairwise_records), 6)
        self.assertEqual(state.pairwise_records[0]["decision"], "duplicate")
        self.assertEqual(len(state.candidate_records), 4)
        self.assertEqual(len(state.raw_responses), 7)  # generation plus every comparison

    def test_numeric_similarity_requires_configured_threshold(self):
        state, _ = self.make_candidates(self.configured(candidate_count=2))
        model = MockModel([json.dumps({"similarity": 0.9})])
        compare_candidates(state, self.configured(candidate_count=2), model)
        self.assertEqual(state.pairwise_records[0]["status"], "failed")
        self.assertIn("threshold is unresolved", state.errors[0]["error"])

    def test_duplicate_cluster_and_representative_policies_are_injected(self):
        state, _ = self.make_candidates()
        state.pairwise_records = [
            {"question_a": left, "question_b": right,
             "decision": "duplicate" if {left, right} == {"CQ1", "CQ2"} else "distinct",
             "status": "ok"}
            for left, right in [("CQ1", "CQ2"), ("CQ1", "CQ3"), ("CQ1", "CQ4"),
                               ("CQ2", "CQ3"), ("CQ2", "CQ4"), ("CQ3", "CQ4")]
        ]
        clusterer = lambda ids, _: [["CQ1", "CQ2"], ["CQ3"], ["CQ4"]]
        representative = lambda group, _: group[0]
        cluster_and_choose_representatives(
            state, self.configured(), clusterer, representative
        )
        self.assertEqual(state.representatives, ["CQ1", "CQ3", "CQ4"])
        self.assertEqual(state.clusters[0]["member_candidate_ids"], ["CQ1", "CQ2"])
        self.assertEqual(len(state.candidate_records), 4)

    def test_unresolved_cluster_policy_blocks_without_dropping_candidates(self):
        state, _ = self.make_candidates()
        state.pairwise_records = [{"status": "ok"}]
        cluster_and_choose_representatives(
            state, self.configured(clustering_policy=None), lambda ids, pairs: [ids], lambda g, r: g[0]
        )
        self.assertEqual(len(state.candidate_records), 4)
        self.assertIn("clustering_policy is unresolved", state.errors[0]["error"])

    def test_qh_sel_uses_injected_ranking_and_retains_scores(self):
        state, _ = self.make_candidates()
        state.representatives = ["CQ1", "CQ2", "CQ3", "CQ4"]
        ranker = lambda rows, weights: {
            "ordered_candidate_ids": ["CQ4", "CQ3", "CQ2", "CQ1"],
            "scores": {"CQ1": 1, "CQ2": 2, "CQ3": 3, "CQ4": 4},
            "raw_response": "mock ranking response",
            "fixture_weights_received": dict(weights),
        }
        select_qh_sel(state, self.configured(), ranker)
        self.assertEqual(state.selections["QH-sel"]["selected_candidate_ids"], ["CQ4", "CQ3", "CQ2"])
        self.assertEqual(state.ranking_result["scores"]["CQ4"], 4)
        self.assertEqual(state.raw_responses[-1]["raw"], "mock ranking response")

    def batch_candidate_state(self):
        state = PipelineState(candidate_generation_complete=True)
        state.candidate_records = [
            {"candidate_id": f"CQ{i}", "source_id": f"Q{i}",
             "source_index": i, "text": f"Candidate question {i}?",
             "validation_status": "valid", "validation_errors": []}
            for i in range(1, 7)
        ]
        return state

    def test_batch_dedup_covers_all_fifteen_pairs_in_one_request(self):
        state = self.batch_candidate_state()
        raw = batch_dedup_response([("CQ1", "CQ2")])
        model = MockModel([raw])
        compare_candidates_batch(state, model)
        self.assertEqual(len(model.calls), 1)
        self.assertIn('"candidate_questions"', model.calls[0][1])
        self.assertEqual(len(state.pairwise_records), 15)
        self.assertEqual(state.pairwise_records[0]["decision"], "duplicate")
        self.assertEqual(state.preparation_provenance["pairwise_deduplication"]["status"], "ok")
        self.assertEqual(state.raw_responses[0]["raw"], raw)

    def test_batch_dedup_rejects_missing_duplicate_and_non_boolean_pairs(self):
        valid = json.loads(batch_dedup_response())
        duplicate = json.loads(batch_dedup_response())
        duplicate["pairwise_comparisons"].append(dict(duplicate["pairwise_comparisons"][0]))
        non_boolean = json.loads(batch_dedup_response())
        non_boolean["pairwise_comparisons"][0]["is_duplicate"] = "false"
        missing = json.loads(batch_dedup_response())
        missing["pairwise_comparisons"].pop()
        for raw in ("not JSON", json.dumps(missing), json.dumps(duplicate), json.dumps(non_boolean)):
            with self.subTest(raw=raw[:20]):
                state = self.batch_candidate_state()
                compare_candidates_batch(state, MockModel([raw]))
                self.assertTrue(state.errors)
                self.assertFalse(state.pairwise_records)
                self.assertEqual(state.raw_responses[0]["raw"], raw)
                self.assertEqual(state.preparation_provenance["pairwise_deduplication"]["status"], "failed")
        self.assertEqual(len(valid["pairwise_comparisons"]), 15)

    def test_complete_link_clustering_uses_generation_order_and_earliest_representative(self):
        state = self.batch_candidate_state()
        duplicate_pairs = {
            frozenset(("CQ1", "CQ2")),
            frozenset(("CQ2", "CQ3")),
        }
        state.pairwise_records = [{
            "question_a": left, "question_b": right,
            "is_duplicate": frozenset((left, right)) in duplicate_pairs,
            "decision": "duplicate" if frozenset((left, right)) in duplicate_pairs else "distinct",
            "status": "ok",
        } for left, right in itertools.combinations([f"CQ{i}" for i in range(1, 7)], 2)]
        cluster_candidates_complete_link(state)
        self.assertEqual(state.clusters[0]["member_candidate_ids"], ["CQ1", "CQ2"])
        self.assertEqual(state.clusters[0]["representative_candidate_id"], "CQ1")
        self.assertEqual(state.representatives, ["CQ1", "CQ3", "CQ4", "CQ5", "CQ6"])

    def test_qh_rand_sha256_selection_is_deterministic_and_uses_exact_key(self):
        representatives = ["CQ1", "CQ3", "CQ4", "CQ5", "CQ6"]
        first = select_qh_rand_sha256(representatives, "development-input-1")
        second = select_qh_rand_sha256(representatives, "development-input-1")
        expected = sorted(
            representatives,
            key=lambda qid: hashlib.sha256(
                f"E6-QH-RAND-v1|2026|development-input-1|{qid}".encode("utf-8")
            ).hexdigest(),
        )[:3]
        self.assertEqual(first, second)
        self.assertEqual(first["selected_candidate_ids"], expected)
        self.assertEqual(first["seed"], 2026)
        self.assertTrue(all(len(item["key_sha256"]) == 64 for item in first["selection_keys"]))

    def test_preparation_shares_exact_pools_and_keeps_qh_sel_scores_out_of_qh_rand(self):
        candidates = candidate_response(6)
        dedup = batch_dedup_response([("CQ1", "CQ2")])
        representatives = ["CQ1", "CQ3", "CQ4", "CQ5", "CQ6"]
        replies = [
            {"raw_response": candidates, "input_tokens": 100, "output_tokens": 30,
             "adapter_metadata": {"http_status": 200}},
            {"raw_response": dedup, "input_tokens": 200, "output_tokens": 90,
             "adapter_metadata": {"http_status": 200}},
            {"raw_response": ranking_response(representatives), "input_tokens": 150,
             "output_tokens": 55, "adapter_metadata": {"http_status": 200}},
        ]
        model = MockModel(replies)
        state = prepare_qh_selection_arms(
            PipelineState(), self.qh_preparation_settings(), model,
            "development-input-1", "Mock domain and task", "Mock abstract evidence",
        )
        selected = state.selections
        self.assertEqual(state.preparation_provenance["status"], "ok")
        self.assertEqual([stage for stage, _ in model.calls], [
            "candidate_generation", "pairwise_deduplication_batch", "qh_sel_ranking",
        ])
        self.assertEqual(len(state.model_calls), 3)
        self.assertEqual(sum(row["output_tokens"] for row in state.model_calls), 175)
        self.assertEqual(selected["QH-sel"]["candidate_pool_sha256"],
                         selected["QH-rand"]["candidate_pool_sha256"])
        self.assertEqual(selected["QH-sel"]["representative_pool_sha256"],
                         selected["QH-rand"]["representative_pool_sha256"])
        self.assertEqual(selected["QH-sel"]["representative_ids"],
                         selected["QH-rand"]["representative_ids"])
        self.assertEqual(selected["QH-sel"]["selected_candidate_ids"], ["CQ1", "CQ3", "CQ4"])
        self.assertNotIn("scores", selected["QH-rand"])
        self.assertNotIn("ranking_result", selected["QH-rand"])
        self.assertEqual(len(state.raw_responses), 3)

    def test_insufficient_representatives_blocks_both_selections_before_ranking(self):
        duplicates = [
            ("CQ1", "CQ2"), ("CQ1", "CQ3"), ("CQ2", "CQ3"),
            ("CQ4", "CQ5"), ("CQ4", "CQ6"), ("CQ5", "CQ6"),
        ]
        model = MockModel([candidate_response(6), batch_dedup_response(duplicates)])
        state = prepare_qh_selection_arms(
            PipelineState(), self.qh_preparation_settings(), model,
            "development-input-2", "Mock task", "Mock evidence",
        )
        self.assertEqual(len(model.calls), 2)
        self.assertEqual(len(state.representatives), 2)
        self.assertEqual(state.selections["QH-sel"]["status"], "blocked_insufficient_representatives")
        self.assertEqual(state.selections["QH-rand"]["status"], "blocked_insufficient_representatives")

    def test_invalid_qh_sel_scores_fail_qh_sel_without_changing_qh_rand_pool(self):
        model = MockModel([
            candidate_response(6), batch_dedup_response(),
            json.dumps({"scores": [{"question_id": "CQ1", "novelty": 9}]}),
        ])
        state = prepare_qh_selection_arms(
            PipelineState(), self.qh_preparation_settings(), model,
            "development-input-3", "Mock task", "Mock evidence",
        )
        self.assertEqual(state.selections["QH-sel"]["status"], "failed_ranking")
        self.assertEqual(state.selections["QH-rand"]["status"], "ok")
        self.assertEqual(state.raw_responses[-1]["stage"], "qh_sel_ranking")
        self.assertEqual(state.selections["QH-rand"]["representative_ids"], state.representatives)

    def test_settings_file_records_approved_retry_and_selection_policies(self):
        settings = PipelineSettings.load()
        self.assertEqual(settings.candidate_count, 6)
        self.assertIsNone(settings.deduplication_threshold)
        self.assertEqual(settings.clustering_policy, "complete_link_candidate_generation_order_v1")
        self.assertEqual(settings.representative_selection_policy, "earliest_candidate_generation_order")
        self.assertEqual(settings.qh_sel_ranking_weights, {
            "novelty": 0.3, "specificity": 0.25,
            "scientific_significance": 0.25, "evidence_grounding": 0.2,
        })
        self.assertEqual(settings.random_seed, 2026)
        self.assertEqual(settings.random_sampler, "sha256_key_ascending_v1")
        self.assertEqual(settings.random_generator_and_version, "SHA256")
        self.assertEqual(settings.per_input_seed_derivation,
                         "E6-QH-RAND-v1|2026|<input_set_id>|<question_id>")
        self.assertEqual(settings.selected_hypothesis_max_attempts, 1)
        self.assertEqual(settings.selected_hypothesis_retry_policy, "none")
        self.assertEqual(settings.arm_hypothesis_max_attempts, 1)
        self.assertEqual(settings.arm_hypothesis_retry_policy, "none")
        self.assertEqual(settings.d_empty_evidence_fields, ["abstract", "reference_evidence"])
        self.assertEqual(settings.d_shuffled_assignment_algorithm, D_SHUFFLED_ALGORITHM)
        self.assertEqual(settings.d_shuffled_assignment_seed, D_SHUFFLED_SEED)
        self.assertTrue(settings.d_shuffled_within_split_only)
        self.assertEqual(settings.d_shuffled_donor_reuse_policy, "prohibited_within_assignment_batch")

    def test_qh_rand_is_reproducible_for_an_explicit_fixture_seed(self):
        state, _ = self.make_candidates()
        state.representatives = ["CQ1", "CQ2", "CQ3", "CQ4"]
        settings = self.configured(random_seed=77)
        fixture_sampler = lambda ids, count, seed: random.Random(seed).sample(list(ids), count)
        select_qh_rand(state, settings, fixture_sampler, "fixture-only Python RNG")
        first = state.selections["QH-rand"]["selected_candidate_ids"]
        other = PipelineState(representatives=list(state.representatives))
        select_qh_rand(other, settings, fixture_sampler, "fixture-only Python RNG")
        self.assertEqual(first, other.selections["QH-rand"]["selected_candidate_ids"])
        self.assertEqual(other.selections["QH-rand"]["seed"], 77)

    def test_fewer_than_three_unique_questions_is_blocked_and_preserved(self):
        state, _ = self.make_candidates()
        state.representatives = ["CQ1", "CQ3"]
        fixture_sampler = lambda ids, count, seed: random.Random(seed).sample(list(ids), count)
        select_qh_rand(state, self.configured(), fixture_sampler, "fixture-only Python RNG")
        self.assertEqual(state.selections["QH-rand"]["status"], "blocked_insufficient_unique_questions")
        self.assertEqual(len(state.candidate_records), 4)

    def test_qh_rand_requires_sampler_implementation(self):
        state, _ = self.make_candidates()
        state.representatives = ["CQ1", "CQ2", "CQ3", "CQ4"]
        select_qh_rand(state, self.configured(), None, None)
        self.assertIn("random sampler and version must be injected", state.errors[0]["error"])

    def test_pairwise_failure_is_recorded_not_silently_skipped(self):
        state, _ = self.make_candidates(self.configured(candidate_count=2))
        model = MockModel([RuntimeError("mock failure")])
        compare_candidates(state, self.configured(candidate_count=2), model)
        self.assertEqual(len(state.pairwise_records), 1)
        self.assertEqual(state.pairwise_records[0]["status"], "failed")
        self.assertTrue(state.errors)

    def selected_questions(self):
        return [
            {"question_id": f"CQ{i}", "text": f"Selected question {i}?"}
            for i in range(1, 4)
        ]

    def nested_hypothesis_response(self, arm, duplicate_hypothesis_id=False,
                                   wrong_question_id=None, omit_hypotheses=False):
        questions = []
        hypothesis_number = 1
        for index, selected in enumerate(self.selected_questions(), start=1):
            question_id = wrong_question_id if index == 2 and wrong_question_id else f"Q{index}"
            hypotheses = []
            if not (omit_hypotheses and index == 1):
                for _ in range(2):
                    current_id = f"H{hypothesis_number}"
                    if duplicate_hypothesis_id and hypothesis_number == 2:
                        current_id = "H1"
                    hypotheses.append({
                        "id": current_id,
                        "text": f"Hypothesis {hypothesis_number} predicts a distinct measurable outcome.",
                    })
                    hypothesis_number += 1
            questions.append({
                "id": question_id,
                "text": selected["text"],
                "hypotheses": hypotheses,
            })
        return json.dumps({"arm": arm, "questions": questions})

    def run_hypothesis_generation(self, arm, response, settings=None, retry_builder=None):
        state = PipelineState()
        model = MockModel([response] if not isinstance(response, list) else response)
        generate_question_hypotheses(
            state, arm, self.selected_questions(), model,
            "Mock domain/task", "Mock evidence", settings or self.configured(),
            retry_prompt_builder=retry_builder,
        )
        return state, model

    def test_qh_sel_uses_existing_prompt_and_returns_six_linked_stable_hypotheses(self):
        raw = self.nested_hypothesis_response("QH-sel")
        state, model = self.run_hypothesis_generation("QH-sel", raw)
        generation = state.hypothesis_generations[0]
        self.assertEqual(generation["status"], "ok")
        self.assertEqual(len(generation["hypotheses"]), 6)
        self.assertEqual(generation["hypotheses"][0]["hypothesis_id"], "QH-sel:H1")
        self.assertEqual(generation["hypotheses"][0]["question_id"], "CQ1")
        self.assertEqual(generation["hypotheses"][2]["question_id"], "CQ2")
        self.assertEqual(generation["raw_response"], raw)
        self.assertIn("You are an AI research scientist", model.calls[0][1])
        self.assertIn("Selected question 1?", model.calls[0][1])

    def test_qh_rand_uses_arm_specific_prompt_and_keeps_arm_identity(self):
        raw = self.nested_hypothesis_response("QH-rand")
        state, model = self.run_hypothesis_generation("QH-rand", raw)
        generation = state.hypothesis_generations[0]
        self.assertEqual(generation["arm"], "QH-rand")
        self.assertTrue(all(item["hypothesis_id"].startswith("QH-rand:") for item in generation["hypotheses"]))
        self.assertIn("three randomly selected research questions", model.calls[0][1])
        self.assertNotIn("touch prompts/e6", model.calls[0][1])

    def test_flat_shared_prompt_schema_preserves_explicit_question_references(self):
        hypotheses = []
        for index in range(1, 4):
            for offset in range(2):
                n = (index - 1) * 2 + offset + 1
                hypotheses.append({
                    "id": f"H{n}", "question_id": f"CQ{index}",
                    "text": f"Hypothesis {n} predicts a measurable outcome.",
                })
        raw = json.dumps({"hypotheses": hypotheses})
        # Use the shared template explicitly while retaining the same response normalizer.
        state = PipelineState()
        model = MockModel([raw])
        generate_question_hypotheses(
            state, "QH-sel", self.selected_questions(), model,
            "Mock task", "Mock evidence", self.configured(),
            prompt_path="prompts/e6/03_hypotheses_from_questions.txt",
        )
        generation = state.hypothesis_generations[0]
        self.assertEqual(generation["status"], "ok")
        self.assertEqual([h["question_id"] for h in generation["hypotheses"]],
                         ["CQ1", "CQ1", "CQ2", "CQ2", "CQ3", "CQ3"])

    def test_malformed_json_is_retried_with_history_and_raw_responses(self):
        good = self.nested_hypothesis_response("QH-sel")
        settings = self.configured(
            selected_hypothesis_max_attempts=2,
            selected_hypothesis_retry_policy="fixture-retry",
        )
        builder_calls = []

        def retry_builder(base_prompt, previous_raw, errors, attempt):
            builder_calls.append((previous_raw, list(errors), attempt))
            return base_prompt + "\nMock retry instruction."

        state, model = self.run_hypothesis_generation(
            "QH-sel", ["{malformed", good], settings, retry_builder
        )
        generation = state.hypothesis_generations[0]
        self.assertEqual(generation["status"], "ok")
        self.assertEqual(len(generation["attempt_history"]), 2)
        self.assertEqual(generation["attempt_history"][0]["raw_response"], "{malformed")
        self.assertTrue(generation["attempt_history"][0]["validation_errors"])
        self.assertEqual(generation["attempt_history"][1]["parsed_output"]["arm"], "QH-sel")
        self.assertEqual(len(state.raw_responses), 2)
        self.assertEqual(builder_calls[0][0], "{malformed")
        self.assertEqual(builder_calls[0][2], 2)
        self.assertEqual(len(model.calls), 2)

    def test_missing_hypotheses_and_duplicate_ids_are_validation_failures(self):
        missing = self.nested_hypothesis_response("QH-sel", omit_hypotheses=True)
        state, _ = self.run_hypothesis_generation("QH-sel", missing)
        self.assertEqual(state.hypothesis_generations[0]["status"], "failed")
        self.assertTrue(state.hypothesis_generations[0]["attempt_history"][0]["validation_errors"])

        duplicate = self.nested_hypothesis_response("QH-rand", duplicate_hypothesis_id=True)
        state, _ = self.run_hypothesis_generation("QH-rand", duplicate)
        self.assertEqual(state.hypothesis_generations[0]["status"], "failed")
        self.assertIn("unique and consecutive", state.hypothesis_generations[0]["errors"][0])

    def test_invalid_question_references_are_rejected(self):
        nested = self.nested_hypothesis_response("QH-sel", wrong_question_id="Q9")
        state, _ = self.run_hypothesis_generation("QH-sel", nested)
        self.assertEqual(state.hypothesis_generations[0]["status"], "failed")
        self.assertIn("invalid or duplicate question reference", state.hypothesis_generations[0]["errors"][0])

        flat = [{"id": f"H{i}", "question_id": "UNKNOWN", "text": "Testable hypothesis."}
                for i in range(1, 7)]
        state = PipelineState()
        generate_question_hypotheses(
            state, "QH-rand", self.selected_questions(), MockModel([json.dumps({"hypotheses": flat})]),
            "Mock task", "Mock evidence", self.configured(),
            prompt_path="prompts/e6/03_hypotheses_from_questions.txt",
        )
        self.assertIn("invalid question reference", state.hypothesis_generations[0]["errors"][0])

    def test_word_limit_and_retry_configuration_are_enforced(self):
        long_text = " ".join(["word"] * 51)
        raw = self.nested_hypothesis_response("QH-sel")
        parsed = json.loads(raw)
        parsed["questions"][0]["hypotheses"][0]["text"] = long_text
        state, _ = self.run_hypothesis_generation("QH-sel", json.dumps(parsed))
        self.assertIn("50-word", state.hypothesis_generations[0]["errors"][0])

        state, model = self.run_hypothesis_generation(
            "QH-sel", self.nested_hypothesis_response("QH-sel"),
            self.configured(selected_hypothesis_max_attempts=None),
        )
        self.assertEqual(model.calls, [])
        self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")

    def test_selection_can_be_resolved_from_existing_pipeline_state(self):
        state, _ = self.make_candidates()
        state.selections["QH-sel"] = {
            "status": "ok", "selected_candidate_ids": ["CQ3", "CQ1", "CQ4"],
        }
        selected = selected_questions_for_arm(state, "QH-sel")
        self.assertEqual([item["question_id"] for item in selected], ["CQ3", "CQ1", "CQ4"])

    def direct_response(self):
        return json.dumps({"hypotheses": [
            {"id": f"H{i}", "text": f"Direct hypothesis {i} predicts a measurable outcome."}
            for i in range(1, 7)
        ]})

    def qh_response(self, missing_hypotheses=False, duplicate_hypothesis_id=False):
        questions = []
        number = 1
        for q in range(1, 4):
            items = []
            if not (missing_hypotheses and q == 2):
                for _ in range(2):
                    hyp_id = f"H{number}"
                    if duplicate_hypothesis_id and number == 4:
                        hyp_id = "H3"
                    items.append({"id": hyp_id, "text": f"QH hypothesis {number} predicts an outcome."})
                    number += 1
            questions.append({
                "id": f"Q{q}", "text": f"QH research question {q}?", "hypotheses": items,
            })
        return json.dumps({"arm": "QH", "questions": questions})

    def hq_response(self, invalid_reference=False, missing_question=False):
        hypotheses = [
            {"id": f"H{i}", "text": f"HQ hypothesis {i} predicts an outcome."}
            for i in range(1, 7)
        ]
        questions = [
            {"hypothesis_id": "H99" if invalid_reference and i == 3 else f"H{i}",
             "text": f"Research question for hypothesis {i}?"}
            for i in range(1, 7)
        ]
        if missing_question:
            questions.pop()
        return json.dumps({"hypotheses": hypotheses, "questions": questions})

    def run_direct_arm(self, arm, response, settings=None, retry_builder=None):
        state = PipelineState()
        model = MockModel([response] if not isinstance(response, list) else response)
        generate_direct_arm(
            state, arm, model, "Mock domain/task", "Mock evidence",
            settings or self.configured(), retry_prompt_builder=retry_builder,
        )
        return state, model

    def test_direct_d_generates_six_stable_hypotheses_and_preserves_raw_output(self):
        raw = self.direct_response()
        state, model = self.run_direct_arm("D", raw)
        result = state.hypothesis_generations[0]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["hypotheses"]), 6)
        self.assertEqual(result["hypotheses"][0]["hypothesis_id"], "D:H1")
        self.assertIsNone(result["hypotheses"][0]["question_id"])
        self.assertEqual(result["raw_response"], raw)
        self.assertIn("Mock evidence", model.calls[0][1])
        self.assertEqual(result["parsed_output"]["hypotheses"][5]["id"], "H6")

    def test_qh_generates_three_questions_and_two_linked_hypotheses_each(self):
        raw = self.qh_response()
        state, model = self.run_direct_arm("QH", raw)
        result = state.hypothesis_generations[0]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["questions"]), 3)
        self.assertEqual(len(result["hypotheses"]), 6)
        self.assertEqual([h["question_id"] for h in result["hypotheses"]],
                         ["QH:Q1", "QH:Q1", "QH:Q2", "QH:Q2", "QH:Q3", "QH:Q3"])
        self.assertEqual(result["hypotheses"][2]["hypothesis_id"], "QH:H3")
        self.assertEqual(result["raw_response"], raw)
        self.assertEqual(model.calls[0][0], "QH_generation")

    def test_hq_generates_six_hypotheses_and_one_question_per_hypothesis(self):
        raw = self.hq_response()
        state, _ = self.run_direct_arm("HQ", raw)
        result = state.hypothesis_generations[0]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["hypotheses"]), 6)
        self.assertEqual(len(result["questions"]), 6)
        self.assertEqual(result["hypotheses"][2]["question_id"], "HQ:Q3")
        self.assertEqual(result["hypotheses"][2]["question_text"], "Research question for hypothesis 3?")
        self.assertEqual(result["questions"][5]["source_hypothesis_id"], "H6")

    def test_direct_workflow_retries_and_preserves_each_attempt(self):
        settings = self.configured(
            arm_hypothesis_max_attempts=2,
            arm_hypothesis_retry_policy="fixture-arm-retry",
        )
        calls = []

        def retry_builder(base_prompt, previous_raw, errors, attempt):
            calls.append((previous_raw, list(errors), attempt))
            return base_prompt + "\nMock correction."

        good = self.direct_response()
        state, model = self.run_direct_arm("D", ["invalid json", good], settings, retry_builder)
        result = state.hypothesis_generations[0]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["attempt_history"]), 2)
        self.assertEqual(result["attempt_history"][0]["raw_response"], "invalid json")
        self.assertTrue(result["attempt_history"][0]["validation_errors"])
        self.assertEqual(result["attempt_history"][1]["normalized_output"]["arm"], "D")
        self.assertEqual(len(state.raw_responses), 2)
        self.assertEqual(calls[0][0], "invalid json")
        self.assertEqual(len(model.calls), 2)

    def test_qh_missing_hypotheses_and_duplicate_ids_are_rejected(self):
        state, _ = self.run_direct_arm("QH", self.qh_response(missing_hypotheses=True))
        self.assertEqual(state.hypothesis_generations[0]["status"], "failed")
        self.assertTrue(state.hypothesis_generations[0]["attempt_history"][0]["validation_errors"])

        state, _ = self.run_direct_arm("QH", self.qh_response(duplicate_hypothesis_id=True))
        self.assertEqual(state.hypothesis_generations[0]["status"], "failed")

    def test_hq_missing_and_invalid_question_links_are_rejected(self):
        state, _ = self.run_direct_arm("HQ", self.hq_response(missing_question=True))
        self.assertEqual(state.hypothesis_generations[0]["status"], "failed")
        state, _ = self.run_direct_arm("HQ", self.hq_response(invalid_reference=True))
        self.assertEqual(state.hypothesis_generations[0]["status"], "failed")
        self.assertIn("invalid hypothesis reference", state.hypothesis_generations[0]["errors"][0])

    def test_direct_contract_rejects_malformed_json_duplicate_ids_and_wrong_counts(self):
        for response in (
            "{malformed",
            json.dumps({"hypotheses": [{"id": "H1", "text": "Only one."}]}),
            json.dumps({"hypotheses": [
                {"id": "H1" if i == 2 else f"H{i}", "text": f"Hypothesis {i}."}
                for i in range(1, 7)
            ]}),
        ):
            state, _ = self.run_direct_arm("D", response)
            self.assertEqual(state.hypothesis_generations[0]["status"], "failed")
            self.assertTrue(state.hypothesis_generations[0]["attempt_history"][0]["validation_errors"])

    def test_unresolved_arm_retry_settings_block_client_call(self):
        state, model = self.run_direct_arm(
            "HQ", self.hq_response(), self.configured(arm_hypothesis_max_attempts=None)
        )
        self.assertEqual(model.calls, [])
        self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")

    def controls_response(self, arm):
        return json.dumps({
            "arm": arm,
            "hypotheses": [
                {"id": f"H{i}", "text": f"{arm} hypothesis {i} predicts a measurable outcome."}
                for i in range(1, 7)
            ],
        })

    def d_empty_audit_fixture(self, recipient="2501.00001", task="Retained task.",
                              abstract="Original abstract.", references=None):
        references = [] if references is None else references
        hash_text = lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest()
        hash_json = lambda value: hashlib.sha256(json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest()
        return {
            "trust_status": "mock_fixture_untrusted",
            "auditor_id": "mock-only",
            "audit_id": "fixture-only",
            "audit_complete": True,
            "audit_scope": "retained_task_domain_text",
            "leakage_check_performed": True,
            "retained_task_leakage_detected": False,
            "recipient_id": recipient,
            "scrubbed_task_sha256": hash_text(task),
            "removed_fields": ["abstract", "reference_evidence"],
            "removed_evidence_sha256": {
                "abstract": hash_text(abstract),
                "reference_evidence": hash_json(list(references)),
            },
            "rendered_evidence": "",
        }

    def run_d_empty_with_mock_audit(self, audit):
        auditor = FixtureDEmptyAuditor(TrustedDEmptyAuditResult(**audit))
        model = MockModel([self.controls_response("D-empty")])
        state = PipelineState()
        generate_d_empty(
            state, "2501.00001", "Retained task.", model, self.configured(), auditor,
            original_abstract="Original abstract.", reference_evidence=[],
        )
        return state, model, auditor

    def test_d_empty_plain_mock_callback_is_rejected_before_invocation_or_generation(self):
        called = []
        model = MockModel([self.controls_response("D-empty")])
        state = PipelineState()
        generate_d_empty(
            state, "2501.00001", "Retained task.", model,
            self.configured(), lambda *args: called.append(args) or self.d_empty_audit_fixture(),
            original_abstract="Original abstract.", reference_evidence=[],
        )
        self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
        self.assertIn("trusted production D-empty auditor is not configured", state.errors[0]["error"])
        self.assertEqual(called, [])
        self.assertEqual(model.calls, [])

    def test_d_empty_mock_spec_auditor_is_not_a_trusted_provider(self):
        auditor = Mock(spec=TrustedDEmptyEvidenceAuditor)
        auditor.audit.return_value = TrustedDEmptyAuditResult(
            trust_status="trusted_production", auditor_id="mock", audit_id="mock",
            audit_complete=True, audit_scope="retained_task_domain_text",
            leakage_check_performed=True, retained_task_leakage_detected=False,
            recipient_id="2501.00001", scrubbed_task_sha256="0" * 64,
            removed_fields=["abstract", "reference_evidence"],
            removed_evidence_sha256={"abstract": "0" * 64, "reference_evidence": "0" * 64},
            rendered_evidence="",
        )
        model = MockModel([self.controls_response("D-empty")])
        state = PipelineState()
        generate_d_empty(
            state, "2501.00001", "Retained task.", model, self.configured(), auditor,
            original_abstract="Original abstract.", reference_evidence=[],
        )
        self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
        self.assertFalse(auditor.audit.called)
        self.assertEqual(model.calls, [])

    def test_d_empty_removed_fields_rejects_mappings_strings_tuples_and_null(self):
        malformed = (
            {"abstract": True, "reference_evidence": True},
            "abstract",
            ("abstract", "reference_evidence"),
            None,
        )
        for removed_fields in malformed:
            with self.subTest(removed_fields=removed_fields):
                audit = self.d_empty_audit_fixture()
                audit["removed_fields"] = removed_fields
                errors = _d_empty_audit_validation_errors(
                    audit, "2501.00001", "Retained task.",
                    hashlib.sha256(b"Original abstract.").hexdigest(),
                    hashlib.sha256(b"[]").hexdigest(),
                )
                self.assertTrue(any("actual list" in error for error in errors))
                state, model, _ = self.run_d_empty_with_mock_audit(audit)
                self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
                self.assertEqual(model.calls, [])

    def test_d_empty_removed_fields_rejects_empty_and_non_string_entries(self):
        for removed_fields in (["abstract", ""], ["abstract", 42], ["abstract", None]):
            with self.subTest(removed_fields=removed_fields):
                audit = self.d_empty_audit_fixture()
                audit["removed_fields"] = removed_fields
                errors = _d_empty_audit_validation_errors(
                    audit, "2501.00001", "Retained task.",
                    hashlib.sha256(b"Original abstract.").hexdigest(),
                    hashlib.sha256(b"[]").hexdigest(),
                )
                self.assertTrue(any("nonempty string" in error for error in errors))
                state, model, _ = self.run_d_empty_with_mock_audit(audit)
                self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
                self.assertEqual(model.calls, [])

    def test_d_empty_removed_fields_rejects_duplicates_and_missing_fields(self):
        for removed_fields in (
            ["abstract", "reference_evidence", "abstract"],
            ["abstract"],
            ["reference_evidence"],
            [],
        ):
            with self.subTest(removed_fields=removed_fields):
                audit = self.d_empty_audit_fixture()
                audit["removed_fields"] = removed_fields
                errors = _d_empty_audit_validation_errors(
                    audit, "2501.00001", "Retained task.",
                    hashlib.sha256(b"Original abstract.").hexdigest(),
                    hashlib.sha256(b"[]").hexdigest(),
                )
                if len(removed_fields) != len(set(removed_fields)):
                    self.assertTrue(any("unique" in error for error in errors))
                else:
                    self.assertTrue(any("exactly abstract and reference_evidence" in error for error in errors))
                state, model, _ = self.run_d_empty_with_mock_audit(audit)
                self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
                self.assertEqual(model.calls, [])

    def test_d_empty_audit_hash_and_recipient_bindings_are_independently_checked(self):
        expected_abstract = hashlib.sha256(b"Original abstract.").hexdigest()
        expected_references = hashlib.sha256(b"[]").hexdigest()
        for field, value, expected_error in (
            ("recipient_id", "different-id", "recipient ID"),
            ("scrubbed_task_sha256", "0" * 64, "scrubbed-task hash"),
            ("removed_evidence_sha256", {"abstract": "0" * 64,
                                          "reference_evidence": expected_references},
             "removed evidence hashes"),
            ("removed_evidence_sha256", {"abstract": expected_abstract,
                                          "reference_evidence": "0" * 64},
             "removed evidence hashes"),
        ):
            with self.subTest(field=field, value=value):
                audit = self.d_empty_audit_fixture()
                audit[field] = value
                errors = _d_empty_audit_validation_errors(
                    audit, "2501.00001", "Retained task.", expected_abstract, expected_references,
                )
                self.assertTrue(any(expected_error in error for error in errors))
                state, model, _ = self.run_d_empty_with_mock_audit(audit)
                self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
                self.assertEqual(model.calls, [])

    def test_d_empty_untrusted_mock_fixture_is_never_a_trusted_audit_result(self):
        audit = self.d_empty_audit_fixture()
        errors = _d_empty_audit_validation_errors(
            audit, "2501.00001", "Retained task.", audit["removed_evidence_sha256"]["abstract"],
            audit["removed_evidence_sha256"]["reference_evidence"],
        )
        self.assertTrue(any("not explicitly marked trusted production" in error for error in errors))
        self.assertEqual(audit["trust_status"], "mock_fixture_untrusted")

    def test_d_empty_unresolved_policy_blocks_generation(self):
        model = MockModel([])
        state = PipelineState()
        generate_d_empty(
            state, "target-123", "Approved task", model,
            self.configured(d_empty_task_evidence_policy=None), None,
            original_abstract="Original abstract.", reference_evidence=[],
        )
        self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
        self.assertEqual(model.calls, [])

    def donor_check(self, target, donor, provenance, constraints):
        return {
            "passed": target != donor and constraints.get("eligible_split") == "DEVELOPMENT",
            "recipient_id": target,
            "recipient_split": "DEVELOPMENT",
            "donor_id": donor,
            "donor_split": "DEVELOPMENT",
            "evidence_sha256": provenance.get("evidence_sha256"),
            "source_record_sha256": provenance.get("source_record_sha256"),
        }

    def donor_assignment_provenance(self, target, donor, evidence="Exact donor abstract text."):
        key = f"E6-D-SHUFFLED-v1|{D_SHUFFLED_SEED}|{target}|{donor}"
        evidence_hash = hashlib.sha256(evidence.encode("utf-8")).hexdigest()
        source_hash = "a" * 64
        return {
            "recipient_id": target,
            "recipient_split": "DEVELOPMENT",
            "donor_id": donor,
            "donor_split": "DEVELOPMENT",
            "seed": D_SHUFFLED_SEED,
            "assignment_algorithm": D_SHUFFLED_ALGORITHM,
            "assignment_key": key,
            "assignment_key_sha256": hashlib.sha256(key.encode("utf-8")).hexdigest(),
            "evidence_sha256": evidence_hash,
            "abstract_sha256": evidence_hash,
            "source_record_sha256": source_hash,
            "donor_source_version_ids": [donor + "v1"],
            "assignment_batch_id": "fixture-batch",
            "source_verification": {
                "passed": True,
                "canonical_source_record_sha256": source_hash,
                "abstract_sha256": evidence_hash,
            },
        }

    def test_d_shuffled_accepts_external_donor_and_preserves_assignment_provenance(self):
        assignment = {
            **self.donor_assignment_provenance("target-123", "donor-456"),
            "external_assignment_id": "mock-assignment-7",
        }
        raw = self.controls_response("D-shuffled")
        state = PipelineState()
        model = MockModel([raw])
        generate_d_shuffled(
            state, "target-123", "donor-456", "Target research task",
            "Exact donor abstract text.", assignment, model, self.configured(), self.donor_check,
            recipient_split="DEVELOPMENT",
        )
        result = state.hypothesis_generations[0]
        self.assertEqual(result["status"], "blocked")
        self.assertIn("paper ID is invalid", result["errors"][0])
        self.assertEqual(model.calls, [])

    def test_d_shuffled_same_paper_or_failed_donor_check_blocks_model_call(self):
        for donor_id, checker, expected in (
            ("target-123", self.donor_check, "must differ"),
            ("donor-456", lambda *_: {"passed": False, "reason": "split constraint"},
             "did not pass configured constraints"),
        ):
            assignment = self.donor_assignment_provenance("target-123", donor_id, "Donor abstract")
            state = PipelineState()
            model = MockModel([])
            generate_d_shuffled(
                state, "target-123", donor_id, "Task", "Donor abstract", assignment,
                model, self.configured(), checker, recipient_split="DEVELOPMENT",
            )
            self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
            self.assertIn("paper ID is invalid", state.hypothesis_generations[0]["errors"][0])
            self.assertEqual(model.calls, [])

    def test_d_shuffled_assignment_provenance_must_match_target_and_donor(self):
        state = PipelineState()
        model = MockModel([])
        generate_d_shuffled(
            state, "target-1", "donor-2", "Task", "Donor evidence",
            self.donor_assignment_provenance("different-target", "donor-2", "Donor evidence"),
            model, self.configured(), self.donor_check, recipient_split="DEVELOPMENT",
        )
        self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
        self.assertIn("paper ID is invalid", state.hypothesis_generations[0]["errors"][0])
        self.assertEqual(model.calls, [])

    def test_d_shuffled_requires_external_provenance_and_unresolved_constraints(self):
        for settings, assignment, checker in (
            (self.configured(), {}, self.donor_check),
            (self.configured(d_shuffled_donor_constraints=None), {"assignment_id": "x"}, self.donor_check),
        ):
            state = PipelineState()
            model = MockModel([])
            generate_d_shuffled(
                state, "target-1", "donor-2", "Task", "Donor abstract", assignment,
                model, settings, checker, recipient_split="DEVELOPMENT",
            )
            self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
            self.assertEqual(model.calls, [])

    def test_d_shuffled_rejects_missing_provenance_and_cross_split(self):
        state = PipelineState()
        model = MockModel([])
        generate_d_shuffled(
            state, "target-1", "donor-2", "Task", "Donor abstract", {},
            model, self.configured(), self.donor_check, recipient_split="DEVELOPMENT",
        )
        self.assertIn("paper ID is invalid", state.errors[0]["error"])
        self.assertEqual(model.calls, [])

        provenance = self.donor_assignment_provenance("target-1", "donor-2", "Donor abstract")
        provenance["donor_split"] = "FINAL_EVALUATION"
        state = PipelineState()
        generate_d_shuffled(
            state, "target-1", "donor-2", "Task", "Donor abstract", provenance,
            model, self.configured(), self.donor_check, recipient_split="DEVELOPMENT",
        )
        self.assertIn("paper ID is invalid", state.errors[-1]["error"])
        self.assertEqual(model.calls, [])

    def test_d_shuffled_rejects_donor_evidence_hash_mismatch(self):
        provenance = self.donor_assignment_provenance("target-1", "donor-2", "Different abstract")
        state = PipelineState()
        model = MockModel([])
        generate_d_shuffled(
            state, "target-1", "donor-2", "Task", "Donor abstract", provenance,
            model, self.configured(), self.donor_check, recipient_split="DEVELOPMENT",
        )
        self.assertIn("paper ID is invalid", state.errors[-1]["error"])
        self.assertEqual(model.calls, [])

    def development_assignment_fixtures(self, count=4):
        records, sources = [], {}
        for index in range(1, count + 1):
            paper_id = f"2501.{index:05d}"
            source = {
                "paper_id": paper_id + "v1",
                "abstract": f"Canonical source abstract {index}.",
                "title": f"Source title {index}",
            }
            source_bytes = json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            abstract_hash = hashlib.sha256(source["abstract"].encode("utf-8")).hexdigest()
            record = {
                "paper_id": paper_id, "split": "DEVELOPMENT", "abstract": source["abstract"],
                "abstract_sha256": abstract_hash,
                "source_record_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "source_version_ids": [paper_id + "v1"],
                "eligibility": {
                    "nonempty_abstract": True,
                    "metadata_conflict": False,
                    "in_focal_exclusion_set": False,
                },
            }
            records.append(record)
            sources[paper_id] = source
        return records, sources

    def assignment_expected_hashes(self, records, sources):
        manifest_hash = hashlib.sha256(json.dumps(
            records, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest()
        corpus_hash = hashlib.sha256(json.dumps(
            {key: sources[key] for key in sorted(sources)}, ensure_ascii=False,
            sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest()
        return {"expected_manifest_sha256": manifest_hash,
                "expected_source_corpus_sha256": corpus_hash}

    def test_d_shuffled_assignment_is_deterministic_and_validates_full_batch(self):
        records, sources = self.development_assignment_fixtures()
        hashes = self.assignment_expected_hashes(records, sources)
        first = assign_d_shuffled_donors(records, records, sources, **hashes)
        second = assign_d_shuffled_donors(records, records, sources, **hashes)
        self.assertEqual(first, second)
        validation = validate_d_shuffled_assignment_batch(first, records, records, sources, **hashes)
        self.assertTrue(validation["passed"])
        self.assertEqual(first["seed"], 2026)
        self.assertEqual(first["recipient_ids_canonical_order"], sorted(row["paper_id"] for row in records))
        self.assertEqual(len({row["donor_id"] for row in first["assignments"]}), len(records))
        self.assertTrue(all(row["recipient_id"] != row["donor_id"] for row in first["assignments"]))

    def test_d_shuffled_assignment_rejects_cross_split_source_mismatch_and_reuse(self):
        records, sources = self.development_assignment_fixtures()
        cross_split = [dict(row) for row in records]
        cross_split[-1]["split"] = "FINAL_EVALUATION"
        with self.assertRaisesRegex(ValueError, "not in the DEVELOPMENT split"):
            assign_d_shuffled_donors(records, cross_split, sources, **self.assignment_expected_hashes(cross_split, sources))

        wrong_hash = [dict(row) for row in records]
        wrong_hash[0]["abstract_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "abstract hash does not match"):
            assign_d_shuffled_donors(records, wrong_hash, sources, **self.assignment_expected_hashes(wrong_hash, sources))

        wrong_source = {key: dict(value) for key, value in sources.items()}
        wrong_source[records[0]["paper_id"]]["abstract"] = "Changed source evidence."
        with self.assertRaisesRegex(ValueError, "evidence differs from its canonical source record"):
            assign_d_shuffled_donors(records, records, wrong_source, **self.assignment_expected_hashes(records, wrong_source))

        hashes = self.assignment_expected_hashes(records, sources)
        batch = assign_d_shuffled_donors(records, records, sources, **hashes)
        batch["assignments"][1]["donor_id"] = batch["assignments"][0]["donor_id"]
        with self.assertRaisesRegex(ValueError, "donor reuse is prohibited"):
            validate_d_shuffled_assignment_batch(batch, records, records, sources, **hashes)

    def test_d_shuffled_assignment_rejects_missing_canonical_source_provenance(self):
        records, sources = self.development_assignment_fixtures()
        with self.assertRaisesRegex(ValueError, "canonical source record is missing"):
            assign_d_shuffled_donors(records, records, {}, **self.assignment_expected_hashes(records, {}))

    def test_d_shuffled_integrity_negative_cases(self):
        records, sources = self.development_assignment_fixtures()
        hashes = self.assignment_expected_hashes(records, sources)
        noncanonical = [dict(row) for row in records]
        noncanonical[0]["paper_id"] += "v1"
        with self.assertRaisesRegex(ValueError, "must be canonical"):
            assign_d_shuffled_donors(noncanonical, records, sources, **hashes)
        with self.assertRaisesRegex(ValueError, "expected hash"):
            assign_d_shuffled_donors(records, records, sources,
                expected_manifest_sha256="0" * 64,
                expected_source_corpus_sha256=hashes["expected_source_corpus_sha256"])
        wrong_source_id = {key: dict(value) for key, value in sources.items()}
        wrong_source_id[records[0]["paper_id"]]["paper_id"] = "2501.99999"
        with self.assertRaisesRegex(ValueError, "source record ID mismatch"):
            assign_d_shuffled_donors(records, records, wrong_source_id,
                **self.assignment_expected_hashes(records, wrong_source_id))

        batch = assign_d_shuffled_donors(records, records, sources, **hashes)
        altered_records = [dict(row) for row in records]
        altered_records[0]["eligibility"] = {"nonempty_abstract": True,
            "metadata_conflict": True, "in_focal_exclusion_set": False}
        altered_hashes = self.assignment_expected_hashes(altered_records, sources)
        batch["manifest_sha256"] = altered_hashes["expected_manifest_sha256"]
        with self.assertRaisesRegex(ValueError, "eligible"):
            validate_d_shuffled_assignment_batch(batch, altered_records, altered_records, sources,
                **altered_hashes)
        no_split = [dict(row) for row in records]
        no_split[0].pop("split")
        with self.assertRaisesRegex(ValueError, "DEVELOPMENT split"):
            assign_d_shuffled_donors(records, no_split, sources,
                **self.assignment_expected_hashes(no_split, sources))
        batch = assign_d_shuffled_donors(records, records, sources, **hashes)
        tampered = json.loads(json.dumps(batch))
        tampered["assignment_batch_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "batch hash"):
            validate_d_shuffled_assignment_batch(tampered, records, records, sources, **hashes)
        fabricated = json.loads(json.dumps(batch))
        fabricated["assignments"].pop()
        with self.assertRaisesRegex(ValueError, "cover every recipient"):
            validate_d_shuffled_assignment_batch(fabricated, records, records, sources, **hashes)

    def test_controls_retry_history_and_response_validation_are_shared(self):
        settings = self.configured(
            arm_hypothesis_max_attempts=2,
            arm_hypothesis_retry_policy="fixture-control-retry",
        )
        good = self.controls_response("D-shuffled")
        model = MockModel(["not json", good])
        state = PipelineState()
        generate_d_shuffled(
            state, "target-1", "donor-2", "Task", "Donor evidence",
            self.donor_assignment_provenance("target-1", "donor-2", "Donor evidence"),
            model, settings, self.donor_check, recipient_split="DEVELOPMENT",
            retry_prompt_builder=lambda prompt, raw, errors, attempt: prompt + "\nMock retry.",
        )
        result = state.hypothesis_generations[0]
        self.assertEqual(result["status"], "blocked")
        self.assertIn("paper ID is invalid", result["errors"][0])
        self.assertEqual(model.calls, [])

        wrong_arm = self.controls_response("D-empty")
        state = PipelineState()
        generate_d_shuffled(
            state, "target-1", "donor-2", "Task", "Donor evidence",
            self.donor_assignment_provenance("target-1", "donor-2", "Donor evidence"),
            MockModel([wrong_arm]), self.configured(), self.donor_check,
            recipient_split="DEVELOPMENT",
        )
        self.assertEqual(state.hypothesis_generations[0]["status"], "blocked")
        self.assertIn("paper ID is invalid", state.hypothesis_generations[0]["errors"][0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
