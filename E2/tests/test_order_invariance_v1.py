import itertools
import unittest
from unittest.mock import patch

import numpy as np

from E2.novelty import score


class TestScoreOrderInvariance(unittest.TestCase):

    def setUp(self):
        def unit(values):
            vector = np.asarray(values, dtype=np.float32)
            return vector / np.linalg.norm(vector)

        self.vectors = {
            "idea": unit([1.0, 0.0, 0.0]),
            "claim_a": unit([0.8, 0.6, 0.0]),
            "claim_b": unit([0.0, 1.0, 0.0]),
            "paper_a": unit([0.9, 0.43589, 0.0]),
            "paper_b": unit([0.0, 0.8, 0.6]),
            "paper_c": unit([-0.2, 0.9799, 0.0]),
        }

        self.paper_text = {
            "p1": "paper_a",
            "p2": "paper_b",
            "p3": "paper_c",
        }

    def mocked_encode(self, texts):
        return np.stack([self.vectors[text] for text in texts])

    def mocked_eligible(self, pool_ids, cutoff, idea_text):
        return [
            {"id": paper_id, "text": self.paper_text[paper_id]}
            for paper_id in pool_ids
        ]

    def calculate(self, claims, pool_ids):
        return score(
            "idea",
            list(claims),
            list(pool_ids),
            "2026-01-01T00:00:00Z",
        )

    def assert_scores_equal(self, first, second):
        for metric in ("Y", "N", "yours", "density"):
            self.assertAlmostEqual(
                first[metric],
                second[metric],
                places=12,
                msg="Metric changed after reordering: {}".format(metric),
            )

    def test_claim_order_does_not_change_scores(self):
        with patch(
            "E2.novelty._encode", side_effect=self.mocked_encode
        ), patch(
            "E2.novelty._eligible_papers",
            side_effect=self.mocked_eligible,
        ):
            baseline = self.calculate(
                ("claim_a", "claim_b"),
                ("p1", "p2", "p3"),
            )

            for claims in itertools.permutations(
                ("claim_a", "claim_b")
            ):
                result = self.calculate(claims, ("p1", "p2", "p3"))
                self.assert_scores_equal(baseline, result)

    def test_pool_order_does_not_change_scores(self):
        with patch(
            "E2.novelty._encode", side_effect=self.mocked_encode
        ), patch(
            "E2.novelty._eligible_papers",
            side_effect=self.mocked_eligible,
        ):
            baseline = self.calculate(
                ("claim_a", "claim_b"),
                ("p1", "p2", "p3"),
            )

            for pool_ids in itertools.permutations(("p1", "p2", "p3")):
                result = self.calculate(("claim_a", "claim_b"), pool_ids)
                self.assert_scores_equal(baseline, result)

    def test_rejects_empty_or_invalid_idea_text(self):
        for idea_text in ("", "   ", None):
            with self.subTest(idea_text=repr(idea_text)):
                with self.assertRaises(ValueError):
                    score(idea_text, ["claim_a"], ["p1"], "2026-01-01T00:00:00Z")

    def test_rejects_empty_or_invalid_claims(self):
        invalid_claim_sets = ([], [""], ["   "], [None], None)

        for claims in invalid_claim_sets:
            with self.subTest(claims=repr(claims)):
                with self.assertRaises(ValueError):
                    score("idea", claims, ["p1"], "2026-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
