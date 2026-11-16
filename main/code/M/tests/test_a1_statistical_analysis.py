import unittest

from M.a1_replication.analyze_a1_results import AnalysisError, analyze


def target(focal, condition, scores):
    return {
        "target_id": f"{focal}:{condition}",
        "focal_paper_id": focal,
        "condition": condition,
        "status": "scored",
        "result": {"status": "scored", "scores": scores},
    }


def fixture_results():
    focals = ("2512.23709v3", "2610.29385v1")
    conditions = (
        "baseline", "coverage_25", "coverage_50", "coverage_75",
        "coverage_100", "concentrated", "distributed", "shuffled",
    )
    rows = []
    for focal_index, focal in enumerate(focals):
        base = 1.0 + focal_index
        values = {
            "baseline": base,
            "coverage_25": base - 0.2,
            "coverage_50": base - 0.4,
            "coverage_75": base - 0.6,
            "coverage_100": base - 0.8,
            "concentrated": base - 0.3,
            "distributed": base - 0.1,
            "shuffled": base + 0.1,
        }
        for condition in conditions:
            score = values[condition]
            rows.append(target(focal, condition, {
                "Y": score, "density": score, "N": score, "yours": score,
            }))
    return {
        "schema": "M-A1-scoring-results-v1",
        "run_status": "completed",
        "authorization_commit": "a" * 40,
        "controls": {
            "empty": "undefined; no numeric score",
            "same_topic_decoy": "unavailable; not scored",
        },
        "scoring_targets": rows,
    }


class A1StatisticalAnalysisTests(unittest.TestCase):
    def test_registered_comparisons_and_cluster_bootstrap_are_deterministic(self):
        first = analyze(fixture_results())
        second = analyze(fixture_results())
        self.assertEqual(first, second)
        self.assertEqual(first["sample"]["independent_focal_clusters_n"], 2)
        self.assertEqual(first["sample"]["scored_targets_n"], 16)
        self.assertEqual(first["bootstrap"]["draws"], 2000)
        self.assertEqual(first["bootstrap"]["bit_generator"], "NumPy PCG64")
        self.assertEqual(first["bootstrap"]["seed"], 20261113)
        self.assertTrue(first["bootstrap"]["shared_draws_across_comparisons"])
        self.assertEqual(
            len(first["partial_coverage"]["coordinate_results"]["Y"]["partial_coverage_steps"]),
            4,
        )
        self.assertEqual(first["partial_coverage"]["registered_axiom_pass_fraction"]["Y"]
                         ["strict_axiom_pass_fraction"]["estimate"], 1.0)
        self.assertEqual(first["concentration"]["coordinate_results"]["Y"]
                         ["strict_axiom_pass_fraction"]["estimate"], 1.0)
        self.assertEqual(first["diagnostic_controls"]["empty_pool"]["numeric_score"], None)
        self.assertEqual(first["diagnostic_controls"]["same_topic_decoy"]["status"], "unavailable")

    def test_missing_scores_and_wrong_bootstrap_configuration_fail_closed(self):
        results = fixture_results()
        results["scoring_targets"].pop()
        with self.assertRaisesRegex(AnalysisError, "Incomplete conditions"):
            analyze(results)
        with self.assertRaisesRegex(AnalysisError, "requires 2,000 draws"):
            analyze(fixture_results(), draws_count=1999)

    def test_undefined_or_decoy_scores_are_never_accepted_as_numeric_targets(self):
        results = fixture_results()
        row = results["scoring_targets"][0]
        row["condition"] = "empty"
        with self.assertRaisesRegex(AnalysisError, "Undefined or unavailable condition"):
            analyze(results)
        results = fixture_results()
        results["controls"]["empty"] = "numeric substitute"
        with self.assertRaisesRegex(AnalysisError, "Empty-pool score must remain undefined"):
            analyze(results)


if __name__ == "__main__":
    unittest.main()
