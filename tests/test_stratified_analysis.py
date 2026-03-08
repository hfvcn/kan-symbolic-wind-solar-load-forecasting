from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.eval.stratified_analysis import analyze_frame, load_run_frame


class TestStratifiedAnalysis(unittest.TestCase):
    def test_main_target_builds_season_weekpart_and_volatility(self) -> None:
        index = pd.date_range("2024-01-05", periods=6, freq="12h", tz="UTC")
        frame = pd.DataFrame(
            {
                "y_true": [10, 12, 9, 20, 22, 24],
                "y_pred": [11, 11, 10, 18, 21, 25],
                "delta_net_load_h6": [1, -2, 3, -4, 5, -6],
                "is_night": [False, True, False, True, False, True],
                "ghi_w_m2": [0.1, 0.0, 0.5, 0.0, 0.9, 0.0],
                "wind_speed_10m_m_s": [1, 2, 3, 4, 5, 6],
            },
            index=index,
        )

        out = analyze_frame(frame, target_col="delta_net_load_h6")

        self.assertEqual(set(out["family"]), {"season", "weekpart", "volatility"})
        self.assertEqual(set(out.loc[out["family"] == "weekpart", "segment"]), {"weekday", "weekend"})
        self.assertEqual(set(out.loc[out["family"] == "volatility", "segment"]), {"high", "low", "mid"})

    def test_solar_quantiles_only_use_daytime_rows(self) -> None:
        index = pd.date_range("2024-03-01", periods=6, freq="h", tz="UTC")
        frame = pd.DataFrame(
            {
                "y_true": [0, 1, 2, 3, 4, 5],
                "y_pred": [0, 1, 2, 4, 4, 6],
                "is_night": [True, True, False, False, False, True],
                "ghi_w_m2": [0.0, 0.0, 0.2, 0.5, 0.8, 0.0],
                "wind_speed_10m_m_s": [1, 1, 1, 1, 1, 1],
                "delta_solar_h72": [0, 0, 1, 2, 3, 0],
            },
            index=index,
        )

        out = analyze_frame(frame, target_col="delta_solar_h72")

        self.assertEqual(set(out["family"]), {"day_night", "ghi_quantile"})
        ghi = out[out["family"] == "ghi_quantile"]
        self.assertEqual(int(ghi["n"].sum()), 3)
        self.assertEqual(set(out.loc[out["family"] == "day_night", "segment"]), {"day", "night"})

    def test_load_run_frame_joins_predictions_and_processed_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            run_dir = root / "runs" / "demo_run"
            artifacts = run_dir / "artifacts"
            data_dir = root / "runs" / "data_run" / "processed"
            artifacts.mkdir(parents=True)
            data_dir.mkdir(parents=True)

            payload = {
                "run_id": "demo_run",
                "phase": "02-kan-training",
                "data_run_id": "data_run",
                "data_timestamp": "2026-03-09_0900",
                "cfg": {"target_col": "delta_wind_h72"},
            }
            (run_dir / "payload.json").write_text(json.dumps(payload))

            index = pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC", name="timestamp")
            pred_df = pd.DataFrame({"y_true": [1.0, 2.0, 3.0], "y_pred": [1.5, 2.5, 2.5]}, index=index)
            pred_df.to_parquet(artifacts / "predictions_test_reconstructed.parquet")

            test_df = pd.DataFrame(
                {
                    "is_night": [False, True, False],
                    "ghi_w_m2": [0.1, 0.0, 0.4],
                    "wind_speed_10m_m_s": [3.0, 4.0, 5.0],
                    "delta_wind_h72": [10.0, -5.0, 2.0],
                },
                index=index,
            )
            test_df.to_parquet(data_dir / "test_2026-03-09_0900.parquet")

            target_col, frame = load_run_frame(run_dir)

            self.assertEqual(target_col, "delta_wind_h72")
            self.assertEqual(list(frame.columns), ["y_true", "y_pred", "delta_wind_h72", "ghi_w_m2", "is_night", "wind_speed_10m_m_s"])
            self.assertEqual(len(frame), 3)


if __name__ == "__main__":
    unittest.main()
