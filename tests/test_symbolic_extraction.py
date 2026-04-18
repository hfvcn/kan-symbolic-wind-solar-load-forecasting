import unittest
from pathlib import Path

import numpy as np
import pandas as pd


class TestSymbolicExtraction(unittest.TestCase):
    def test_modal_symbolic_timeout_is_24_hours(self) -> None:
        source = Path("modal_jobs/kan_symbolic.py").read_text()
        self.assertIn("SYMBOLIC_TIMEOUT_S = 24 * 3600", source)
        self.assertNotIn("timeout=2 * 3600", source)

    def test_modal_symbolic_supports_submit_only(self) -> None:
        source = Path("modal_jobs/kan_symbolic.py").read_text()
        self.assertIn("submit_only: bool = False", source)
        self.assertIn("call = fn.spawn(", source)
        self.assertIn('"status": "submitted"', source)

    def test_modal_symbolic_has_cli_friendly_cpu_wrapper(self) -> None:
        source = Path("modal_jobs/kan_symbolic.py").read_text()
        self.assertIn("def extract_symbolic_cpu_cli(", source)
        self.assertIn("lib_csv: str = \"default\"", source)
        self.assertIn("device_name=\"cpu\"", source)

    def test_prime_symbolic_activations_replays_forward_on_cpu_after_gpu(self) -> None:
        from src.kan_sr.symbolic import prime_symbolic_activations

        class FakeNoGrad:
            def __enter__(self):
                return None

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeTorch:
            @staticmethod
            def no_grad():
                return FakeNoGrad()

        class FakeTensor:
            def __init__(self, device: str) -> None:
                self.device = device

            def to(self, device: str):
                return FakeTensor(device)

        class FakeModel:
            def __init__(self, device: str) -> None:
                self.device = device
                self.calls: list[tuple[str, str]] = []
                self.symbolic_fun = [FakeSymbolicLayer(device), FakeSymbolicLayer(device)]

            def to(self, device: str):
                self.device = device
                return self

            def __call__(self, x):
                self.calls.append((self.device, x.device))
                return None

        class FakeSymbolicLayer:
            def __init__(self, device: str) -> None:
                self.device = device

            def to(self, device: str):
                self.device = device
                return self

        model, x_sample = prime_symbolic_activations(
            FakeModel("cuda"),
            FakeTensor("cuda"),
            device_name="cuda",
            torch_mod=FakeTorch(),
        )

        self.assertEqual(model.device, "cpu")
        self.assertEqual(x_sample.device, "cpu")
        self.assertEqual(model.calls, [("cuda", "cuda"), ("cpu", "cpu")])
        self.assertTrue(all(layer.device == "cpu" for layer in model.symbolic_fun))

    def test_evaluate_symbolic_formula_broadcasts_scalar(self) -> None:
        import sympy as sp

        from src.kan_sr.symbolic import evaluate_symbolic_formula

        df = pd.DataFrame({"x0": [1.0, 2.0, 3.0], "x1": [0.0, 0.0, 0.0]})
        expr = sp.Integer(7)

        pred = evaluate_symbolic_formula(expr, feature_cols=["x0", "x1"], x_df=df)
        self.assertEqual(pred.shape, (3,))
        self.assertTrue(np.allclose(pred, 7.0))

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
