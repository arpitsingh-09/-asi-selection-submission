"""Checks for the scoped E6 minimum-configuration/preregistration draft."""

import json
import unittest
from pathlib import Path


E6 = Path(__file__).resolve().parents[1]
ROOT = E6.parent


def read_json(name):
    return json.loads((E6 / name).read_text(encoding="utf-8"))


class MinimumExperimentalConfigurationTests(unittest.TestCase):
    def test_seven_arm_output_and_selection_contracts_are_explicit(self):
        config = read_json("config.json")
        self.assertEqual(config["arms"], ["D", "QH", "QH-sel", "QH-rand", "HQ", "D-empty", "D-shuffled"])
        self.assertEqual(config["prompt_contracts"]["hypotheses_per_arm"], 6)
        for arm in ("QH", "QH-sel", "QH-rand"):
            self.assertEqual(config["prompt_contracts"]["arm_outputs"][arm]["questions"], 3)
            self.assertEqual(config["prompt_contracts"]["arm_outputs"][arm]["hypotheses_per_question"], 2)
        self.assertEqual(config["candidate_generation"]["requested_candidate_count"], 6)
        self.assertEqual(config["selection_randomization"]["qh_rand"]["master_seed"], 2026)
        self.assertTrue(config["selection_randomization"]["qh_rand"]["sampling_without_replacement"])

    def test_evaluation_config_records_required_interfaces_without_fabricating_policies(self):
        config = read_json("evaluation_config.json")
        self.assertEqual(config["reconstruction"]["best_similarity_metrics"], ["research_question", "main_hypothesis"])
        self.assertIn("exact-match accuracy", config["hypobench"]["heldout_scoring_interface"])
        self.assertEqual(config["diversity"]["hypothesis_count"], 6)
        self.assertEqual(config["question_type"]["categories"], ["constructive", "analytic", "other", "ambiguous"])
        self.assertEqual(config["pairwise_judging"]["maximum_judges"], 1)
        self.assertEqual(config["paired_bootstrap"]["confidence_level"], 0.95)
        self.assertTrue(config["paired_bootstrap"]["all_seven_arm_pairwise_comparisons"])
        self.assertEqual(config["hypobench"]["dataset_and_split"]["dataset_id"],
                         "hypobench-synthetic-election-level2")
        self.assertEqual(config["hypobench"]["dataset_and_split"]["split"], "TEST")
        self.assertEqual(config["hypobench"]["dataset_and_split"]["input_set_count"], 501)
        self.assertEqual(config["hypobench"]["planted_hypothesis_source"]["scope"],
                         "dataset_level")
        self.assertIsNone(config["hypobench"]["planted_hypothesis_source"][
            "row_level_hypothesis_mapping"])
        prediction = config["hypobench"]["prediction_policy"]
        self.assertEqual(prediction["temperature"], 0.0)
        self.assertEqual(prediction["seed"], 2026)
        self.assertFalse(prediction["heldout_label_available_to_predictor"])
        self.assertIn("denominator", prediction["invalid_prediction_policy"])
        recovery = config["hypobench"]["recovery_judgment_policy"]
        self.assertEqual(recovery["judge_count"], 1)
        self.assertEqual(recovery["comparison_unit"].split(" per ")[0],
                         "all 6 generated hypotheses by all 14 dataset-level planted hypotheses")
        self.assertEqual(recovery["per_input_set_metric"],
                         "number of recovered planted hypotheses divided by 14")
        self.assertEqual(config["paired_bootstrap"]["replicates"], 10000)

    def test_preregistration_is_explicitly_draft_and_covers_required_sections(self):
        prereg = (ROOT / "PREREG.md").read_text(encoding="utf-8")
        for heading in (
            "E6: seven-arm experiment working preregistration draft",
            "Research questions and directional hypotheses",
            "Testbeds and outcomes",
            "Data, generator, and selection",
            "Statistical and analysis plan",
        ):
            self.assertIn(heading, prereg)
        self.assertIn("not a prospective preregistration", prereg)
        self.assertIn("The exact cap remains unset until preregistration", prereg)

    def test_experiment_and_dataset_gates_remain_closed(self):
        config = read_json("config.json")
        literature = read_json("literature_testbed_config.json")
        self.assertEqual(config["protocol"]["status"], "approved")
        self.assertEqual(config["generation"]["model"], "gemma3:12b")
        self.assertEqual(config["generation"]["backend"], "ollama-local")
        self.assertEqual(config["generation"]["documented_training_cutoff"],
                         "August 2024 (month-level precision)")
        self.assertTrue(config["inference_budget"]["equalize_calls_or_tokens"])
        self.assertTrue(config["inference_budget"]["count_selector_dedup_judge_calls"])
        self.assertEqual(config["inference_budget"]["tokens_per_input_set_arm"], 8192)
        self.assertTrue(config["protocol"]["execution_authorized"])
        self.assertIn("committed-artifact", config["protocol"]["authorization_scope"])
        self.assertEqual(literature["status"], "provisional_unapproved")
        self.assertEqual(literature["generator_training_cutoff_utc"], "2024-09-01T00:00:00Z")
        self.assertTrue(literature["input_sets_frozen"])
        self.assertFalse(literature["real_annotations_extracted"])
        self.assertEqual(literature["candidate_manifest"]["eligible_candidate_count"], 216)
        self.assertFalse(literature["candidate_manifest"]["selected"])

    def test_local_model_inventory_records_candidates_without_selecting_one(self):
        audit = read_json("config.json")["local_model_inventory_audit"]
        self.assertEqual(audit["ollama_cli_version"], "0.40.15")
        self.assertFalse(audit["server_api_reachable"])
        self.assertFalse(audit["inference_verified"])
        self.assertFalse(audit["tokenizer_counting_verified"])
        self.assertIn("gemma3:12b (proposed", audit["selected_for_e6"])
        models = {row["tag"]: row for row in audit["models"]}
        self.assertEqual(set(models), {"gemma3:12b", "qwen3:1.7b", "qwen3:8b"})
        for row in models.values():
            self.assertRegex(row["manifest_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(row["model_layer_digest"], r"^sha256:[0-9a-f]{64}$")
            self.assertEqual(row["status"], "installed_manifest_verified_runtime_unverified")
        self.assertEqual(models["gemma3:12b"]["training_cutoff"],
                         "2024-08 (month precision; day not specified)")
        self.assertIsNone(models["qwen3:8b"]["training_cutoff"])
        reported = audit["later_user_reported_runtime_verification"]
        self.assertEqual(reported["status"],
                         "passed_as_reported; machine-readable verifier output not saved in repository")
        self.assertEqual(reported["api_tags_digest_sha256"],
                         "b92b218582c521ba287f38f1d6057dcd3c6cbff036f13cac97b5d861f5e58ec3")
        self.assertTrue(reported["exact_prompt_token_preflight"] == "passed")


if __name__ == "__main__":
    unittest.main()
