import unittest

from M.prospective_grounding.exploratory_evidence.compare_review_responses import validate_and_compare


class ExploratoryReviewPairTests(unittest.TestCase):
    def test_pair_is_validated_and_compared_without_gate_promotion(self):
        result, ratings, associations = validate_and_compare()
        self.assertEqual(len(ratings), 18)
        self.assertEqual(len(associations), 6)
        self.assertEqual(result["rating_agreement"]["exact_agreement_n"], 17)
        self.assertAlmostEqual(result["rating_agreement"]["cohen_kappa_unweighted"], 0.9117647058823529)
        self.assertEqual(result["association_agreement"]["joint_decision_agreement_n"], 6)
        self.assertEqual(result["association_agreement"]["field_disagreement_count"], 0)
        self.assertFalse(result["validation"]["reviewer_1_independence_verified_externally"])
        self.assertFalse(result["validation"]["reviewer_2_independence_confirmed"])
        self.assertIn("no_preregistered_v2_scoring", result["status"])


if __name__ == "__main__":
    unittest.main()
