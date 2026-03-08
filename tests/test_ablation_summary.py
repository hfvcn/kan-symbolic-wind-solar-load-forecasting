import io
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.eval.ablation_summary import AblationSummaryConfig, summarize_run, write_csv


class TestAblationSummary(unittest.TestCase):
    def test_wind_summary_counts_feature_edges_and_abs_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            run_dir = Path(d) / "runs" / "wind_h2"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)

            payload = {
                "run_id": "wind_h2",
                "phase": "02-kan-training",
                "kind": "exp_longh_wind_delta_h2",
                "cfg": {"target_col": "delta_wind_h2"},
            }
            (run_dir / "payload.json").write_text(json.dumps(payload))

            pd.DataFrame(
                {
                    "y_true": [0.0, 1.0, 2.0, 3.0],
                    "y_pred": [0.0, 1.0, 2.0, 2.0],
                }
            ).to_parquet(artifacts / "predictions_test.parquet", compression="snappy")
            pd.DataFrame(
                {
                    "y_true": [10.0, 12.0, 14.0, 16.0, 18.0],
                    "y_pred": [10.0, 12.0, 14.0, 15.0, 19.0],
                }
            ).to_parquet(artifacts / "predictions_test_reconstructed.parquet", compression="snappy")
            (artifacts / "eval_pruned.json").write_text(json.dumps({"rmse": 3.0, "r2": 0.25}))
            pd.DataFrame(
                [
                    {"feature": "wind_speed_10m_m_s", "active_edges": 2},
                    {"feature": "wind_speed_10m_m_s_cubed", "active_edges": 3},
                    {"feature": "wind_speed_hub_est", "active_edges": 1},
                    {"feature": "wind_lag_24", "active_edges": 5},
                ]
            ).to_csv(artifacts / "feature_importance.csv", index=False)

            config = AblationSummaryConfig(
                target_prefix="delta_wind",
                edge_field_name="wind_speed_edges",
                feature_prefixes=("wind_speed_",),
            )
            row = summarize_run(run_dir, config=config, require_abs=True)

            self.assertEqual(row["run_id"], "wind_h2")
            self.assertEqual(row["target_col"], "delta_wind_h2")
            self.assertEqual(row["horizon_steps"], 2)
            self.assertEqual(row["wind_speed_edges"], 6)
            self.assertAlmostEqual(float(row["delta_test_rmse"]), 0.5, places=6)
            self.assertAlmostEqual(float(row["abs_test_rmse_persist"]), 4.0, places=6)
            self.assertAlmostEqual(float(row["abs_test_rmse"]), 0.8164965809, places=6)

    def test_write_csv_uses_configured_edge_field(self) -> None:
        output = io.StringIO()
        row = {
            "run_id": "r1",
            "kind": "wind",
            "target_col": "delta_wind_h2",
            "horizon_steps": 2,
            "abs_test_rmse": 1.0,
            "abs_test_r2": 0.5,
            "abs_test_rmse_persist": 2.0,
            "abs_test_skill": 0.5,
            "delta_test_rmse": 1.5,
            "delta_test_r2": 0.25,
            "delta_val_rmse": 2.0,
            "delta_val_r2": 0.2,
            "wind_speed_edges": 4,
        }

        write_csv([row], edge_field_name="wind_speed_edges", output=output)

        text = output.getvalue()
        self.assertIn("wind_speed_edges", text.splitlines()[0])
        self.assertIn(",4", text.splitlines()[1])


if __name__ == "__main__":
    unittest.main()
