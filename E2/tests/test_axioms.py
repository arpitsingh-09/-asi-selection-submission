"""Mathematical tests for the E2 novelty measure.

These tests verify the idealised orthonormal-claim model.
They do not establish performance on real research papers.
"""

import math
import unittest


def distributed_y(m):
    return 1.0 - 1.0 / math.sqrt(m)


def distributed_n(m, j):
    return 1.0 - j / m


def concentrated_y(m, j):
    return 1.0 - math.sqrt(j / m)


def concentrated_n(m, j):
    return 1.0 - math.sqrt(j) / m


def score(y, n, alpha):
    return alpha * y + (1.0 - alpha) * n


class TestNoveltyAxioms(unittest.TestCase):

    def test_distributed_closed_forms(self):
        for m in range(2, 51):
            for j in range(1, m + 1):
                self.assertAlmostEqual(
                    distributed_y(m),
                    1.0 - 1.0 / math.sqrt(m),
                )
                self.assertAlmostEqual(
                    distributed_n(m, j),
                    1.0 - j / m,
                )

    def test_concentrated_closed_forms(self):
        for m in range(2, 51):
            for j in range(1, m + 1):
                self.assertAlmostEqual(
                    concentrated_y(m, j),
                    1.0 - math.sqrt(j / m),
                )
                self.assertAlmostEqual(
                    concentrated_n(m, j),
                    1.0 - math.sqrt(j) / m,
                )

    def test_gradient_axiom_for_alpha_grid(self):
        # Distributed novelty must strictly decrease as j increases.
        for alpha in [0.5001, 0.55, 0.75, 0.90, 0.99]:
            for m in range(2, 51):
                values = [
                    score(
                        distributed_y(m),
                        distributed_n(m, j),
                        alpha,
                    )
                    for j in range(1, m + 1)
                ]
                for earlier, later in zip(values, values[1:]):
                    self.assertLess(later, earlier)

    def test_concentration_axiom_for_alpha_grid(self):
        for alpha in [0.5001, 0.55, 0.75, 0.90, 0.99]:
            for m in range(2, 51):
                for j in range(2, m + 1):
                    distributed = score(
                        distributed_y(m),
                        distributed_n(m, j),
                        alpha,
                    )
                    concentrated = score(
                        concentrated_y(m, j),
                        concentrated_n(m, j),
                        alpha,
                    )
                    self.assertLess(concentrated, distributed)

    def test_boundary_values_fail_strict_axioms(self):
        # alpha = 0.5 fails strict concentration at j = m.
        for m in range(2, 20):
            distributed = score(
                distributed_y(m),
                distributed_n(m, m),
                0.5,
            )
            concentrated = score(
                concentrated_y(m, m),
                concentrated_n(m, m),
                0.5,
            )
            self.assertAlmostEqual(distributed, concentrated)

        # alpha = 1 ignores N, so distributed novelty does not decrease.
        for m in range(2, 20):
            first = score(distributed_y(m), distributed_n(m, 1), 1.0)
            second = score(distributed_y(m), distributed_n(m, 2), 1.0)
            self.assertAlmostEqual(first, second)

    def test_adding_papers_cannot_increase_score(self):
        # Abstract cosine similarities for a nonempty pool.
        # Adding candidates can only increase each maximum similarity.
        examples = [
            (0.2, 0.4, 0.1, 0.3),
            (-0.8, -0.4, -0.9, -0.2),
            (0.0, 0.0, 0.0, 0.0),
        ]

        alpha = 0.75

        for y_old, y_new, n_old, n_new in examples:
            # Similarities increase or stay unchanged after adding papers.
            self.assertGreaterEqual(y_new, y_old)
            self.assertGreaterEqual(n_new, n_old)

            old_score = score(1.0 - y_old, 1.0 - n_old, alpha)
            new_score = score(1.0 - y_new, 1.0 - n_new, alpha)

            self.assertLessEqual(new_score, old_score)


if __name__ == "__main__":
    unittest.main(verbosity=2)
