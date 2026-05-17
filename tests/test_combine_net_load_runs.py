import json
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

import pandas as pd


class TestCombineNetLoadRuns(unittest.TestCase):
    def _write_run(
        self,
        *,
        base: Path,
        run_id: str,
        target_col: str,
        rows: list[dict[str, float]],
        reconstructed: bool,
        formula_expr: str | None = None,
        node_count: int | None = None,
    ) -> Path:
        run_dir = base / "runs" / run_id
        artifacts = run_dir / "artifacts"
        artifacts.mkdir(parents=True, exist_ok=True)
        (run_dir / "payload.json").write_text(json.dumps({"run_id": run_id, "target_col": target_col}))
        file_name = "predictions_test_reconstructed.parquet" if reconstructed else "predictions_test.parquet"
        pd.DataFrame(rows).to_parquet(artifacts / file_name, compression="snappy")
        if formula_expr is not None:
            (artifacts / "formula_reconstructed.sympy.txt").write_text(formula_expr)
            (artifacts / "formula_metrics.json").write_text(json.dumps({"node_count": node_count or 1}))
        return run_dir

    def test_generates_predictor_and_formula_artifacts(self) -> None:
        if importlib.util.find_spec("sympy") is None:
            self.skipTest("sympy not installed in current python3 environment")
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "combine_net_load_runs.py"

        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            rows_load = [{"y_true": 10.0, "y_pred": 9.0}, {"y_true": 12.0, "y_pred": 11.0}, {"y_true": 14.0, "y_pred": 13.0}]
            rows_wind = [{"y_true": 1.0, "y_pred": 1.5}, {"y_true": 2.0, "y_pred": 1.0}, {"y_true": 3.0, "y_pred": 2.0}]
            rows_solar = [{"y_true": 0.0, "y_pred": 0.0}, {"y_true": 1.0, "y_pred": 2.0}, {"y_true": 0.0, "y_pred": 0.0}]
            load_run = self._write_run(base=base, run_id="load_pred", target_col="delta_load_h2", rows=rows_load, reconstructed=True)
            wind_run = self._write_run(base=base, run_id="wind_pred", target_col="delta_wind_h2", rows=rows_wind, reconstructed=True)
            solar_run = self._write_run(base=base, run_id="solar_pred", target_col="delta_solar_h2", rows=rows_solar, reconstructed=True)

            load_formula = self._write_run(
                base=base,
                run_id="load_formula",
                target_col="delta_load_h2",
                rows=[{"y_true": 10.0, "y_pred": 10.0}, {"y_true": 12.0, "y_pred": 12.0}, {"y_true": 14.0, "y_pred": 14.0}],
                reconstructed=True,
                formula_expr="load_lag_2 + temp_2m_c",
                node_count=10,
            )
            wind_formula = self._write_run(
                base=base,
                run_id="wind_formula",
                target_col="delta_wind_h2",
                rows=[{"y_true": 1.0, "y_pred": 1.0}, {"y_true": 2.0, "y_pred": 2.0}, {"y_true": 3.0, "y_pred": 3.0}],
                reconstructed=True,
                formula_expr="wind_lag_2 + 1",
                node_count=20,
            )
            solar_formula = self._write_run(
                base=base,
                run_id="solar_formula",
                target_col="delta_solar_h2",
                rows=[{"y_true": 0.0, "y_pred": 0.0}, {"y_true": 1.0, "y_pred": 1.0}, {"y_true": 0.0, "y_pred": 0.0}],
                reconstructed=True,
                formula_expr="solar_lag_2",
                node_count=30,
            )

            subprocess.run(
                [
                    "python3",
                    str(script),
                    "--load-run",
                    str(load_run),
                    "--wind-run",
                    str(wind_run),
                    "--solar-run",
                    str(solar_run),
                    "--load-formula-run",
                    str(load_formula),
                    "--wind-formula-run",
                    str(wind_formula),
                    "--solar-formula-run",
                    str(solar_formula),
                    "--out-run-id",
                    "combo_run",
                    "--out-runs-dir",
                    str(base / "runs"),
                ],
                check=True,
                cwd=str(repo_root),
            )

            artifacts = base / "runs" / "combo_run" / "artifacts"
            self.assertTrue((artifacts / "predictions_test.parquet").exists())
            self.assertTrue((artifacts / "formula_combined.sympy.txt").exists())
            self.assertTrue((artifacts / "formula_combined.tex").exists())
            self.assertTrue((artifacts / "formula_combined_metrics.json").exists())
            self.assertTrue((artifacts / "formula_eval_test.json").exists())
            self.assertTrue((artifacts / "predictions_test_formula.parquet").exists())

            formula_eval = json.loads((artifacts / "formula_eval_test.json").read_text())
            self.assertAlmostEqual(float(formula_eval["rmse"]), 0.0, places=12)
            self.assertEqual(int(formula_eval["n"]), 3)

            formula_text = (artifacts / "formula_combined.sympy.txt").read_text()
            self.assertIn("load_lag_2", formula_text)
            self.assertIn("wind_lag_2", formula_text)
            self.assertIn("solar_lag_2", formula_text)

            payload = json.loads((base / "runs" / "combo_run" / "payload.json").read_text())
            self.assertEqual(payload["formula_component_runs"]["load"], "load_formula")
            self.assertEqual(payload["formula_component_targets"]["solar"], "delta_solar_h2")

    def test_rejects_partial_formula_run_args(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "combine_net_load_runs.py"

        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            rows = [{"y_true": 1.0, "y_pred": 1.0}, {"y_true": 2.0, "y_pred": 2.0}]
            load_run = self._write_run(base=base, run_id="load_pred", target_col="delta_load_h2", rows=rows, reconstructed=True)
            wind_run = self._write_run(base=base, run_id="wind_pred", target_col="delta_wind_h2", rows=rows, reconstructed=True)
            solar_run = self._write_run(base=base, run_id="solar_pred", target_col="delta_solar_h2", rows=rows, reconstructed=True)

            result = subprocess.run(
                [
                    "python3",
                    str(script),
                    "--load-run",
                    str(load_run),
                    "--wind-run",
                    str(wind_run),
                    "--solar-run",
                    str(solar_run),
                    "--load-formula-run",
                    str(load_run),
                    "--out-runs-dir",
                    str(base / "runs"),
                ],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Incomplete formula run set", result.stderr)


if __name__ == "__main__":
    unittest.main()
