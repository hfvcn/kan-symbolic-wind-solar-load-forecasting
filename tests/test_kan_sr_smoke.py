import unittest

import numpy as np
import pandas as pd


class TestKANSRSanity(unittest.TestCase):
    def test_build_dataset_and_train_tiny(self) -> None:
        import torch
        from kan import KAN

        from src.kan_sr.dataset import build_kan_dataset
        from src.kan_sr.sparsity import compute_edge_sparsity

        rng = np.random.default_rng(1)
        x = rng.standard_normal((200, 2)).astype(np.float32)
        y = (x[:, 0] * 2.0 + np.sin(x[:, 1] * 3.0)).astype(np.float32)

        df = pd.DataFrame(x, columns=["x0", "x1"])
        df["y"] = y

        train_df = df.iloc[:150].copy()
        val_df = df.iloc[150:].copy()

        dataset, meta = build_kan_dataset(train_df, val_df, target_col="y", feature_cols=["x0", "x1"], scale_target=True)

        model = KAN(width=[2, 4, 1], grid=5, k=3, grid_range=[-5, 5], seed=1, auto_save=False, device="cpu")
        model.fit(dataset, opt="Adam", steps=30, lr=0.01, log=10, lamb=0.0, update_grid=True, grid_update_num=5, stop_grid_update_step=30)

        # Ensure forward works and sparsity structure is well-formed.
        with torch.no_grad():
            pred = model(dataset["test_input"])
        self.assertEqual(tuple(pred.shape), tuple(dataset["test_label"].shape))

        sparsity = compute_edge_sparsity(model)
        self.assertGreater(sparsity.total_edges, 0)
        self.assertGreaterEqual(sparsity.pruned_edges, 0)


if __name__ == "__main__":
    unittest.main()

