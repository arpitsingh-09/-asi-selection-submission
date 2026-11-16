import unittest

import numpy as np

from E2.novelty import _rnd_score


class TestRelativeNeighbourDensity(unittest.TestCase):

    def setUp(self):
        self.pool = np.array([
            [1.0, 0.0, 0.0],
            [0.99, 0.141067, 0.0],
            [0.98, 0.0, 0.198997],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [-1.0, 0.0, 0.0],
        ], dtype=np.float64)

        self.pool /= np.linalg.norm(
            self.pool, axis=1, keepdims=True
        )

        self.query = np.array([1.0, 0.0, 0.0])

    def test_score_is_between_zero_and_100(self):
        result = _rnd_score(self.query, self.pool, p=3, q=2)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 100.0)

    def test_score_is_deterministic(self):
        first = _rnd_score(self.query, self.pool, p=3, q=2)
        second = _rnd_score(self.query, self.pool, p=3, q=2)
        self.assertEqual(first, second)

    def test_rejects_pool_with_one_paper(self):
        with self.assertRaises(ValueError):
            _rnd_score(self.query, self.pool[:1])

    def test_caps_parameters_for_small_pools(self):
        result = _rnd_score(
            self.query, self.pool, p=100, q=100
        )
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 100.0)

    def test_default_parameters(self):
        self.assertEqual(_rnd_score.__defaults__, (100, 50))


if __name__ == "__main__":
    unittest.main()
