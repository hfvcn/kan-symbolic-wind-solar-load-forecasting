import unittest

import numpy as np
import sympy as sp


class TestSensitivity(unittest.TestCase):
    def test_compute_partials_matches_known_derivatives(self) -> None:
        from src.kan_sr.sensitivity import compute_partials

        x0, x1 = sp.symbols("x0 x1")
        expr = 2 * x0 + sp.sin(3 * x1)

        partials = compute_partials(expr, [x0, x1])
        self.assertEqual(sp.simplify(partials["x0"]), sp.Integer(2))
        self.assertEqual(sp.simplify(partials["x1"]), 3 * sp.cos(3 * x1))

    def test_summarize_derivative_constant(self) -> None:
        from src.kan_sr.sensitivity import summarize_derivative

        values = np.full(100, 2.0, dtype=np.float64)
        s = summarize_derivative(values, var="x0")
        self.assertAlmostEqual(s.mean, 2.0, places=12)
        self.assertAlmostEqual(s.median, 2.0, places=12)
        self.assertAlmostEqual(s.min, 2.0, places=12)
        self.assertAlmostEqual(s.max, 2.0, places=12)
        self.assertAlmostEqual(s.pct_positive, 1.0, places=12)
        self.assertAlmostEqual(s.pct_negative, 0.0, places=12)
        self.assertEqual(s.n, 100)

    def test_summarize_derivative_filters_nan_inf(self) -> None:
        from src.kan_sr.sensitivity import summarize_derivative

        values = np.asarray([1.0, np.nan, np.inf, -np.inf, -2.0], dtype=np.float64)
        s = summarize_derivative(values, var="x0")
        self.assertEqual(s.n, 2)
        self.assertAlmostEqual(s.mean, -0.5, places=12)
        self.assertAlmostEqual(s.pct_positive, 0.5, places=12)
        self.assertAlmostEqual(s.pct_negative, 0.5, places=12)


if __name__ == "__main__":
    unittest.main()

