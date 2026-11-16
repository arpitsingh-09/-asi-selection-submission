import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from M.prospective_grounding.generate_v2 import (
    GENERATOR_MODEL_ID,
    GENERATOR_PARAMETERS,
    OUTPUT_ROOT,
    REPO_ROOT,
    SEEDS,
    V1_PRESERVATION_SHA256,
    OllamaV2Generator,
    _claim_output,
    make_plan,
    verify_frozen_inputs,
    verify_v1_preserved,
)


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.data


class GenerateV2OfflineTests(unittest.TestCase):
    def test_v1_preservation_hashes_and_failure_record_are_unchanged(self):
        verify_v1_preserved(REPO_ROOT)
        failed = REPO_ROOT / "M/prospective_grounding/generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json"
        record = json.loads(failed.read_text())
        response = record["ollama_response"]["parsed"]
        self.assertEqual(record["status"], "FAILED")
        self.assertEqual(response["response"], "")
        self.assertTrue(response["thinking"])
        self.assertEqual(response["eval_count"], 512)
        self.assertEqual(set(V1_PRESERVATION_SHA256), {
            "M/PREREG.md",
            "M/prospective_grounding/PREREG_DRAFT.md",
            "M/prospective_grounding/workflow.py",
            "M/prospective_grounding/generate.py",
            "M/prospective_grounding/tests/test_workflow_safeguards.py",
            "M/prospective_grounding/tests/test_generate_cli.py",
            "M/prospective_grounding/generated_v1/ONE_SHOT_CLAIM.json",
            "M/prospective_grounding/generated_v1/run_20261115T023429_468521Z/run.json",
            "M/prospective_grounding/generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json",
        })

    def test_frozen_inputs_plan_and_reused_seed_schedule(self):
        _, requests = verify_frozen_inputs(REPO_ROOT)
        plan = make_plan(requests)
        self.assertEqual([item["seed"] for item in plan], [4900, 4901, 4910, 4911])
        self.assertEqual(SEEDS, {"video_memorability": (4900, 4901), "image_enhancement": (4910, 4911)})
        self.assertEqual(len(plan), 4)
        for item in plan:
            request = item["request"]
            self.assertEqual(len(request["input_records"]), 3)
            self.assertEqual(request["prompt_sha256"], hashlib.sha256(request["prompt"].encode()).hexdigest())

    def test_ollama_request_sends_think_false_and_locked_options_once(self):
        captured = []
        body = {"model": GENERATOR_MODEL_ID, "created_at": "2026-11-15T00:00:00Z",
                "response": "fixture", "thinking": "", "done": True}

        def opener(request, timeout):
            captured.append((request, timeout))
            return FakeResponse(json.dumps(body).encode())

        generator = OllamaV2Generator(opener=opener)
        result = generator(prompt="fixed prompt", model_id=GENERATOR_MODEL_ID,
                           parameters=GENERATOR_PARAMETERS, seed=4900)
        self.assertEqual(result, "fixture")
        self.assertEqual(len(captured), 1)
        payload = json.loads(captured[0][0].data)
        self.assertIs(payload["think"], False)
        self.assertEqual(payload["options"], {**GENERATOR_PARAMETERS, "seed": 4900})
        self.assertEqual(payload["prompt"], "fixed prompt")

    def test_empty_response_is_saved_by_adapter_and_fails_without_retry(self):
        captured = []
        body = {"model": GENERATOR_MODEL_ID, "created_at": "2026-11-15T00:00:00Z",
                "response": "", "thinking": "reasoning", "done": True, "eval_count": 512}

        def opener(request, timeout):
            captured.append(request)
            return FakeResponse(json.dumps(body).encode())

        generator = OllamaV2Generator(opener=opener)
        with self.assertRaisesRegex(RuntimeError, "stops without retry"):
            generator(prompt="fixed prompt", model_id=GENERATOR_MODEL_ID,
                      parameters=GENERATOR_PARAMETERS, seed=4900)
        self.assertEqual(len(captured), 1)
        self.assertEqual(generator.last_response["parsed"]["response"], "")
        self.assertEqual(generator.last_response["parsed"]["eval_count"], 512)

    def test_v2_output_root_is_one_shot_and_isolated_from_v1(self):
        self.assertEqual(OUTPUT_ROOT.name, "generated_v2")
        self.assertFalse(OUTPUT_ROOT.exists())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "generated_v2"
            _claim_output(root)
            with self.assertRaises(RuntimeError):
                _claim_output(root)


if __name__ == "__main__":
    unittest.main()
