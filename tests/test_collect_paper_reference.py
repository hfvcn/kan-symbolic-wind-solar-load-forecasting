import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestCollectPaperReference(unittest.TestCase):
    def test_collects_manifest_session_assets_and_run_refs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "collect_paper_reference.py"

        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            session_id = "paperref_test"
            session_dir = base / "doc" / "thesis_sweeps" / session_id
            run_dir = base / "runs" / "run_a"
            out_dir = base / "bundle"

            (session_dir / "paper_assets").mkdir(parents=True, exist_ok=True)
            (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

            (session_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "session_id": session_id,
                        "source_data_run_id": "run_a",
                        "derived_data_run_id": "run_a",
                        "runs": {"kan_train": ["run_a"], "baselines": [], "symbolic": []},
                        "structured_components": {},
                    }
                )
            )
            (session_dir / "paper_assets" / "comparison_table.csv").write_text("x,y\n1,2\n")
            (session_dir / "resume_after_timeout.json").write_text("{\"status\": \"saved\"}\n")
            (run_dir / "payload.json").write_text(json.dumps({"run_id": "run_a", "phase": "02-kan-training", "kind": "kan"}))
            (run_dir / "artifacts" / "eval_test.json").write_text(json.dumps({"rmse": 1.0}))
            (base / "doc" / "paper_assets").mkdir(parents=True, exist_ok=True)
            (base / "doc" / "paper_assets" / "ASSET_INDEX.md").write_text("# idx\n")
            (base / "doc" / "paper_assets" / "comparison_table.csv").write_text("run,rmse\nrun_a,1.0\n")
            (base / "doc" / "paper_delivery_closure_20260306.md").write_text("# closure\n")

            subprocess.run(
                ["python3", str(script), "--session-id", session_id, "--out-dir", str(out_dir), "--repo-root", str(base)],
                check=True,
                cwd=str(base),
            )

            self.assertTrue((out_dir / "manifest.json").exists())
            self.assertTrue((out_dir / "paper_assets" / "comparison_table.csv").exists())
            self.assertTrue((out_dir / "run_refs" / "run_a" / "payload.json").exists())
            self.assertTrue((out_dir / "run_refs" / "run_a" / "artifacts" / "eval_test.json").exists())
            self.assertTrue((out_dir / "paper_assets_snapshot" / "comparison_table.csv").exists())
            self.assertTrue((out_dir / "doc_snapshot" / "paper_delivery_closure_20260306.md").exists())
            self.assertTrue((out_dir / "session_meta" / "resume_after_timeout.json").exists())
            self.assertIn("run_a", (out_dir / "README.md").read_text())


if __name__ == "__main__":
    unittest.main()
