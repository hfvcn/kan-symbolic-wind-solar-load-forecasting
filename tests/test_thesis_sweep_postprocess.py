from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.thesis_sweep.utils import det_run_id


class TestThesisSweepPostprocess(unittest.TestCase):
    def _write_run(
        self,
        runs_root: Path,
        run_id: str,
        *,
        payload: dict | None = None,
        formula_expr: str | None = None,
        formula_rmse: float | None = None,
        formula_val_rmse: float | None = None,
        reconstructed_rmse: float | None = None,
        eval_pruned_rmse: float | None = None,
    ) -> Path:
        run_dir = runs_root / run_id
        artifacts_dir = run_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        if payload is not None:
            (run_dir / "payload.json").write_text(json.dumps(payload))
        if formula_expr is not None:
            (artifacts_dir / "formula.sympy.txt").write_text(formula_expr)
        if formula_rmse is not None:
            (artifacts_dir / "formula_eval_test.json").write_text(json.dumps({"rmse": formula_rmse}))
        if formula_val_rmse is not None:
            (artifacts_dir / "formula_eval_val.json").write_text(json.dumps({"rmse": formula_val_rmse}))
        if reconstructed_rmse is not None:
            (artifacts_dir / "eval_test_reconstructed.json").write_text(json.dumps({"rmse": reconstructed_rmse}))
        if eval_pruned_rmse is not None:
            metrics = json.dumps({"rmse": eval_pruned_rmse})
            (artifacts_dir / "eval_pruned.json").write_text(metrics)
            (artifacts_dir / "eval_val.json").write_text(metrics)
        return run_dir

    def test_skips_combo_when_structured_components_are_incomplete(self) -> None:
        import src.thesis_sweep.postprocess as postprocess

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "runs").mkdir()
            (repo_root / "doc" / "paper_assets").mkdir(parents=True)
            self._write_run(
                repo_root / "runs",
                "wind_phys_train",
                payload={"run_id": "wind_phys_train"},
                eval_pruned_rmse=0.5,
            )

            with (
                mock.patch.object(postprocess, "REPO_ROOT", repo_root),
                mock.patch.object(postprocess, "local_py") as local_py,
                mock.patch.object(postprocess, "run_cmd") as run_cmd,
                mock.patch.object(postprocess, "sync_run") as sync_run,
            ):
                out = postprocess.local_postprocess(
                    run_ids=[],
                    comp_runs={"physics_wind": "wind_phys_train"},
                    session_id="demo",
                    session_dir=repo_root / "doc" / "thesis_sweeps" / "demo",
                )

            self.assertEqual(out, [])
            run_cmd.assert_not_called()
            sync_run.assert_not_called()
            self.assertTrue(local_py.called)

    def test_modal_combo_uses_resolved_formula_run_ids(self) -> None:
        import src.thesis_sweep.postprocess as postprocess

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            runs_root = repo_root / "runs"
            runs_root.mkdir()
            (repo_root / "doc" / "paper_assets").mkdir(parents=True)

            for run_id in ("load_pred", "wind_pred", "solar_pred", "wind_phys_train", "solar_phys_train"):
                reconstructed = {
                    "load_pred": 0.7,
                    "wind_pred": 0.8,
                    "solar_pred": 0.2,
                    "wind_phys_train": 0.3,
                    "solar_phys_train": 0.5,
                }[run_id]
                eval_pruned = {
                    "load_pred": 0.4,
                    "wind_pred": 0.2,
                    "solar_pred": 0.7,
                    "wind_phys_train": 0.9,
                    "solar_phys_train": 0.3,
                }[run_id]
                self._write_run(
                    runs_root,
                    run_id,
                    payload={"run_id": run_id},
                    reconstructed_rmse=reconstructed,
                    eval_pruned_rmse=eval_pruned,
                )

            self._write_run(
                runs_root,
                "load_formula_bad",
                payload={"run_id": "load_formula_bad", "train_run_id": "load_pred", "r2_threshold": 0.999},
                formula_expr="x",
                formula_rmse=1.2,
                formula_val_rmse=1.2,
            )
            self._write_run(
                runs_root,
                "load_formula_best",
                payload={"run_id": "load_formula_best", "train_run_id": "load_pred", "r2_threshold": 0.995},
                formula_expr="x + 1",
                formula_rmse=0.4,
                formula_val_rmse=0.4,
            )
            self._write_run(
                runs_root,
                "wind_formula_regular",
                payload={"run_id": "wind_formula_regular", "train_run_id": "wind_pred", "r2_threshold": 0.999},
                formula_expr="w",
                formula_rmse=0.8,
                formula_val_rmse=0.1,
            )
            self._write_run(
                runs_root,
                "wind_formula_physics",
                payload={"run_id": "wind_formula_physics", "train_run_id": "wind_phys_train", "r2_threshold": 0.995},
                formula_expr="w + 1",
                formula_rmse=0.3,
                formula_val_rmse=0.6,
            )
            self._write_run(
                runs_root,
                "solar_formula_physics",
                payload={"run_id": "solar_formula_physics", "train_run_id": "solar_phys_train", "r2_threshold": 0.999},
                formula_expr="s",
                formula_rmse=0.2,
                formula_val_rmse=0.2,
            )
            self._write_run(
                runs_root,
                "solar_formula_regular",
                payload={"run_id": "solar_formula_regular", "train_run_id": "solar_pred", "r2_threshold": 0.995},
                formula_expr="s + 1",
                formula_rmse=0.1,
                formula_val_rmse=0.7,
            )

            comp_runs = {
                "load": "load_pred",
                "wind": "wind_pred",
                "solar": "solar_pred",
                "physics_wind": "wind_phys_train",
                "physics_solar": "solar_phys_train",
            }

            with (
                mock.patch.object(postprocess, "REPO_ROOT", repo_root),
                mock.patch.object(postprocess, "local_py") as local_py,
                mock.patch.object(postprocess, "run_cmd") as run_cmd,
                mock.patch.object(postprocess, "sync_run") as sync_run,
            ):
                out = postprocess.local_postprocess(
                    run_ids=["load_pred", "wind_pred", "solar_pred"],
                    comp_runs=comp_runs,
                    session_id="paperref",
                    session_dir=repo_root / "doc" / "thesis_sweeps" / "paperref",
                )

            combo_id = det_run_id("paperref", "s3_combo_net_load")
            cmd = run_cmd.call_args.args[0]

            self.assertIn(combo_id, out)
            self.assertIn("--wind-run-id", cmd)
            self.assertIn("wind_pred", cmd)
            self.assertIn("--solar-run-id", cmd)
            self.assertIn("solar_phys_train", cmd)
            self.assertIn("--load-formula-run-id", cmd)
            self.assertIn("load_formula_best", cmd)
            self.assertIn("--wind-formula-run-id", cmd)
            self.assertIn("wind_formula_regular", cmd)
            self.assertIn("--solar-formula-run-id", cmd)
            self.assertIn("solar_formula_physics", cmd)
            sync_run.assert_called_once_with(combo_id, dry_run=False)
            self.assertTrue(local_py.called)


if __name__ == "__main__":
    unittest.main()
