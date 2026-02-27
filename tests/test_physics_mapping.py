import unittest

import numpy as np
import pandas as pd
import sympy as sp


class TestPhysicsMapping(unittest.TestCase):
    def test_detects_cubic_wind_term(self) -> None:
        from src.eval.physics_mapping import contains_integer_power

        v = sp.Symbol("wind_speed_10m_m_s")
        expr = 0.5 * v**3 + 2 * v
        self.assertTrue(contains_integer_power(expr, v, 3))
        self.assertFalse(contains_integer_power(expr, v, 4))

    def test_analyze_physics_wind_monotone(self) -> None:
        from src.eval.physics_mapping import analyze_physics

        v = sp.Symbol("wind_speed_10m_m_s")
        # y = v^3 => dy/dv = 3 v^2 >= 0
        expr = v**3

        rng = np.random.default_rng(0)
        df = pd.DataFrame(
            {
                "wind_speed_10m_m_s": rng.normal(size=500).astype(np.float64),
                "x_dummy": rng.normal(size=500).astype(np.float64),
            }
        )

        rep = analyze_physics(expr, feature_cols=["wind_speed_10m_m_s", "x_dummy"], x_df=df, target_col="wind")
        checks = {c["name"]: c for c in rep["checks"]}
        self.assertIn("wind_speed_cubic_term", checks)
        self.assertTrue(checks["wind_speed_cubic_term"]["passed"])
        self.assertIn("wind_speed_monotone_increasing", checks)
        # dy/dv should never be negative for v^3
        summ = checks["wind_speed_monotone_increasing"]["details"]["derivative_summary"]
        self.assertAlmostEqual(float(summ["pct_negative"]), 0.0, places=12)

    def test_analyze_physics_net_load_decreasing(self) -> None:
        from src.eval.physics_mapping import analyze_physics

        v = sp.Symbol("wind_speed_10m_m_s")
        g = sp.Symbol("ghi_w_m2")
        # net_load should decrease as wind/GHI increase (proxy for more RE generation).
        expr = -(v**3) - 2 * g

        rng = np.random.default_rng(1)
        df = pd.DataFrame(
            {
                "wind_speed_10m_m_s": rng.normal(size=800).astype(np.float64),
                "ghi_w_m2": rng.normal(size=800).astype(np.float64),
            }
        )

        rep = analyze_physics(expr, feature_cols=["wind_speed_10m_m_s", "ghi_w_m2"], x_df=df, target_col="net_load")
        checks = {c["name"]: c for c in rep["checks"]}
        self.assertIn("wind_proxy_monotone_decreasing", checks)
        self.assertTrue(checks["wind_proxy_monotone_decreasing"]["passed"])
        self.assertIn("ghi_proxy_monotone_decreasing", checks)
        self.assertTrue(checks["ghi_proxy_monotone_decreasing"]["passed"])


if __name__ == "__main__":
    unittest.main()
