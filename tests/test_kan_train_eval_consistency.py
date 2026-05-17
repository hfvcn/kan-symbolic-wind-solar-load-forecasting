import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestKanTrainEvalConsistency(unittest.TestCase):
    def test_local_finalize_calls_post_refine_eval_helper(self) -> None:
        path = Path("src/local/kan_train_job.py")
        source = path.read_text()
        tree = ast.parse(source)
        finalize = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_finalize")
        calls = [node.func.id for node in ast.walk(finalize) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        self.assertIn("_write_final_pruned_eval", calls)
        self.assertNotIn('"eval_pruned": best.eval_val', source)
        self.assertIn("mark_payload_completed", calls)

    def test_modal_helper_writes_final_eval(self) -> None:
        from modal_jobs.kan_train import _write_final_pruned_eval

        with tempfile.TemporaryDirectory() as d:
            artifacts_dir = Path(d)
            final_eval = {"rmse": 2.0, "mae": 1.0, "r2": 0.8}
            with patch("modal_jobs.kan_train._evaluate", return_value=final_eval):
                result = _write_final_pruned_eval(
                    artifacts_dir=artifacts_dir,
                    model=object(),
                    dataset={"test_input": object(), "test_label": object()},
                    target_scaler=None,
                )

            self.assertEqual(result, final_eval)
            saved = json.loads((artifacts_dir / "eval_pruned.json").read_text())
            self.assertEqual(saved, final_eval)
            saved_explicit = json.loads((artifacts_dir / "eval_val.json").read_text())
            self.assertEqual(saved_explicit, final_eval)

    def test_completion_helper_sets_status_and_finished_at(self) -> None:
        from src.local.run_contract import mark_payload_completed

        payload = {"run_id": "run_x", "status": "running", "started_at": "2026-04-18T00:00:00+00:00"}
        results = {"eval_pruned": {"rmse": 1.23}, "eval_test": {"rmse": 2.34}}

        completed = mark_payload_completed(payload, results=results, finished_at="2026-04-18T00:01:00+00:00")

        self.assertEqual(payload["status"], "running")
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["finished_at"], "2026-04-18T00:01:00+00:00")
        self.assertEqual(completed["completed_at"], "2026-04-18T00:01:00+00:00")
        self.assertEqual(completed["eval_pruned"], results["eval_pruned"])
        self.assertEqual(completed["eval_test"], results["eval_test"])
        self.assertEqual(completed["results"], results)

    def test_modal_returns_post_refine_eval_payload_contract(self) -> None:
        source = Path("modal_jobs/kan_train.py").read_text()
        self.assertIn("mark_payload_completed(", source)
        self.assertNotIn('"eval_pruned": best["eval_val"]', source)
        self.assertIn('"eval_test"', source)
        self.assertIn("eval_val.json", source)
        self.assertIn("prune_candidate_profile", source)
        self.assertIn("scale_features", source)
        self.assertIn('"feature_scaler"', source)


if __name__ == "__main__":
    unittest.main()
