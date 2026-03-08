import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.eval.paired_significance import PairedTestConfig, compare_predictions, load_run_predictions


def _write_run(run_dir: Path, *, run_id: str, target_col: str, y_true, y_pred, reconstructed: bool = True) -> None:
    artifacts = run_dir / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    payload = {"run_id": run_id, "phase": "02-kan-training", "cfg": {"target_col": target_col}}
    (run_dir / "payload.json").write_text(json.dumps(payload))
    path = artifacts / ("predictions_test_reconstructed.parquet" if reconstructed else "predictions_test.parquet")
    pd.DataFrame({"y_true": y_true, "y_pred": y_pred}).to_parquet(path, compression="snappy")


class TestPairedSignificance(unittest.TestCase):
    def test_compare_predictions_prefers_reconstructed_and_reports_positive_diff(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            y_true = list(range(40))
            ref_dir = base / "runs" / "ref"
            cmp_dir = base / "runs" / "cmp"

            _write_run(ref_dir, run_id="ref", target_col="delta_load_h6", y_true=y_true, y_pred=y_true)
            _write_run(cmp_dir, run_id="cmp", target_col="delta_load_h6", y_true=y_true, y_pred=[x + 2 for x in y_true])

            result = compare_predictions(
                load_run_predictions(ref_dir),
                load_run_predictions(cmp_dir),
                config=PairedTestConfig(metric="absolute_error", bootstrap_samples=300, permutation_samples=300, random_seed=11),
            )

            self.assertEqual(result.n, 40)
            self.assertAlmostEqual(result.reference_mean_error, 0.0, places=12)
            self.assertAlmostEqual(result.compare_mean_error, 2.0, places=12)
            self.assertAlmostEqual(result.mean_diff, 2.0, places=12)
            self.assertAlmostEqual(result.median_diff, 2.0, places=12)
            self.assertAlmostEqual(result.win_rate, 1.0, places=12)
            self.assertAlmostEqual(result.tie_rate, 0.0, places=12)
            self.assertGreater(result.ci95_low, 0.0)
            self.assertLess(result.permutation_pvalue, 0.05)

    def test_compare_predictions_rejects_mismatched_truth(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            ref_dir = base / "runs" / "ref"
            cmp_dir = base / "runs" / "cmp"

            _write_run(ref_dir, run_id="ref", target_col="delta_load_h6", y_true=[0, 1, 2], y_pred=[0, 1, 2])
            _write_run(cmp_dir, run_id="cmp", target_col="delta_load_h6", y_true=[0, 1, 3], y_pred=[0, 1, 3])

            with self.assertRaisesRegex(ValueError, "y_true mismatch"):
                compare_predictions(
                    load_run_predictions(ref_dir),
                    load_run_predictions(cmp_dir),
                    config=PairedTestConfig(metric="absolute_error", bootstrap_samples=50, permutation_samples=50),
                )

    def test_cli_compares_reference_against_multiple_runs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "paired_significance.py"

        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            ref_dir = base / "runs" / "ref"
            cmp_a_dir = base / "runs" / "cmp_a"
            cmp_b_dir = base / "runs" / "cmp_b"
            out_path = base / "paired.csv"
            y_true = list(range(12))

            _write_run(ref_dir, run_id="ref", target_col="delta_net_load_h6", y_true=y_true, y_pred=y_true)
            _write_run(cmp_a_dir, run_id="cmp_a", target_col="delta_net_load_h6", y_true=y_true, y_pred=[x + 1 for x in y_true])
            _write_run(cmp_b_dir, run_id="cmp_b", target_col="delta_net_load_h6", y_true=y_true, y_pred=[x + 3 for x in y_true])

            subprocess.run(
                [
                    "python3",
                    str(script),
                    "--reference-run",
                    str(ref_dir),
                    "--compare-run",
                    str(cmp_a_dir),
                    "--compare-run",
                    str(cmp_b_dir),
                    "--bootstrap-samples",
                    "80",
                    "--permutation-samples",
                    "80",
                    "--out",
                    str(out_path),
                ],
                check=True,
                cwd=str(repo_root),
            )

            out_df = pd.read_csv(out_path)
            self.assertEqual(set(out_df["metric"]), {"absolute_error", "squared_error"})
            self.assertEqual(set(out_df["compare_run_id"]), {"cmp_a", "cmp_b"})
            self.assertTrue((out_df["mean_diff"] > 0).all())


if __name__ == "__main__":
    unittest.main()
