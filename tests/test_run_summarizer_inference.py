import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd


class TestRunSummarizerInference(unittest.TestCase):
    def test_phase2_kan_prefers_predictions_test_metrics(self) -> None:
        from src.eval.runs import summarize_run

        with tempfile.TemporaryDirectory() as d:
            run_dir = Path(d) / "runs" / "kan_train"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)

            payload = {"run_id": "kan_train", "phase": "02-kan-training", "kind": "kan"}
            (run_dir / "payload.json").write_text(json.dumps(payload))

            # If present, eval_pruned.json corresponds to VAL (KAN.fit's test_* fields).
            # For thesis tables we prefer TEST metrics computed from predictions_test.parquet.
            (artifacts / "eval_pruned.json").write_text(json.dumps({"rmse": 999.0, "mae": 999.0, "r2": -1.0}))

            pd.DataFrame({"y_true": [0.0, 0.0], "y_pred": [1.0, 1.0], "residual": [1.0, 1.0]}).to_parquet(
                artifacts / "predictions_test.parquet",
                compression="snappy",
            )

            s = summarize_run(run_dir)
            self.assertEqual(s.phase, "02-kan-training")
            self.assertEqual(s.kind, "kan")
            self.assertAlmostEqual(float(s.rmse or 0.0), 1.0, places=6)

    def test_symbolic_phase_inferred_when_payload_phase_is_null(self) -> None:
        from src.eval.runs import summarize_run

        with tempfile.TemporaryDirectory() as d:
            run_dir = Path(d) / "runs" / "sym_run"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)

            # payload.phase can be null for older runs; summarizer should still infer Phase 03
            payload = {"run_id": "sym_run", "phase": None, "train_run_id": "train_1"}
            (run_dir / "payload.json").write_text(json.dumps(payload))

            (artifacts / "formula_eval_test.json").write_text(json.dumps({"rmse": 1.0, "mae": 1.0, "r2": 0.0}))

            s = summarize_run(run_dir)
            self.assertEqual(s.phase, "03-symbolic-extraction")
            self.assertEqual(s.kind, "kan_symbolic")

    def test_pysr_seeded_kind_when_seed_from_symbolic_run_present(self) -> None:
        from src.eval.runs import summarize_run

        with tempfile.TemporaryDirectory() as d:
            run_dir = Path(d) / "runs" / "pysr_seeded"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)

            payload = {
                "run_id": "pysr_seeded",
                "phase": "04-baselines-pysr",
                "seed_from_symbolic_run": "sym_1",
            }
            (run_dir / "payload.json").write_text(json.dumps(payload))
            (artifacts / "eval_test.json").write_text(json.dumps({"rmse": 1.0, "mae": 1.0, "r2": 0.0}))

            pd.DataFrame([{"complexity": 3, "loss": 1.0, "equation": "x0"}]).to_csv(artifacts / "equations.csv", index=False)

            s = summarize_run(run_dir)
            self.assertEqual(s.phase, "04-baselines-pysr")
            self.assertEqual(s.kind, "pysr_seeded")


if __name__ == "__main__":
    unittest.main()
