import tempfile
import unittest
from pathlib import Path


class TestKANPruneCheckpointPath(unittest.TestCase):
    def test_prune_helper_avoids_ckpt_history_dependency(self) -> None:
        import torch
        from kan import KAN

        from src.kan_sr.prune import prune_kan_model

        x = torch.randn(64, 2)

        with tempfile.TemporaryDirectory() as td:
            ckpt_path = Path(td) / "missing_ckpt_dir"
            self.assertFalse(ckpt_path.exists())

            # pykan's `KAN.prune()` can try to write ckpt_path/history.txt and crash if the
            # directory doesn't exist (even when the original model has auto_save=False).
            model = KAN(width=[2, 4, 1], grid=5, k=3, grid_range=[-5, 5], seed=1, auto_save=False, ckpt_path=str(ckpt_path), device="cpu")
            _ = model(x)
            with self.assertRaises((FileNotFoundError, OSError)):
                _ = model.prune(node_th=0.01, edge_th=0.01)

            # Our helper should prune without touching ckpt_path.
            model2 = KAN(width=[2, 4, 1], grid=5, k=3, grid_range=[-5, 5], seed=1, auto_save=False, ckpt_path=str(ckpt_path), device="cpu")
            pruned = prune_kan_model(model2, x, node_th=0.01, edge_th=0.01)
            with torch.no_grad():
                y = pruned(x)
            self.assertTrue(torch.isfinite(y).all().item())


if __name__ == "__main__":
    unittest.main()

