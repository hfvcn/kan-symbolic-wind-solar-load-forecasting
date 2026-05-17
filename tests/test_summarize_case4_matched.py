from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


PHYSICAL_FEATURES = [
    "wind_speed_10m_m_s",
    "wind_speed_10m_m_s_cubed",
    "wind_speed_hub_est",
    "ghi_w_m2",
    "ghi_day_w_m2",
    "ghi_temp_corr_w_m2",
    "temp_2m_c",
    "cdd_18c",
    "hdd_18c",
]


class TestSummarizeCase4Matched(unittest.TestCase):
    def _load_module(self, relative_path: str, name: str):
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / relative_path
        spec = importlib.util.spec_from_file_location(name, script)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Failed to import script module: {script}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _write_run(self, base: Path, run_id: str, *, active_features: dict[str, int], rmse: float) -> Path:
        run_dir = base / run_id
        artifacts = run_dir / "artifacts"
        artifacts.mkdir(parents=True, exist_ok=True)
        (run_dir / "payload.json").write_text(json.dumps({"run_id": run_id, "cfg": {"target_col": "delta_net_load_h6"}}))
        feature_rows = [{"feature": name, "active_edges": active_features.get(name, 0)} for name in PHYSICAL_FEATURES]
        feature_rows += [
            {"feature": "load_lag_12", "active_edges": active_features.get("load_lag_12", 0)},
            {"feature": "wind_lag_24", "active_edges": active_features.get("wind_lag_24", 0)},
            {"feature": "hour_sin", "active_edges": active_features.get("hour_sin", 0)},
        ]
        pd.DataFrame(feature_rows).to_csv(artifacts / "feature_importance.csv", index=False)
        (artifacts / "eval_pruned.json").write_text(json.dumps({"rmse": rmse}))
        pd.DataFrame([{"y_true": 0.0, "y_pred": rmse}]).to_parquet(artifacts / "predictions_test.parquet", index=False)
        return run_dir

    def test_writes_detail_and_summary_csv(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "summarize_case4_matched.py"

        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            out_dir = base / "out"
            u1 = self._write_run(base, "case4_u_seed1", active_features={}, rmse=10.0)
            u2 = self._write_run(base, "case4_u_seed2", active_features={"ghi_w_m2": 1}, rmse=12.0)
            b1 = self._write_run(base, "case4_b_seed1", active_features={"ghi_w_m2": 2, "temp_2m_c": 1}, rmse=9.0)
            b2 = self._write_run(base, "case4_b_seed2", active_features={"ghi_w_m2": 1}, rmse=11.0)

            subprocess.run(
                [
                    "python3",
                    str(script),
                    "--unblocked-run",
                    str(u1),
                    "--unblocked-run",
                    str(u2),
                    "--blocked-run",
                    str(b1),
                    "--blocked-run",
                    str(b2),
                    "--out-dir",
                    str(out_dir),
                    "--bootstrap-samples",
                    "200",
                ],
                check=True,
                cwd=str(repo_root),
            )

            detail_path = out_dir / "case4_matched_blocking_seed_detail_20260417.csv"
            summary_path = out_dir / "case4_matched_blocking_summary_20260417.csv"
            self.assertTrue(detail_path.exists())
            self.assertTrue(summary_path.exists())

            with detail_path.open() as fh:
                detail_rows = list(csv.DictReader(fh))
            with summary_path.open() as fh:
                summary_rows = list(csv.DictReader(fh))
            self.assertEqual(len(detail_rows), 2)
            any_row = next(row for row in summary_rows if row["metric"] == "any_physical_ver")
            rmse_row = next(row for row in summary_rows if row["metric"] == "final_test_rmse")
            self.assertEqual(any_row["unblocked_mean"], "0.5")
            self.assertEqual(any_row["blocked_mean"], "1.0")
            self.assertEqual(rmse_row["unblocked_mean"], "11.0")
            self.assertEqual(rmse_row["blocked_mean"], "10.0")

    def test_falls_back_to_checkpoint_mask(self) -> None:
        module = self._load_module("src/eval/case4_matched.py", "case4_matched")
        fake_torch = types.SimpleNamespace(
            load=lambda *args, **kwargs: {
                "model_state": {
                    "act_fun.0.mask": np.array(
                        [
                            [0, 1, 0],
                            [0, 0, 0],
                            [1, 1, 0],
                        ],
                        dtype=np.int64,
                    )
                }
            }
        )
        original_torch = sys.modules.get("torch")

        with tempfile.TemporaryDirectory() as tmp_dir:
            run_dir = Path(tmp_dir) / "case4_u_seed1"
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)
            (run_dir / "checkpoint").mkdir(parents=True, exist_ok=True)
            (run_dir / "checkpoint" / "model_refine_step50.pt").write_bytes(b"fake")
            (run_dir / "payload.json").write_text(
                json.dumps(
                    {
                        "run_id": run_dir.name,
                        "feature_cols": ["wind_speed_10m_m_s", "load", "ghi_w_m2"],
                        "cfg": {"target_col": "delta_net_load_h6"},
                    }
                )
            )
            (run_dir / "artifacts" / "eval_pruned.json").write_text(json.dumps({"rmse": 10.0}))
            pd.DataFrame([{"y_true": 0.0, "y_pred": 10.0}]).to_parquet(run_dir / "artifacts" / "predictions_test.parquet", index=False)

            sys.modules["torch"] = fake_torch
            try:
                feature_map = module.load_feature_map(run_dir, module.read_payload(run_dir))
            finally:
                if original_torch is None:
                    sys.modules.pop("torch", None)
                else:
                    sys.modules["torch"] = original_torch

        self.assertEqual(feature_map["wind_speed_10m_m_s"], 1)
        self.assertEqual(feature_map["ghi_w_m2"], 2)
        self.assertEqual(feature_map["temp_2m_c"], 0)


if __name__ == "__main__":
    unittest.main()
