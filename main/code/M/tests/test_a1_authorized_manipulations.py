import json
import unittest
from datetime import timedelta
from pathlib import Path

from M.a1_replication.controls import build_controls, score_control
from M.a1_replication.generate_authorized_manipulations import (
    build_manipulations,
    generate,
    parse_time,
    stable_id,
)


class AuthorizedManipulationTests(unittest.TestCase):
    def setUp(self):
        self.focal = {
            "paper_id": "focal",
            "pool": "machine_learning",
            "published": "2026-10-21T08:11:52Z",
            "title": "Focal title",
            "abstract": "Focal abstract",
        }
        self.claims = [
            {"claim_number": index, "claim": f"Claim {index}",
             "evidence": f"Evidence {index}"}
            for index in range(1, 8)
        ]
        self.papers = {
            "prior-a": {"paper_id": "prior-a", "published": "2025-01-01T00:00:00Z"},
            "prior-b": {"paper_id": "prior-b", "published": "2026-01-01T00:00:00Z"},
            "future": {"paper_id": "future", "published": "2026-11-01T00:00:00Z"},
        }

    def controls(self):
        return build_controls(
            focal=self.focal,
            original_input_ids=["prior-a", "prior-b"],
            papers=self.papers,
            other_instances=[{
                "paper_id": "other",
                "published": "2026-10-01T00:00:00Z",
                "question": "Other focal",
                "input_paper_ids": ["prior-a", "future"],
            }],
        )

    def test_registered_coverage_rounding_and_claim_order(self):
        cases, synthetic = build_manipulations(
            self.focal, self.claims, ["prior-a", "prior-b"], self.controls()
        )
        coverage = {case["manipulation"]: case for case in cases
                    if case["manipulation"].startswith("coverage_")}
        expected = {
            "coverage_25": [1, 2],
            "coverage_50": [1, 2, 3, 4],
            "coverage_75": [1, 2, 3, 4, 5, 6],
            "coverage_100": [1, 2, 3, 4, 5, 6, 7],
        }
        self.assertEqual(
            {name: case["metadata"]["selected_claim_numbers"]
             for name, case in coverage.items()},
            expected,
        )
        self.assertTrue(all(case["claims"] == [c["claim"] for c in self.claims]
                            for case in cases))
        self.assertEqual(len(synthetic), 4 + 1 + 7)
        self.assertTrue(all(
            parse_time(row["published"]) ==
            parse_time(self.focal["published"]) - timedelta(seconds=1)
            for row in synthetic
        ))

    def test_concentrated_and_distributed_definitions(self):
        cases, synthetic = build_manipulations(
            self.focal, self.claims, ["prior-a", "prior-b"], self.controls()
        )
        concentrated = next(c for c in cases if c["manipulation"] == "concentrated")
        distributed = next(c for c in cases if c["manipulation"] == "distributed")
        by_id = {row["paper_id"]: row for row in synthetic}
        self.assertEqual(len(concentrated["metadata"]["synthetic_paper_ids"]), 1)
        self.assertEqual(
            by_id[concentrated["metadata"]["synthetic_paper_ids"][0]]["abstract"],
            "\n".join(claim["claim"] for claim in self.claims),
        )
        distributed_ids = distributed["metadata"]["synthetic_paper_ids"]
        self.assertEqual(len(distributed_ids), len(self.claims))
        self.assertEqual(
            [by_id[paper_id]["abstract"] for paper_id in distributed_ids],
            [claim["claim"] for claim in self.claims],
        )

    def test_control_cases_are_temporal_and_empty_and_decoy_are_not_scored(self):
        controls = self.controls()
        self.assertEqual(
            [control["condition"] for control in controls],
            ["original", "empty", "shuffled", "same_topic_decoy"],
        )
        self.assertEqual(controls[0]["input_paper_ids"], ["prior-a", "prior-b"])
        self.assertEqual(controls[2]["input_paper_ids"], ["prior-a"])
        self.assertEqual(controls[1]["score_status"], "undefined")
        self.assertEqual(controls[1]["input_paper_ids"], [])
        self.assertEqual(controls[3]["status"], "unavailable")
        self.assertNotIn("input_paper_ids", controls[3])
        cutoff = parse_time(self.focal["published"])
        for control in (controls[0], controls[2]):
            self.assertTrue(all(
                parse_time(self.papers[paper_id]["published"]) < cutoff
                for paper_id in control["input_paper_ids"]
            ))
        self.assertEqual(
            score_control(controls[1], None, claims=[], cutoff=self.focal["published"])["status"],
            "undefined",
        )
        with self.assertRaisesRegex(ValueError, "unavailable and cannot be scored"):
            score_control(controls[3], None, claims=[], cutoff=self.focal["published"])

    def test_stable_synthetic_ids_and_case_ids(self):
        first_cases, first_synthetic = build_manipulations(
            self.focal, self.claims, ["prior-a", "prior-b"], self.controls()
        )
        second_cases, second_synthetic = build_manipulations(
            self.focal, self.claims, ["prior-a", "prior-b"], self.controls()
        )
        self.assertEqual(
            [case["case_id"] for case in first_cases],
            [case["case_id"] for case in second_cases],
        )
        self.assertEqual(
            [row["paper_id"] for row in first_synthetic],
            [row["paper_id"] for row in second_synthetic],
        )
        self.assertEqual(
            stable_id("sha256:E2-manipulations-v1", "machine_learning",
                      "focal", "coverage_25", "planted"),
            first_cases[1]["metadata"]["synthetic_paper_ids"][0],
        )

    def test_authorized_frozen_inputs_validate_and_match_saved_artifacts(self):
        inputs, report = generate()
        root = Path(__file__).resolve().parents[1] / "a1_replication"
        saved_inputs = (root / "A1_AUTHORIZED_MANIPULATIONS_V1.json").read_text(
            encoding="utf-8"
        )
        saved_report = (
            root / "A1_AUTHORIZED_MANIPULATIONS_VALIDATION_V1.json"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            saved_inputs, json.dumps(inputs, ensure_ascii=False, indent=2) + "\n"
        )
        self.assertEqual(
            saved_report, json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        )
        self.assertEqual(len(inputs["manipulation_cases"]), 14)
        self.assertEqual(report["validation_status"], "passed")


if __name__ == "__main__":
    unittest.main()
