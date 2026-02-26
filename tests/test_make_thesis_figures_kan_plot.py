import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


class TestMakeThesisFiguresKANPlot(unittest.TestCase):
    def test_with_kan_plot_generates_topology_png(self) -> None:
        import torch
        from kan import KAN

        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "make_thesis_figures.py"

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            runs_dir = tmp / "runs"
            runs_dir.mkdir(parents=True, exist_ok=True)

            data_run_id = "data_run"
            data_ts = "2026-01-01_000000"
            feature_cols = ["x0", "x1"]

            processed_dir = runs_dir / data_run_id / "processed"
            processed_dir.mkdir(parents=True, exist_ok=True)

            rng = np.random.default_rng(1)
            x = rng.standard_normal((256, 2)).astype(np.float32)
            df = pd.DataFrame(x, columns=feature_cols)
            df["y"] = (x[:, 0] * 0.5 + np.sin(x[:, 1])).astype(np.float32)
            df.to_parquet(processed_dir / f"train_{data_ts}.parquet", compression="snappy")

            run_id = "kan_run"
            ckpt_dir = runs_dir / run_id / "checkpoint"
            ckpt_dir.mkdir(parents=True, exist_ok=True)

            model = KAN(width=[2, 3, 1], grid=3, k=3, grid_range=[-5, 5], seed=1, auto_save=False, device="cpu")
            ckpt = {
                "model_state": model.state_dict(),
                "payload": {
                    "cfg": {
                        "target_col": "y",
                        "hidden_width": 3,
                        "hidden_mult": 0,
                        "mult_arity": 2,
                        "grid": 3,
                        "k": 3,
                        "grid_range_min": -5.0,
                        "grid_range_max": 5.0,
                        "seed": 1,
                    },
                    "data_run_id": data_run_id,
                    "data_timestamp": data_ts,
                },
                "feature_cols": feature_cols,
            }
            torch.save(ckpt, ckpt_dir / "model.pt")

            out_dir = tmp / "paper_assets" / "figures"
            out_dir.mkdir(parents=True, exist_ok=True)

            subprocess.check_call(
                [
                    sys.executable,
                    str(script),
                    "--out-dir",
                    str(out_dir),
                    "--run",
                    str(runs_dir / run_id),
                    "--with-kan-plot",
                ],
                cwd=str(repo_root),
            )

            plot_dir = out_dir / f"kan_plot_{run_id}"
            self.assertTrue((plot_dir / "topology.png").exists())
            self.assertGreater(len(list(plot_dir.glob("sp_*.png"))), 0)


if __name__ == "__main__":
    unittest.main()

