import unittest

import numpy as np
import pandas as pd
import sympy as sp


class TestSeedFeatures(unittest.TestCase):
    def test_extracts_multi_symbol_seeds(self) -> None:
        from src.eval.seed_features import extract_seed_features

        x0, x1, x2 = sp.symbols("x0 x1 x2")
        expr = x0 + x1 * x2 + sp.sin(x0) + (x1 + 1) * (x2 - 2)

        seeds = extract_seed_features(expr, max_seeds=5, max_nodes=20, require_multi_symbol=True)
        self.assertGreaterEqual(len(seeds), 1)
        self.assertTrue(all(s.symbol_count >= 2 for s in seeds))

    def test_compute_seed_matrix_finite(self) -> None:
        from src.eval.seed_features import compute_seed_matrix, extract_seed_features

        x0, x1 = sp.symbols("x0 x1")
        expr = (x0 + 1) * (x1 - 2)
        seeds = extract_seed_features(expr, max_seeds=3, max_nodes=20, require_multi_symbol=True)

        rng = np.random.default_rng(0)
        df = pd.DataFrame({"x0": rng.normal(size=200), "x1": rng.normal(size=200)})

        mat, names, kept = compute_seed_matrix(seeds, feature_cols=["x0", "x1"], x_df=df)
        self.assertEqual(mat.shape[0], len(df))
        self.assertEqual(mat.shape[1], len(names))
        self.assertEqual(len(kept), len(names))
        self.assertTrue(np.isfinite(mat).all())


if __name__ == "__main__":
    unittest.main()

