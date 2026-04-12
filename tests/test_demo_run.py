from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


def _load_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "src" / "demo_quick_train_support.py"
    spec = importlib.util.spec_from_file_location("demo_run", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


demo_run = _load_module()


def _load_midterm_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "src" / "demo_midterm_support.py"
    spec = importlib.util.spec_from_file_location("demo_midterm_support", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


demo_midterm = _load_midterm_module()


class DemoRunScriptTests(unittest.TestCase):
    def test_sanitize_text_hides_remote_terms(self) -> None:
        volume_name = "artifact-store-real"
        raw = " ".join(
            [
                demo_run.remote_cli(),
                "run",
                str(demo_run.remote_job_dir() / "kan_train.py"),
                volume_name,
                demo_run.sync_script().name,
                "/vol/runs/demo_id",
                "KAN_SR_VOLUME",
                "VOLUME_NAME",
            ]
        )

        sanitized = demo_run.sanitize_text(raw, volume_name)

        self.assertNotIn(demo_run.remote_cli(), sanitized)
        self.assertNotIn(demo_run.remote_job_dir().name, sanitized)
        self.assertNotIn(demo_run.sync_script().name, sanitized)
        self.assertNotIn(volume_name, sanitized)
        self.assertNotIn("/vol", sanitized)
        self.assertIn("cloud", sanitized)
        self.assertIn("remote_jobs", sanitized)
        self.assertIn("artifact_sync.sh", sanitized)
        self.assertIn("artifact-store", sanitized)

    def test_find_latest_training_run_uses_most_recent_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            self._write_payload(runs_root, "2026-04-10_010101_old", {"run_id": "2026-04-10_010101_old", "phase": "02-kan-training"})
            self._write_payload(runs_root, "2026-04-11_020202_new", {"run_id": "2026-04-11_020202_new", "phase": "02-kan-training"})
            self._write_payload(runs_root, "2026-04-12_030303_skip", {"run_id": "2026-04-12_030303_skip", "phase": "04-baselines-torch"})

            latest = demo_run.find_latest_training_run(runs_root)

            self.assertEqual("2026-04-11_020202_new", latest)

    def test_template_from_run_extracts_training_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            run_id = "train_template"
            self._write_payload(
                runs_root,
                run_id,
                {
                    "run_id": run_id,
                    "phase": "02-kan-training",
                    "data_run_id": "data_001",
                    "data_timestamp": "2026-04-12_000001",
                    "include_groups": ["g1", "g2"],
                    "lag_series": ["load"],
                    "lag_steps": [1, 12],
                    "cfg": {"target_col": "solar_h6"},
                },
            )

            template = demo_run.template_from_run(runs_root, run_id)

            self.assertEqual("data_001", template.data_run_id)
            self.assertEqual("solar_h6", template.target_col)
            self.assertEqual(("g1", "g2"), template.include_groups)
            self.assertEqual((1, 12), template.lag_steps)

    def test_load_summary_writes_local_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            run_id = "demo_train_20260412_abcdef12"
            run_dir = runs_root / run_id
            (run_dir / "artifacts").mkdir(parents=True)
            (run_dir / "checkpoint").mkdir(parents=True)
            (run_dir / "payload.json").write_text(
                json.dumps(
                    {
                        "run_id": run_id,
                        "data_run_id": "data_001",
                        "cfg": {"target_col": "load"},
                        "results": {"eval_pruned": {"rmse": 1.23}},
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "checkpoint" / "model.pt").write_text("ckpt", encoding="utf-8")
            (run_dir / "metrics.csv").write_text("ts,stage\n", encoding="utf-8")
            (run_dir / "artifacts" / "predictions_test.parquet").write_text("PAR1", encoding="utf-8")

            config = demo_run.DemoConfig(
                runs_root=runs_root,
                template=demo_run.TemplateRun(
                    run_id="source_train",
                    data_run_id="data_001",
                    data_timestamp="",
                    target_col="load",
                    include_groups=(),
                    lag_series=(),
                    lag_steps=(),
                ),
                run_id=run_id,
                volume_name="hidden-store",
                max_train_rows=demo_run.DEFAULT_MAX_TRAIN_ROWS,
                warmup_steps=demo_run.DEFAULT_WARMUP_STEPS,
                sparsify_steps=demo_run.DEFAULT_SPARSIFY_STEPS,
                refine_steps=demo_run.DEFAULT_REFINE_STEPS,
                hidden_width=demo_run.DEFAULT_HIDDEN_WIDTH,
                use_gpu=False,
                dry_run=False,
            )

            summary = demo_run.load_summary(config)

            self.assertEqual("load", summary["target_col"])
            self.assertEqual("source_train", summary["source_train_run_id"])
            self.assertTrue((run_dir / demo_run.SUMMARY_PATH).exists())

    def test_resolve_symbolic_run_prefers_matching_train_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            self._write_symbolic_run(runs_root, "sym_by_target", train_run_id="other_train", target_col="solar_h6")
            self._write_symbolic_run(runs_root, "sym_exact", train_run_id="template_train", target_col="solar_h6")

            resolved = demo_midterm.resolve_symbolic_run(
                runs_root,
                explicit_run_id="",
                template_train_run_id="template_train",
                target_col="solar_h6",
            )

            self.assertEqual("sym_exact", resolved)

    def test_load_symbolic_summary_reads_formula_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            self._write_symbolic_run(runs_root, "sym_run", train_run_id="template_train", target_col="solar_h6")

            summary = demo_midterm.load_symbolic_summary(runs_root, "sym_run")

            self.assertEqual("sym_run", summary["run_id"])
            self.assertEqual("solar_h6", summary["target_col"])
            self.assertIn("ghi", summary["formula_preview"])

    def test_infer_data_run_id_from_training_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            self._write_payload(
                runs_root,
                "template_train",
                {
                    "run_id": "template_train",
                    "phase": "02-kan-training",
                    "data_run_id": "data_001",
                    "cfg": {"target_col": "solar_h6"},
                },
            )

            data_run_id = demo_midterm.infer_data_run_id_from_training_payload(runs_root, "template_train")

            self.assertEqual("data_001", data_run_id)

    @staticmethod
    def _write_payload(runs_root: Path, run_id: str, payload: dict[str, str]) -> None:
        run_dir = runs_root / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "payload.json").write_text(json.dumps(payload), encoding="utf-8")

    @staticmethod
    def _write_symbolic_run(runs_root: Path, run_id: str, *, train_run_id: str, target_col: str) -> None:
        run_dir = runs_root / run_id
        artifacts_dir = run_dir / "artifacts"
        artifacts_dir.mkdir(parents=True)
        (run_dir / "payload.json").write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "status": "completed",
                    "train_run_id": train_run_id,
                    "target_col": target_col,
                }
            ),
            encoding="utf-8",
        )
        (artifacts_dir / "formula.sympy.txt").write_text("ghi + temp", encoding="utf-8")
        (artifacts_dir / "formula_metrics.json").write_text(json.dumps({"node_count": 3}), encoding="utf-8")
        (artifacts_dir / "formula_eval_test.json").write_text(json.dumps({"rmse": 1.0}), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
