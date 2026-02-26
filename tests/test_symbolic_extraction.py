import unittest

import numpy as np
import pandas as pd


class TestSymbolicExtraction(unittest.TestCase):
    def test_extracts_reasonable_formula_on_linear(self) -> None:
        import torch
        from kan import KAN

        from src.kan_sr.symbolic import (
            build_symbolic_formula,
            evaluate_symbolic_formula,
            extract_symbolic_edges,
        )

        rng = np.random.default_rng(0)
        x = rng.uniform(-1, 1, size=(600, 2)).astype(np.float32)
        y = (x[:, 0] + x[:, 1]).astype(np.float32)

        df = pd.DataFrame(x, columns=["x0", "x1"])
        df["y"] = y

        x_t = torch.tensor(df[["x0", "x1"]].to_numpy(dtype=np.float32))
        y_t = torch.tensor(df[["y"]].to_numpy(dtype=np.float32))
        dataset = {"train_input": x_t[:500], "train_label": y_t[:500], "test_input": x_t[500:], "test_label": y_t[500:]}

        # Narrow width makes it easier to recover a clean formula.
        model = KAN(width=[2, 1, 1], grid=5, k=3, grid_range=[-5, 5], seed=1, auto_save=False, device="cpu")
        model.fit(dataset, opt="LBFGS", steps=40, lamb=0.001, log=10)

        # Populate activations then fix edges.
        _ = model(dataset["train_input"])
        _ = extract_symbolic_edges(model, r2_threshold=0.95, fix_below_threshold_to_zero=False, lib=("x", "x^2", "x^3", "sin", "cos"))

        expr = build_symbolic_formula(model, feature_cols=["x0", "x1"])
        pred = evaluate_symbolic_formula(expr, feature_cols=["x0", "x1"], x_df=df.iloc[500:])
        true = df.iloc[500:]["y"].to_numpy(dtype=np.float64)

        rmse = float(np.sqrt(np.mean((pred - true) ** 2)))
        self.assertLess(rmse, 0.05)


if __name__ == "__main__":
    unittest.main()

