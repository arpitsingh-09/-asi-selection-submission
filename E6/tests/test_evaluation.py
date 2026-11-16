"""Mock-only tests of E6 evaluation adapters and statistical plumbing."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation import (  # noqa: E402
    EvaluationError,
    aggregate_hypobench_dataset_level_recovery,
    aggregate_hypobench_heldout_accuracy,
    build_blinded_pairwise_presentations,
    classify_question,
    evaluate_already_asked_rate,
    evaluate_k6_hypothesis_diversity,
    evaluate_hypobench_data_explanation,
    evaluate_hypobench_explanation_on_heldout,
    evaluate_hypobench_recovery,
    evaluate_hypobench_dataset_level_recovery,
    evaluate_reconstruction,
    evaluate_reconstruction_best_similarity,
    evaluate_literature_seven_arm_outputs,
    evaluate_same_question_judgments,
    extract_reference_targets,
    judge_blinded_presentations,
    make_synthetic_planted_recovery_fixture,
    load_hypobench_split,
    normalize_hypobench_evaluation_inputs,
    paired_bootstrap_interval,
    paired_bootstrap_all_seven_arms,
    prepare_hypobench_data_explanation_input,
    prepare_hypobench_normalized_data_explanation_input,
    score_hypobench_heldout_predictions,
    summarize_binary_rate,
    summarize_hypothesis_diversity,
    write_literature_evaluation_bundle_exclusive,
)


class MockClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.prompts = []

    def __call__(self, stage, prompt):
        self.prompts.append((stage, prompt))
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


class EvaluationPlumbingTests(unittest.TestCase):
    def test_reconstruction_best_similarity_and_same_question_judgments(self):
        similarities = {"candidate Q1": 0.2, "candidate Q2": 0.9,
                        "candidate H1": 0.4, "candidate H2": 0.7}
        result = evaluate_reconstruction_best_similarity(
            "paper-1", ["candidate Q1", "candidate Q2"], ["candidate H1", "candidate H2"],
            {"research_question": "target Q", "main_hypothesis": "target H"},
            lambda candidate, target: similarities[candidate],
            reference_provenance={"source": "fixture"}, policy_id="fixture-similarity",
        )
        self.assertEqual(result["stage"], "reconstruction_best_similarity")
        self.assertEqual(result["parsed_output"]["research_question"]["best_similarity"], 0.9)
        self.assertEqual(result["parsed_output"]["main_hypothesis"]["best_similarity"], 0.7)

        judgments = evaluate_same_question_judgments(
            "paper-1", ["Q1", "Q2"], "target Q", lambda candidate, reference: candidate == "Q1",
            reference_provenance={"source": "fixture"}, policy_id="fixture-same-question",
        )
        self.assertEqual([row["same_question"] for row in judgments["parsed_output"]], [True, False])

    def test_hypobench_heldout_accuracy_uses_caller_supplied_labels(self):
        prepared = prepare_hypobench_data_explanation_input(
            "hb-test-1", {"text": "fixture"}, ["explanation"],
            dataset_id="hypobench-fixture", split="TEST",
            dataset_provenance={"source_sha256": "fixture-hash"},
        )
        result = score_hypobench_heldout_predictions(
            prepared, ["truthful", "deceptive", "truthful"],
            ["truthful", "truthful", "truthful"],
        )
        self.assertEqual(result["stage"], "hypobench_heldout_accuracy")
        self.assertEqual(result["parsed_output"], {
            "correct": 2, "denominator": 3, "accuracy": 2 / 3,
            "invalid_prediction_count": 0,
            "invalid_prediction_policy": "count_as_incorrect_keep_in_fixed_denominator",
        })
        self.assertEqual(result["provenance"]["dataset_id"], "hypobench-fixture")
        with self.assertRaisesRegex(EvaluationError, "length matched"):
            score_hypobench_heldout_predictions(prepared, ["A"], ["A", "B"])

        end_to_end = evaluate_hypobench_explanation_on_heldout(
            prepared, ["truthful", "deceptive"],
            lambda item: {"predicted_labels": ["truthful", "truthful"],
                          "raw_response": "fixture predictor response"},
            predictor_policy_id="fixture-prediction-policy",
        )
        self.assertEqual(end_to_end["stage"], "hypobench_data_explanation_heldout")
        self.assertEqual(end_to_end["parsed_output"]["accuracy"], 0.5)
        self.assertEqual(end_to_end["provenance"]["split"], "TEST")

    def test_heldout_invalid_predictions_are_wrong_in_fixed_denominator(self):
        prepared = prepare_hypobench_data_explanation_input(
            "hb-invalid", {"text": "heldout observation"}, ["generated rule"],
            dataset_id="fixture", split="TEST", dataset_provenance={"source": "fixture"},
        )
        scored = score_hypobench_heldout_predictions(
            prepared, ["A", "B", "A"], ["A", None, "not-a-class"],
            valid_labels=["A", "B"],
        )
        self.assertEqual(scored["parsed_output"], {
            "correct": 1, "denominator": 3, "accuracy": 1 / 3,
            "invalid_prediction_count": 2,
            "invalid_prediction_policy": "count_as_incorrect_keep_in_fixed_denominator",
        })

    def test_dataset_level_recovery_uses_conservative_match_and_ambiguity_rules(self):
        generated = [f"generated {i}" for i in range(6)]
        planted = [f"ground truth {i}" for i in range(14)]
        matrix = [["NO_MATCH"] * 14 for _ in range(6)]
        matrix[0][0] = "MATCH"
        matrix[1][1] = "AMBIGUOUS"
        matrix[2][2] = None
        result = evaluate_hypobench_dataset_level_recovery(
            "input-1", generated, planted,
            lambda hypotheses, references: {"judgments": matrix},
            dataset_provenance={"dataset_id": "fixture", "scope": "dataset_level"},
            policy_id="fixture-recovery",
        )
        parsed = result["parsed_output"]
        self.assertEqual(parsed["recovered_ground_truth_count"], 1)
        self.assertEqual(parsed["ground_truth_denominator"], 14)
        self.assertEqual(parsed["recovery_recall"], 1 / 14)
        self.assertEqual(parsed["ambiguous_ground_truth_count"], 2)
        self.assertEqual(parsed["invalid_judgment_cell_count"], 1)
        self.assertEqual(parsed["per_ground_truth"][1]["status"], "ambiguous_unrecovered")
        self.assertEqual(parsed["per_ground_truth"][2]["status"], "ambiguous_unrecovered")

    def test_recovery_aggregation_is_manifest_ordered_and_reproducible(self):
        def recovery(input_id, count):
            return {
                "input_set_id": input_id,
                "parsed_output": {
                    "ground_truth_denominator": 14,
                    "recovered_ground_truth_count": count,
                    "ambiguous_ground_truth_count": 1,
                    "invalid_judgment_cell_count": 0,
                },
            }
        ids = ["input-1", "input-2"]
        results = [recovery("input-1", 2), recovery("input-2", 1)]
        first = aggregate_hypobench_dataset_level_recovery(
            ids, results, dataset_provenance={"dataset_id": "fixture"},
        )
        reversed_results = aggregate_hypobench_dataset_level_recovery(
            ids, list(reversed(results)), dataset_provenance={"dataset_id": "fixture"},
        )
        self.assertEqual(first["parsed_output"], reversed_results["parsed_output"])
        self.assertEqual(first["parsed_output"]["input_set_count"], 2)
        self.assertEqual(first["parsed_output"]["macro_recovery_recall"], 3 / 28)
        self.assertEqual(first["parsed_output"]["ground_truth_item_opportunities"], 28)

    def test_heldout_accuracy_aggregation_keeps_missing_rows_invalid(self):
        result = aggregate_hypobench_heldout_accuracy(
            ["row-1", "row-2", "row-3"], ["A", "B", "A"], ["A", None, "A"],
            valid_labels=["A", "B"], dataset_provenance={"dataset_id": "fixture"},
        )
        self.assertEqual(result["parsed_output"]["accuracy"], 2 / 3)
        self.assertEqual(result["parsed_output"]["invalid_prediction_count"], 1)
        self.assertEqual(result["parsed_output"]["aggregation_unit"],
                         "source_test_example_input_set")

    def test_already_asked_rate_uses_injected_corpus_matcher(self):
        calls = []
        result = evaluate_already_asked_rate(
            "paper-1", [{"question_id": "q1", "question": "Does A cause B?"},
                        {"question_id": "q2", "question": "How can C be built?"}],
            ["Does A cause B?", "What is C?"],
            lambda question, corpus: calls.append((question, corpus)) or question in corpus,
            denominator_policy_id="fixture-denominator",
            provenance={"corpus_source": "fixture"},
        )
        self.assertEqual(result["parsed_output"]["rate"], 0.5)
        self.assertEqual(result["stage"], "already_asked_rate")
        self.assertEqual(len(calls), 2)

    def test_k6_diversity_adjudicates_all_15_pairs(self):
        hypotheses = [{"hypothesis_id": f"H{i}", "text": f"Hypothesis {i}"}
                      for i in range(1, 7)]
        calls = []
        result = evaluate_k6_hypothesis_diversity(
            "paper-1", hypotheses,
            lambda left, right: calls.append((left, right)) or left != right,
            lambda pairs: sum(row["distinct"] for row in pairs) / len(pairs),
            policy_id="fixture-diversity", provenance={"source": "fixture"},
        )
        self.assertEqual(len(calls), 15)
        self.assertEqual(result["parsed_output"]["K"], 6)
        self.assertEqual(result["parsed_output"]["pair_count"], 15)
        self.assertEqual(result["parsed_output"]["aggregate"], 1.0)
        with self.assertRaisesRegex(EvaluationError, "exactly six"):
            evaluate_k6_hypothesis_diversity(
                "paper-1", hypotheses[:5], lambda a, b: True, lambda pairs: 0,
                policy_id="fixture", provenance={},
            )

    def test_bootstrap_compares_all_seven_arms_with_paired_95_percent_intervals(self):
        def mean(values):
            return sum(values) / len(values)

        def percentile_interval(draws, confidence_level):
            values = sorted(draws)
            alpha = (1 - confidence_level) / 2
            return values[int(alpha * (len(values) - 1))], values[int(
                (1 - alpha) * (len(values) - 1)
            )]

        def sampler(ids, size, replicate, seed):
            return [ids[(replicate + offset + seed) % len(ids)] for offset in range(size)]

        arm_values = {
            arm: {"input-1": float(index), "input-2": float(index + 1)}
            for index, arm in enumerate(("D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled"))
        }
        options = {"replicates": 50, "seed": 9, "statistic": mean,
                   "interval_estimator": percentile_interval,
                   "resample_input_set_ids": sampler, "rng_name": "fixture RNG v1"}
        first = paired_bootstrap_all_seven_arms("all-inputs", arm_values, **options)
        second = paired_bootstrap_all_seven_arms("all-inputs", arm_values, **options)
        comparisons = first["parsed_output"]["comparisons"]
        self.assertEqual(first, second)
        self.assertEqual(len(comparisons), 21)
        self.assertEqual(comparisons["D-minus-QH"]["point_estimate"], -1.0)
        self.assertEqual(comparisons["D-minus-QH"]["confidence_level"], 0.95)
        self.assertEqual(first["provenance"]["resampling_unit"], "input_set")
        arm_values["HQ"] = {"input-1": 1.0}
        with self.assertRaisesRegex(EvaluationError, "same paired input_set_ids"):
            paired_bootstrap_all_seven_arms("all-inputs", arm_values, **options)

    def test_hypobench_normalized_data_explanation_flows_into_audited_evaluation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "hypobench.json"
            path.write_text(json.dumps({
                "text": ["record one", "record two"],
                "label": ["A", "B"],
                "unused": ["preserved-1", "preserved-2"],
            }), encoding="utf-8")
            ingested = load_hypobench_split(path, dataset_id="fixture-dataset", split="TEST")
        normalized = normalize_hypobench_evaluation_inputs(
            ingested, field_mapping={"data": "text"}, identifier_field="unused",
        )
        row = normalized["records"][0]
        prepared = prepare_hypobench_normalized_data_explanation_input(
            "hypobench-input-0", normalized, row, ["An explanation."],
        )
        seen = []
        result = evaluate_hypobench_data_explanation(
            prepared, lambda value: seen.append(value) or {"fixture": "adjudicated"},
            policy_id="fixture-policy",
        )

        self.assertEqual(prepared["provenance"]["dataset_id"], "fixture-dataset")
        self.assertEqual(prepared["provenance"]["split"], "TEST")
        self.assertEqual(prepared["provenance"]["dataset"]["source_record_index"], 0)
        self.assertEqual(prepared["provenance"]["dataset"]["source_record_id"], "preserved-1")
        self.assertEqual(prepared["provenance"]["dataset"]["source_sha256"],
                         ingested["provenance"]["source_sha256"])
        self.assertEqual(result["stage"], "hypobench_data_explanation")
        self.assertEqual(result["input_set_id"], "hypobench-input-0")
        self.assertEqual(result["provenance"]["dataset"]["split"], "TEST")
        self.assertEqual(result["parsed_output"], {"fixture": "adjudicated"})
        self.assertEqual(seen[0]["evaluation_input"], prepared["evaluation_input"])
        self.assertEqual(result["evaluation_input_sha256"], prepared["evaluation_input_sha256"])

    def test_hypobench_data_explanation_evaluator_rejects_tampered_input_hash(self):
        prepared = prepare_hypobench_data_explanation_input(
            "input", {"task": "fixture"}, ["explanation"],
            dataset_id="fixture", split="TEST", dataset_provenance={"source": "fixture"},
        )
        prepared["evaluation_input"]["generated_explanations"] = ["changed"]
        calls = []
        with self.assertRaisesRegex(EvaluationError, "hash"):
            evaluate_hypobench_data_explanation(
                prepared, lambda value: calls.append(value), policy_id="fixture",
            )
        self.assertEqual(calls, [])

    def test_hypobench_data_explanation_input_preserves_inputs_provenance_and_is_deterministic(self):
        benchmark_record = {
            "example_id": "hb-17", "task": "Explain the pattern",
            "data": [{"group": "A", "value": 2}], "extra": "kept",
        }
        explanations = ["The observed value differs by group.", "A second explanation."]
        provenance = {"source_sha256": "abc123", "source_row": 17}
        first = prepare_hypobench_data_explanation_input(
            "input-17", benchmark_record, explanations,
            dataset_id="hypobench-fixture", split="DEVELOPMENT",
            dataset_provenance=provenance,
        )
        second = prepare_hypobench_data_explanation_input(
            "input-17", benchmark_record, explanations,
            dataset_id="hypobench-fixture", split="DEVELOPMENT",
            dataset_provenance=provenance,
        )

        self.assertEqual(first, second)
        self.assertEqual(first["evaluation_input"]["benchmark_record"], benchmark_record)
        self.assertEqual(first["evaluation_input"]["generated_explanations"], explanations)
        self.assertEqual(first["provenance"], {
            "dataset_id": "hypobench-fixture", "split": "DEVELOPMENT",
            "dataset": provenance,
        })
        self.assertEqual(first["evaluation_input_sha256"], hashlib.sha256(
            json.dumps(first["evaluation_input"], ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
        ).hexdigest())
        self.assertEqual(first["status"], "input_ready_unscored")
        self.assertEqual(first["scoring_status"], "not_run")

    def test_hypobench_data_explanation_input_rejects_invalid_and_missing_fields(self):
        valid = ("input", {"task": "fixture"}, ["explanation"])
        kwargs = {"dataset_id": "fixture", "split": "DEVELOPMENT",
                  "dataset_provenance": {"source": "fixture"}}
        invalid = [
            ((" ", valid[1], valid[2]), kwargs),
            ((valid[0], {}, valid[2]), kwargs),
            ((valid[0], valid[1], []), kwargs),
            ((valid[0], valid[1], "explanation"), kwargs),
            ((valid[0], valid[1], [" "]), kwargs),
            (valid, {**kwargs, "dataset_id": " "}),
            (valid, {**kwargs, "split": " "}),
            (valid, {**kwargs, "dataset_provenance": {}}),
        ]
        for args, call_kwargs in invalid:
            with self.subTest(args=args, call_kwargs=call_kwargs):
                with self.assertRaises(EvaluationError):
                    prepare_hypobench_data_explanation_input(*args, **call_kwargs)

    def test_hypobench_columnar_json_ingestion_preserves_rows_and_hashes_source(self):
        source = {
            "text": ["record one", "record two"],
            "label": ["A", "B"],
            "features": [[1, 0], [0, 1]],
        }
        raw = json.dumps(source, ensure_ascii=False).encode("utf-8")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixture.json"
            path.write_bytes(raw)

            result = load_hypobench_split(
                path, dataset_id="fixture-dataset", split="DEVELOPMENT",
            )

            self.assertEqual(result["status"], "ingested_unselected_unfrozen")
            self.assertEqual(result["records"], [
                {"text": "record one", "label": "A", "features": [1, 0]},
                {"text": "record two", "label": "B", "features": [0, 1]},
            ])
            self.assertEqual(result["provenance"]["source_format"], "json-columnar")
            self.assertEqual(result["provenance"]["source_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(result["provenance"]["record_count"], 2)
            self.assertFalse(result["provenance"]["dataset_selected"])
            self.assertFalse(result["provenance"]["dataset_frozen"])

    def test_hypobench_jsonl_ingestion_preserves_order_and_source_byte_hash(self):
        raw = b'{"id":1,"text":"first"}\n\n{"id":2,"text":"second"}\n'
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixture.jsonl"
            path.write_bytes(raw)
            first = load_hypobench_split(path, dataset_id="fixture", split="TEST")

            path.write_bytes(raw.replace(b"second", b"changed"))
            changed = load_hypobench_split(path, dataset_id="fixture", split="TEST")

        self.assertEqual(first["records"], [
            {"id": 1, "text": "first"}, {"id": 2, "text": "second"},
        ])
        self.assertEqual(first["provenance"]["source_format"], "jsonl-records")
        self.assertNotEqual(first["provenance"]["source_sha256"],
                            changed["provenance"]["source_sha256"])
        self.assertEqual(changed["records"][1]["text"], "changed")

    def test_hypobench_ingestion_rejects_misaligned_columns_and_invalid_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "misaligned.json"
            path.write_text('{"text":["one","two"],"label":["A"]}', encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "equal lengths"):
                load_hypobench_split(path, dataset_id="fixture", split="DEVELOPMENT")

            path.write_text('[{"id":1},null]', encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "record list"):
                load_hypobench_split(path, dataset_id="fixture", split="DEVELOPMENT")

    def test_hypobench_normalization_preserves_ids_split_records_and_source_provenance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixture.json"
            path.write_text(json.dumps([{
                "example_id": "row-17",
                "task_text": "Explain the observed pattern.",
                "evidence_text": "The outcome rises after treatment.",
                "unused_source_field": "retained",
            }]), encoding="utf-8")
            ingested = load_hypobench_split(
                path, dataset_id="fixture-dataset", split="DEVELOPMENT",
            )

        normalized = normalize_hypobench_evaluation_inputs(
            ingested,
            field_mapping={"task": "task_text", "evidence": "evidence_text"},
            identifier_field="example_id",
        )

        self.assertEqual(normalized["status"], "normalized_unselected_unfrozen")
        self.assertEqual(normalized["dataset_id"], "fixture-dataset")
        self.assertEqual(normalized["split"], "DEVELOPMENT")
        self.assertEqual(normalized["records"][0]["source_record_id"], "row-17")
        self.assertEqual(normalized["records"][0]["source_record_index"], 0)
        self.assertEqual(normalized["records"][0]["evaluation_fields"], {
            "task": "Explain the observed pattern.",
            "evidence": "The outcome rises after treatment.",
        })
        self.assertEqual(normalized["records"][0]["source_record"]["unused_source_field"],
                         "retained")
        self.assertEqual(normalized["provenance"], ingested["provenance"])
        self.assertFalse(normalized["dataset_selected"])
        self.assertFalse(normalized["dataset_frozen"])
        self.assertNotIn("planted_hypothesis", normalized["records"][0])

    def test_hypobench_normalization_rejects_missing_required_or_requested_id_fields(self):
        ingested = {
            "status": "ingested_unselected_unfrozen",
            "dataset_id": "fixture",
            "split": "DEVELOPMENT",
            "records": [{"task_text": "Task only"}],
            "provenance": {"source_sha256": "fixture-hash"},
        }
        with self.assertRaisesRegex(EvaluationError, "missing required field 'evidence_text'"):
            normalize_hypobench_evaluation_inputs(
                ingested, field_mapping={"task": "task_text", "evidence": "evidence_text"},
            )
        with self.assertRaisesRegex(EvaluationError, "missing identifier field 'example_id'"):
            normalize_hypobench_evaluation_inputs(
                ingested, field_mapping={"task": "task_text"}, identifier_field="example_id",
            )

    def test_reference_extraction_uses_prompt_and_preserves_raw(self):
        raw = json.dumps({
            "research_question": "Does X change Y?", "research_question_explicit": True,
            "main_hypothesis": "X increases Y.", "main_hypothesis_explicit": True,
        })
        client = MockClient([raw])
        result = extract_reference_targets("paper-1", "full paper fixture", client,
                                           model_configuration={"model": "mock"})
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["raw_output"], raw)
        self.assertIn("full paper fixture", client.prompts[0][1])
        self.assertEqual(result["provenance"]["gold_truth_status"], "requires independent validation")

    def test_reference_extraction_records_malformed_json_failure(self):
        result = extract_reference_targets("paper-1", "text", MockClient(["not-json"]),
                                           model_configuration={})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["attempts"][0]["status"], "failed")
        self.assertEqual(result["raw_output"], "not-json")

    def test_reference_extraction_enforces_exact_fixed_prompt_output_schema(self):
        missing = json.dumps({"research_question_explicit": False,
                              "main_hypothesis": None,
                              "main_hypothesis_explicit": False})
        result = extract_reference_targets("paper-1", "text", MockClient([missing]),
                                           model_configuration={})
        self.assertEqual(result["status"], "failed")
        self.assertIn("exactly the four documented fields", result["error"])

        extra = json.dumps({"research_question": "RQ", "research_question_explicit": True,
                            "main_hypothesis": None, "main_hypothesis_explicit": False,
                            "confidence": 0.9})
        result = extract_reference_targets("paper-1", "text", MockClient([extra]),
                                           model_configuration={})
        self.assertEqual(result["status"], "failed")

    def test_literature_evaluation_integrates_all_seven_arms_and_stores_hashed_bundle(self):
        arms = {}
        for arm in ("D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled"):
            arms[arm] = {
                "execution_status": "succeeded",
                "output": {"status": "ok",
                           "questions": [{"text": f"Question for {arm}?"}],
                           "hypotheses": [{"hypothesis_id": f"{arm}-{i}",
                                           "text": f"Hypothesis {i} for {arm}."}
                                          for i in range(6)]},
                "manifest": {"arm": arm, "input_sha256": f"hash-{arm}"},
            }
        target = {"stage": "reference_target_extraction", "status": "succeeded",
                  "parsed_output": {"research_question": "Does A affect B?",
                                    "research_question_explicit": True,
                                    "main_hypothesis": "A increases B.",
                                    "main_hypothesis_explicit": True}}
        bundle = evaluate_literature_seven_arm_outputs(
            "literature-1", arms, target,
            similarity_evaluator=lambda candidate, reference: 0.75,
            same_question_evaluator=lambda candidate, reference: candidate.startswith("Question"),
            similarity_policy_id="fixture-sim-v1", same_question_policy_id="fixture-same-v1",
            reference_provenance={"target_source_url": "https://arxiv.org/abs/2501.12345",
                                  "target_record_sha256": "a" * 64},
        )
        self.assertEqual(bundle["record_count"], 21)
        self.assertEqual(len(bundle["records"]), 7 * 3)
        for arm in arms:
            arm_records = [row for row in bundle["records"] if row["provenance"].get("arm") == arm]
            self.assertEqual(len(arm_records), 3)
            self.assertTrue(all(row["status"] == "succeeded" for row in arm_records))
            self.assertTrue(all(row["provenance"]["target_extraction_record_sha256"]
                                for row in arm_records))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "literature-eval.json"
            write_literature_evaluation_bundle_exclusive(path, bundle)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved, bundle)
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                write_literature_evaluation_bundle_exclusive(path, bundle)

    def test_literature_evaluation_records_unavailable_fields_as_blocked(self):
        arms = {arm: {"execution_status": "succeeded", "output": {
            "status": "ok", "questions": [], "hypotheses": [{"text": "H"}]
        }} for arm in ("D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled")}
        bundle = evaluate_literature_seven_arm_outputs(
            "literature-2", arms,
            {"parsed_output": {"research_question": None, "main_hypothesis": "Truth."}},
            similarity_evaluator=lambda candidate, reference: 1.0,
            same_question_evaluator=lambda candidate, reference: True,
            similarity_policy_id="fixture", same_question_policy_id="fixture",
            reference_provenance={"source": "fixture"},
        )
        self.assertEqual(len(bundle["records"]), 21)
        by_stage = [row for row in bundle["records"] if row["stage"] == "same_question_judgment"]
        self.assertEqual(len(by_stage), 7)
        self.assertTrue(all(row["status"] == "blocked" for row in by_stage))
        question_similarity = [row for row in bundle["records"]
                               if row["stage"] == "literature_reconstruction_similarity"
                               and row["evaluation_input"]["field"] == "research_question"]
        self.assertTrue(all(row["status"] == "blocked" for row in question_similarity))

    def test_reconstruction_calls_injected_policy_and_retains_inputs(self):
        generated = {"questions": ["Q"], "hypotheses": ["H"]}
        reference = {"research_question": "RQ", "main_hypothesis": "RH"}
        result = evaluate_reconstruction(
            "input-1", generated, reference,
            lambda got, gold: {"match_result": "fixture"},
            reference_provenance={"source": "fixture"}, policy_id="test-policy",
        )
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["evaluation_input"]["reference"], reference)
        self.assertEqual(result["parsed_output"], {"match_result": "fixture"})
        with self.assertRaises(EvaluationError):
            evaluate_reconstruction("input-1", generated, reference, None,
                                    reference_provenance={}, policy_id=None)

    def test_hypobench_synthetic_planted_hypothesis_recovery(self):
        fixture = make_synthetic_planted_recovery_fixture()
        self.assertTrue(fixture["provenance"]["not_for_research"])
        result = evaluate_hypobench_recovery(
            fixture["input_set_id"], fixture["benchmark_record"],
            fixture["planted_hypothesis"],
            lambda record, planted: {"fixture_recovered": planted == fixture["planted_hypothesis"]},
            dataset_provenance=fixture["provenance"], policy_id="fixture-exact-match",
        )
        self.assertEqual(result["parsed_output"], {"fixture_recovered": True})
        self.assertEqual(result["evaluation_input"]["planted_hypothesis"], fixture["planted_hypothesis"])

    def test_hypobench_recovery_rejects_invalid_caller_inputs_before_judging(self):
        calls = []
        judge = lambda record, planted: calls.append((record, planted))
        fixture = make_synthetic_planted_recovery_fixture()
        invalid_calls = [
            {"input_set_id": " ", "benchmark_record": fixture["benchmark_record"],
             "planted_hypothesis": fixture["planted_hypothesis"], "dataset_provenance": fixture["provenance"]},
            {"input_set_id": fixture["input_set_id"], "benchmark_record": [],
             "planted_hypothesis": fixture["planted_hypothesis"], "dataset_provenance": fixture["provenance"]},
            {"input_set_id": fixture["input_set_id"], "benchmark_record": fixture["benchmark_record"],
             "planted_hypothesis": " ", "dataset_provenance": fixture["provenance"]},
            {"input_set_id": fixture["input_set_id"], "benchmark_record": fixture["benchmark_record"],
             "planted_hypothesis": fixture["planted_hypothesis"], "dataset_provenance": None},
        ]

        for arguments in invalid_calls:
            with self.subTest(arguments=arguments), self.assertRaises(EvaluationError):
                evaluate_hypobench_recovery(
                    arguments["input_set_id"], arguments["benchmark_record"],
                    arguments["planted_hypothesis"], judge,
                    dataset_provenance=arguments["dataset_provenance"],
                    policy_id="fixture-policy",
                )

        self.assertEqual(calls, [])

    def test_already_asked_binary_rate_preserves_decisions_and_denominator_policy(self):
        result = summarize_binary_rate(
            "input-1", "already_asked_rate",
            [{"question_id": "q1", "already_asked": True},
             {"question_id": "q2", "already_asked": False}],
            numerator_field="already_asked", denominator_policy_id="test-denom",
            provenance={"adjudicator": "fixture"},
        )
        self.assertEqual(result["parsed_output"], {"successes": 1, "denominator": 2, "rate": 0.5})
        self.assertEqual(len(result["evaluation_input"]["decisions"]), 2)
        with self.assertRaises(EvaluationError):
            summarize_binary_rate("input-1", "already_asked_rate", [{"already_asked": 1}],
                                  numerator_field="already_asked", denominator_policy_id="x", provenance={})

    def test_diversity_uses_supplied_pair_adjudications_only(self):
        result = summarize_hypothesis_diversity(
            "input-1", [{"id": "h1"}, {"id": "h2"}],
            [{"pair": ["h1", "h2"], "distinct": True}], distinct_field="distinct",
            policy_id="fixture-policy",
            aggregate=lambda pairs: {"fixture_aggregate": pairs[0]["distinct"]},
            provenance={"source": "fixture"},
        )
        self.assertEqual(result["parsed_output"], {"fixture_aggregate": True})
        with self.assertRaises(EvaluationError):
            summarize_hypothesis_diversity("input-1", [], [], distinct_field="distinct",
                                           policy_id=None, aggregate=None, provenance={})

    def test_question_type_classifier_uses_existing_prompt_and_validates_labels(self):
        raw = '{"type":"constructive"}'
        client = MockClient([raw, '{"type":"ambiguous"}', '{"type":"unknown"}'])
        result = classify_question("input-1", "q1", "How can X be built?", client,
                                   model_configuration={"model": "mock"})
        self.assertEqual(result["parsed_output"], {"type": "constructive"})
        self.assertIn("constructive", client.prompts[0][1])
        ambiguous = classify_question("input-1", "q-amb", "Unclear question", client,
                                      model_configuration={"model": "mock"})
        self.assertEqual(ambiguous["parsed_output"], {"type": "ambiguous"})
        bad = classify_question("input-1", "q2", "Question?", client,
                                model_configuration={"model": "mock"})
        self.assertEqual(bad["status"], "failed")
        self.assertEqual(bad["attempts"][0]["raw"], '{"type":"unknown"}')

    def test_pairwise_blinding_emits_both_orders_and_requires_length_matcher_for_llm(self):
        comparison = [{"input_set_id": "input-1", "left_id": "arm-x", "right_id": "arm-y",
                       "left_text": "Hypothesis X", "right_text": "Hypothesis Y",
                       "provenance": {"source": "fixture"}}]
        labels = {"arm-x": "Blind-7", "arm-y": "Blind-2"}
        with self.assertRaises(EvaluationError):
            build_blinded_pairwise_presentations(comparison, labels, llm_judge=True)
        presentations = build_blinded_pairwise_presentations(
            comparison, labels,
            length_matcher=lambda a, b: {"left_text": a, "right_text": b,
                                         "policy_id": "fixture", "matched": True},
        )
        self.assertEqual(len(presentations), 2)
        self.assertEqual(presentations[0]["item_a_blind_id"], "Blind-7")
        self.assertEqual(presentations[1]["item_a_blind_id"], "Blind-2")
        client = MockClient(['{"better":"A"}', '{"better":"tie"}'])
        records = judge_blinded_presentations(
            presentations, client, domain_and_task="fixture task", evidence="fixture evidence",
            model_configuration={"model": "mock"},
        )
        self.assertEqual([r["parsed_output"]["better"] for r in records], ["A", "tie"])
        self.assertEqual(len(client.prompts), 2)
        self.assertTrue(all(r["raw_output"] for r in records))
        self.assertTrue(all(r["provenance"]["output_kind"] == "llm_judge_output"
                            and r["provenance"]["judge_count"] == 1 for r in records))

    def test_pairwise_malformed_and_model_errors_are_retained(self):
        pres = [{"input_set_id": "i", "item_a_text": "A", "item_b_text": "B"}]
        records = judge_blinded_presentations(
            pres, MockClient(["not-json"]), domain_and_task="t", evidence="e", model_configuration={},
        )
        self.assertEqual(records[0]["status"], "failed")
        self.assertIn("malformed JSON", records[0]["error"])
        records = judge_blinded_presentations(
            pres, MockClient([RuntimeError("mock failure")]), domain_and_task="t", evidence="e",
            model_configuration={},
        )
        self.assertEqual(records[0]["attempts"][0]["status"], "failed")

    def test_paired_bootstrap_resamples_input_set_pairs_with_explicit_settings(self):
        def mean(values):
            return sum(values) / len(values)

        def percentile(values, level):
            ordered = sorted(values)
            alpha = (1 - level) / 2
            return ordered[int(alpha * (len(ordered) - 1))], ordered[int((1 - alpha) * (len(ordered) - 1))]

        def fixture_resampler(ids, size, replicate, seed):
            # Deterministic mock draws include input_set IDs and emulate
            # with-replacement resampling without fixing a production RNG.
            return [ids[(replicate + offset + seed) % len(ids)] for offset in range(size)]

        result = paired_bootstrap_interval(
            {"input-a": 1.0, "input-b": 3.0}, replicates=100,
            confidence_level=0.95, seed=17, statistic=mean,
            interval_estimator=percentile, resample_input_set_ids=fixture_resampler,
            rng_name="mock deterministic sampler v1",
        )
        self.assertEqual(result["resampling_unit"], "input_set")
        self.assertEqual(result["point_estimate"], 2.0)
        self.assertEqual(result["input_set_ids"], ["input-a", "input-b"])
        with self.assertRaises(EvaluationError):
            paired_bootstrap_interval({"a": 1.0}, replicates=None, confidence_level=None,
                                      seed=None, statistic=None, interval_estimator=None,
                                      resample_input_set_ids=None, rng_name=None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
