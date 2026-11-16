import hashlib
from pathlib import Path
import tempfile
import unittest

from M.prospective_grounding.generate import (
    GENERATOR_MODEL_ID,
    GENERATOR_PARAMETERS,
    PREREG_COMMIT,
    REPO_ROOT,
    SEEDS,
    make_plan,
    _claim_one_shot,
    verify_frozen_inputs,
    verify_preregistration,
)


class GenerationCliOfflineTests(unittest.TestCase):
    def test_preregistration_and_frozen_inputs_pass_offline(self):
        verify_preregistration(REPO_ROOT)
        manifest, requests = verify_frozen_inputs(REPO_ROOT)
        self.assertEqual(set(requests), {"video_memorability", "image_enhancement"})
        self.assertEqual({item["input_set_id"] for item in manifest["input_sets"]}, set(requests))

    def test_plan_has_exact_four_candidates_and_frozen_seed_schedule(self):
        _, requests = verify_frozen_inputs(REPO_ROOT)
        plan = make_plan(requests)
        self.assertEqual([(item["family"], item["kind"], item["seed"]) for item in plan], [
            ("video_memorability", "primary", 4900),
            ("video_memorability", "decoy", 4901),
            ("image_enhancement", "primary", 4910),
            ("image_enhancement", "decoy", 4911),
        ])
        self.assertEqual([len(item["request"]["input_records"]) for item in plan], [3] * 4)
        for item in plan:
            request = item["request"]
            self.assertEqual(request["prompt_sha256"], hashlib.sha256(request["prompt"].encode()).hexdigest())

    def test_model_and_settings_are_preregistered(self):
        self.assertEqual(PREREG_COMMIT, "76c084a0679a52973542df43aa87866dbd1be782")
        self.assertEqual(GENERATOR_MODEL_ID, "qwen3:8b")
        self.assertEqual(GENERATOR_PARAMETERS,
                         {"temperature": 0.7, "top_p": 0.8, "num_predict": 512})
        self.assertEqual(SEEDS, {"video_memorability": (4900, 4901), "image_enhancement": (4910, 4911)})

    def test_output_root_is_claimed_once_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "generated"
            _claim_one_shot(root)
            with self.assertRaises(RuntimeError):
                _claim_one_shot(root)


if __name__ == "__main__":
    unittest.main()
