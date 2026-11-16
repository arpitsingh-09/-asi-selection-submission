"""Integrity and integration tests for the selected real HypoBench split."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_hypobench_testbed import (  # noqa: E402
    DEFAULT_DATASET_DIR,
    HypoBenchPreparationError,
    prepare_hypobench_election_level2_testbed,
    prepare_hypobench_evaluation_input,
    score_hypobench_evaluation_input,
    score_hypobench_testbed_predictions,
    to_orchestrator_inputs,
    write_manifest_new,
)


class HypoBenchTestbedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = prepare_hypobench_election_level2_testbed()

    def test_selected_test_split_has_stable_unique_ids_and_valid_observations(self):
        manifest = self.manifest
        self.assertEqual(manifest["dataset_id"], "hypobench-synthetic-election-level2")
        self.assertEqual(manifest["split"], "TEST")
        self.assertEqual(manifest["record_count"], 501)
        self.assertEqual(manifest["provenance"]["split_row_counts"], {
            "TRAIN": 1750, "VALIDATION": 249, "TEST": 501,
        })
        ids = [row["input_set_id"] for row in manifest["records"]]
        self.assertEqual(len(ids), len(set(ids)))
        rebuilt = prepare_hypobench_election_level2_testbed()
        self.assertEqual(manifest["manifest_sha256"], rebuilt["manifest_sha256"])
        self.assertEqual(ids, [row["input_set_id"] for row in rebuilt["records"]])
        for row in manifest["records"]:
            self.assertTrue(row["evidence"].strip())
            self.assertEqual(row["split"], "TEST")
            self.assertTrue(row["source_record_sha256"])

    def test_dataset_level_ground_truth_and_row_level_labels_are_separate(self):
        manifest = self.manifest
        gt = manifest["dataset_ground_truth"]
        self.assertEqual(gt["scope"], "dataset_level")
        self.assertEqual(len(gt["hypotheses"]), 14)
        self.assertIsNone(gt["row_level_hypothesis_assignment"])
        row = manifest["records"][0]
        self.assertEqual(row["ground_truth_set_id"], gt["ground_truth_set_id"])
        self.assertEqual(row["heldout_label"]["field"], "label")
        self.assertTrue(row["heldout_label"]["evaluation_only"])
        self.assertIn(row["heldout_label"]["value"], manifest["observed_test_label_classes"])

    def test_train_validation_test_isolation_and_row_provenance_are_verified(self):
        provenance = self.manifest["provenance"]
        self.assertEqual(set(provenance["split_file_hashes"]), {"TRAIN", "VALIDATION", "TEST"})
        self.assertEqual(provenance["split_row_counts"]["TRAIN"], 1750)
        self.assertEqual(provenance["split_row_counts"]["VALIDATION"], 249)
        self.assertEqual(provenance["split_row_counts"]["TEST"], 501)
        for row in self.manifest["records"]:
            self.assertIn("text", row["source_record"])
            self.assertIn("label", row["source_record"])
            self.assertEqual(row["evidence"], row["source_record"]["text"])
            self.assertEqual(row["heldout_label"]["value"], row["source_record"]["label"])

    def test_orchestrator_input_excludes_label_and_eval_interface_scores_explicit_prediction(self):
        row = self.manifest["records"][0]
        prepared = to_orchestrator_inputs(self.manifest)
        self.assertEqual(len(prepared), 501)
        model_input = prepared[0]
        self.assertEqual(model_input.paper_id, row["input_set_id"])
        self.assertEqual(model_input.split, "TEST")
        self.assertEqual(model_input.evidence, row["evidence"])
        self.assertNotIn(row["heldout_label"]["value"], model_input.evidence)
        self.assertNotIn("heldout_label", model_input.provenance)
        self.assertFalse(hasattr(model_input, "heldout_label"))
        evaluation_input = prepare_hypobench_evaluation_input(
            self.manifest, row, ["The observation may predict voting preference."]
        )
        scored = score_hypobench_evaluation_input(
            evaluation_input, row, row["heldout_label"]["value"],
        )
        self.assertEqual(scored["parsed_output"]["accuracy"], 1.0)
        self.assertEqual(scored["provenance"]["split"], "TEST")

    def test_testbed_aggregation_keeps_missing_predictions_in_all_501_rows(self):
        result = score_hypobench_testbed_predictions(self.manifest, [])
        self.assertEqual(result["parsed_output"]["denominator"], 501)
        self.assertEqual(result["parsed_output"]["invalid_prediction_count"], 501)
        self.assertEqual(result["parsed_output"]["accuracy"], 0.0)
        first = self.manifest["records"][0]
        one_policy_record = {
            "input_set_id": first["input_set_id"],
            "raw_output": {"predicted_labels": [first["heldout_label"]["value"]]},
        }
        aggregated = score_hypobench_testbed_predictions(self.manifest, [one_policy_record])
        self.assertEqual(aggregated["parsed_output"]["denominator"], 501)
        self.assertEqual(aggregated["parsed_output"]["invalid_prediction_count"], 500)

    def test_ground_truth_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "dataset"
            destination.mkdir()
            for name in ("metadata.json", "gt_hypotheses_level2.json", "config.yaml",
                         "synthetic_election_train_level2.json",
                         "synthetic_election_val_level2.json",
                         "synthetic_election_test_level2.json"):
                source = DEFAULT_DATASET_DIR / name
                (destination / name).write_bytes(source.read_bytes())
            gt_path = destination / "gt_hypotheses_level2.json"
            gt = json.loads(gt_path.read_text())
            gt[0] += " changed"
            gt_path.write_text(json.dumps(gt), encoding="utf-8")
            with self.assertRaisesRegex(HypoBenchPreparationError, "differs"):
                prepare_hypobench_election_level2_testbed(destination)

    def test_orchestrator_conversion_rejects_tampered_row_mapping(self):
        tampered = json.loads(json.dumps(self.manifest))
        tampered["records"][0]["heldout_label"]["value"] = "invented label"
        tampered["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(HypoBenchPreparationError, "manifest hash"):
            to_orchestrator_inputs(tampered)

        tampered = json.loads(json.dumps(self.manifest))
        tampered["records"][0]["evidence"] += " edited"
        from prepare_hypobench_testbed import _canonical_hash
        tampered["manifest_sha256"] = _canonical_hash({
            key: value for key, value in tampered.items() if key != "manifest_sha256"
        })
        with self.assertRaisesRegex(HypoBenchPreparationError, "evidence or held-out label mapping"):
            to_orchestrator_inputs(tampered)

    def test_manifest_writer_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "manifest.json"
            write_manifest_new(target, self.manifest)
            original = target.read_bytes()
            with self.assertRaisesRegex(HypoBenchPreparationError, "refusing to overwrite"):
                write_manifest_new(target, self.manifest)
            self.assertEqual(target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
