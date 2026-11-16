"""Offline validation tests for development-only token profile artifacts."""

import sys
import json
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from profile_development_token_budget import (
    ARMS,
    build_profile_attestation,
    load_development_manifest,
    run_development_profile,
    summarize_development_token_profile,
)


class DevelopmentTokenProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.manifest_sha = load_development_manifest()

    def _envelope(self, record, used=100):
        return {
            "paper_id": record["paper_id"],
            "execution_mode": "development_profile",
            "arms": {arm: {"execution_status": "succeeded"} for arm in ARMS},
            "token_budget_accounting": {
                arm: {"tokens_used": used, "budget_status": "within_budget"}
                for arm in ARMS
            },
        }

    def test_partial_profile_checkpoints_survive_later_runner_failure(self):
        calls = []
        def runner(record, task, cap):
            calls.append(record)
            if len(calls) == 2:
                raise RuntimeError("interrupted development run")
            return self._envelope(record)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                run_development_profile(task_text="Generic task", profile_cap=500,
                                        runner=runner, limit=2, checkpoint_dir=Path(directory))
            saved = json.loads((Path(directory) / "record_01.json").read_text())
            self.assertEqual(saved[0]["paper_id"], self.manifest["inputs"][0]["paper_id"])
            self.assertFalse((Path(directory) / "record_02.json").exists())

    def test_partial_profile_limit_and_exclusive_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            kwargs = dict(task_text="Generic task", profile_cap=500,
                          runner=lambda record, task, cap: self._envelope(record),
                          limit=1, checkpoint_dir=Path(directory))
            profile = run_development_profile(**kwargs)
            self.assertEqual(len(profile["profiled_input_set_ids"]), 1)
            with self.assertRaises(FileExistsError):
                run_development_profile(**kwargs)
        for limit in (0, 11, True):
            with self.assertRaisesRegex(ValueError, "limit"):
                run_development_profile(task_text="Generic task", profile_cap=500,
                                        runner=lambda *args: {}, limit=limit)

    def test_profile_reports_observed_usage_without_setting_protocol_cap(self):
        records = self.manifest["inputs"][:2]
        profile = summarize_development_token_profile(
            self.manifest, [self._envelope(records[0], 100), self._envelope(records[1], 130)],
            manifest_sha256=self.manifest_sha, profile_cap=500,
        )
        self.assertEqual(profile["status"], "development_profile_descriptive_pending_review")
        self.assertFalse(profile["confirmatory_experiment"])
        self.assertFalse(profile["configured_e6_token_cap_changed"])
        self.assertEqual(profile["arms"]["D"]["maximum_tokens"], 130)
        self.assertEqual(profile["arms"]["D"]["candidate_floor_from_observed_complete_runs"], 130)

    def test_evaluation_ids_and_non_profile_envelopes_are_rejected(self):
        bad = self._envelope(self.manifest["inputs"][0])
        bad["paper_id"] = "not-a-development-id"
        with self.assertRaisesRegex(ValueError, "not an authorized development"):
            summarize_development_token_profile(
                self.manifest, [bad], manifest_sha256=self.manifest_sha, profile_cap=500,
            )

    def test_missing_arm_accounting_and_invalid_caps_fail_closed(self):
        envelope = self._envelope(self.manifest["inputs"][0])
        del envelope["token_budget_accounting"]["D-empty"]
        with self.assertRaisesRegex(ValueError, "complete seven-arm"):
            summarize_development_token_profile(
                self.manifest, [envelope], manifest_sha256=self.manifest_sha, profile_cap=500,
            )
        with self.assertRaisesRegex(ValueError, "positive temporary"):
            summarize_development_token_profile(
                self.manifest, [], manifest_sha256=self.manifest_sha, profile_cap=0,
            )

    def test_profile_attestation_is_bound_to_manifest_and_task(self):
        value = build_profile_attestation(
            self.manifest_sha, "Generic research task",
            task_matches_profile_constant=True,
        )
        self.assertEqual(value["scope"], "e6_development_token_profile_only")
        self.assertTrue(value["task_matches_profile_constant"])
        self.assertEqual(len(value["task_sha256"]), 64)

    def test_runner_is_invoked_only_for_the_ten_existing_development_rows(self):
        seen = []

        def runner(record, task_text, profile_cap):
            seen.append(record["paper_id"])
            self.assertEqual(task_text, "Reviewed generic task")
            self.assertEqual(profile_cap, 1000)
            return self._envelope(record, used=200)

        profile = run_development_profile(
            task_text="Reviewed generic task", profile_cap=1000, runner=runner,
        )
        self.assertEqual(len(seen), 10)
        self.assertEqual(set(seen), {row["paper_id"] for row in self.manifest["inputs"]})
        self.assertFalse(profile["confirmatory_experiment"])
        self.assertFalse(profile["configured_e6_token_cap_changed"])


if __name__ == "__main__":
    unittest.main()
