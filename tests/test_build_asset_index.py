import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import pandas as pd


class TestBuildAssetIndex(unittest.TestCase):
    def test_includes_cross_validation_report_and_seeded_kind(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "build_asset_index.py"

        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            runs_dir = base / "runs"
            paper_dir = base / "doc" / "paper_assets"
            figures_dir = paper_dir / "figures"
            out_path = paper_dir / "ASSET_INDEX.md"

            run_id = "2026-02-26_000000_deadbeef"
            run_dir = runs_dir / run_id
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)

            payload = {
                "run_id": run_id,
                "phase": "04-baselines-pysr",
                "seed_from_symbolic_run": "sym_1",
            }
            (run_dir / "payload.json").write_text(json.dumps(payload))
            (artifacts / "eval_test.json").write_text(json.dumps({"rmse": 1.0, "mae": 1.0, "r2": 0.0}))
            pd.DataFrame([{"complexity": 3, "loss": 1.0, "equation": "x0"}]).to_csv(artifacts / "equations.csv", index=False)

            # Global cross-validation report
            paper_dir.mkdir(parents=True, exist_ok=True)
            cv = paper_dir / f"kan_pysr_cross_validation_{run_id}.md"
            cv.write_text("# dummy\n")

            figures_dir.mkdir(parents=True, exist_ok=True)

            subprocess.run(
                [
                    "python3",
                    str(script),
                    "--runs-dir",
                    str(runs_dir),
                    "--paper-assets-dir",
                    str(paper_dir),
                    "--figures-dir",
                    str(figures_dir),
                    "--out",
                    str(out_path),
                ],
                check=True,
                cwd=str(repo_root),
            )

            text = out_path.read_text()
            self.assertIn(f"kan_pysr_cross_validation_{run_id}.md", text)
            self.assertIn("kind: `pysr_seeded`", text)


if __name__ == "__main__":
    unittest.main()

