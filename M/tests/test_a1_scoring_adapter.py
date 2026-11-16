import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from E2 import novelty
from M.a1_replication import scoring_adapter


class A1ScoringAdapterTests(unittest.TestCase):
    def setUp(self):
        self.previous_papers = novelty._PAPERS
        self.previous_model = novelty._MODEL
        if self.previous_model is not None:
            self.skipTest("E2 model was initialized before the adapter test")
        novelty._PAPERS = None

    def tearDown(self):
        novelty._PAPERS = self.previous_papers
        novelty._MODEL = self.previous_model

    def test_prepare_validates_all_inputs_and_installs_only_in_memory_overlay(self):
        base_papers = novelty._load_papers()
        base_ids = set(base_papers)
        manifest = scoring_adapter.prepare_scoring_inputs(novelty_module=novelty)
        self.assertTrue(manifest["validated"])
        self.assertEqual(manifest["manipulation_case_count"], 14)
        self.assertEqual(manifest["shuffled_control_score_target_count"], 2)
        self.assertEqual(manifest["empty_controls"], "undefined; excluded from numeric scoring")
        self.assertEqual(manifest["same_topic_decoys"], "unavailable; never scored")
        self.assertFalse(manifest["scores_generated"])
        self.assertFalse(manifest["model_inference_run"])
        self.assertFalse(manifest["bootstrap_run"])
        self.assertIsNone(novelty._MODEL)
        saved_manifest = json.loads(
            scoring_adapter.MANIFEST_FILE.read_text(encoding="utf-8")
        )
        self.assertEqual(saved_manifest, manifest)
        self.assertEqual(
            manifest["scoring_adapter_sha256"],
            scoring_adapter._file_sha256(Path(scoring_adapter.__file__).resolve()),
        )
        self.assertEqual(
            manifest["control_adapter_sha256"],
            scoring_adapter._file_sha256(scoring_adapter.HERE / "controls.py"),
        )

        inputs = json.loads(scoring_adapter.INPUTS_FILE.read_text(encoding="utf-8"))
        synthetic_ids = {row["paper_id"] for row in inputs["synthetic_papers"]}
        self.assertEqual(len(synthetic_ids), 26)
        self.assertTrue(synthetic_ids.issubset(novelty._PAPERS))
        self.assertTrue(synthetic_ids.isdisjoint(base_ids))
        self.assertEqual(set(base_papers), base_ids)
        self.assertIsNot(novelty._PAPERS, base_papers)
        self.assertEqual(len(manifest["scoring_targets"]), 16)

    def test_input_hash_mismatch_fails_before_loading_e2_papers(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_input = Path(directory) / scoring_adapter.INPUTS_FILE.name
            shutil.copyfile(scoring_adapter.INPUTS_FILE, temp_input)
            temp_input.write_text(temp_input.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaisesRegex(
                scoring_adapter.ScoringInputError, "SHA-256 differs"
            ):
                scoring_adapter._read_inputs(temp_input, scoring_adapter.VALIDATION_FILE)

    def test_validation_rejects_focal_leakage_even_with_recomputed_file_digest(self):
        manifest = scoring_adapter.prepare_scoring_inputs(novelty_module=novelty)
        inputs = json.loads(scoring_adapter.INPUTS_FILE.read_text(encoding="utf-8"))
        validation = json.loads(scoring_adapter.VALIDATION_FILE.read_text(encoding="utf-8"))
        inputs["manipulation_cases"][0]["pool_ids"].append(
            inputs["manipulation_cases"][0]["focal_paper_id"]
        )
        validation["inputs_sha256"] = scoring_adapter._json_sha256(inputs)
        with self.assertRaisesRegex(scoring_adapter.ScoringInputError, "Focal paper leakage"):
            scoring_adapter.validate_scoring_inputs(inputs, validation, novelty._PAPERS)
        self.assertTrue(manifest["validated"])

    def test_score_target_forwards_nonempty_target_only_to_locked_e2_wrapper(self):
        target = {
            "condition": "coverage_25",
            "question": "Focal question",
            "claims": ["Human-approved claim"],
            "pool_ids": ["prior-paper", "synthetic-paper"],
            "cutoff": "2025-01-01T00:00:00Z",
        }
        with patch.object(
            scoring_adapter.controls,
            "score_with_e2",
            return_value={"status": "scored", "scores": {"Y": 0.1}},
        ) as locked_score:
            result = scoring_adapter.score_target(target)
        self.assertEqual(result["status"], "scored")
        locked_score.assert_called_once_with(
            {
                "condition": "coverage_25",
                "question": "Focal question",
                "input_paper_ids": ["prior-paper", "synthetic-paper"],
            },
            claims=["Human-approved claim"],
            cutoff="2025-01-01T00:00:00Z",
        )

    def test_score_target_rejects_empty_and_unavailable_conditions(self):
        for condition in ("empty", "same_topic_decoy"):
            with self.subTest(condition=condition):
                with self.assertRaisesRegex(
                    scoring_adapter.ScoringInputError, "not a numeric scoring target"
                ):
                    scoring_adapter.score_target({"condition": condition})

    def test_locked_e2_wrapper_accepts_adapter_preimport_without_loading_model(self):
        previous_verified = scoring_adapter.controls._E2_MODEL_LOCK_VERIFIED
        previous_cache = novelty.CACHE_DB
        previous_env = {
            key: os.environ.get(key)
            for key in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
        }
        try:
            scoring_adapter.controls._E2_MODEL_LOCK_VERIFIED = False
            novelty._MODEL = None
            with patch.object(scoring_adapter.controls, "_verify_e2_snapshot"):
                with tempfile.TemporaryDirectory() as directory:
                    with patch.object(
                        scoring_adapter.controls,
                        "__file__",
                        str(Path(directory) / "controls.py"),
                    ):
                        with patch.object(
                            novelty, "score", return_value={"Y": 0.1, "N": 0.2}
                        ) as e2_score:
                            result = scoring_adapter.controls.score_with_e2(
                                {
                                    "condition": "baseline",
                                    "question": "Focal question",
                                    "input_paper_ids": ["prior-paper"],
                                },
                                claims=["approved claim"],
                                cutoff="2025-01-01T00:00:00Z",
                            )
            self.assertEqual(result["status"], "scored")
            e2_score.assert_called_once()
            self.assertTrue(scoring_adapter.controls._E2_MODEL_LOCK_VERIFIED)
            self.assertIsNone(novelty._MODEL)
        finally:
            scoring_adapter.controls._E2_MODEL_LOCK_VERIFIED = previous_verified
            novelty.CACHE_DB = previous_cache
            for key, value in previous_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
