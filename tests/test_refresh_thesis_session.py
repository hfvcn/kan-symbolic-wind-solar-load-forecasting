from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def _write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))


class TestRefreshThesisSession(unittest.TestCase):
    def test_resolve_refresh_inputs_merges_target_and_extra_sessions(self) -> None:
        from src.thesis_sweep.refresh_session import resolve_refresh_inputs

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _write_manifest(
                repo_root / "doc" / "thesis_sweeps" / "paperref" / "manifest.json",
                {
                    "session_id": "paperref",
                    "planned": [
                        {"run_id": "paper_train"},
                        {"run_id": "paper_symbolic"},
                    ],
                    "runs": {
                        "kan_train": ["paper_train"],
                        "symbolic": ["paper_symbolic"],
                    },
                    "structured_components": {"load": "paper_load", "wind": "paper_wind"},
                },
            )
            _write_manifest(
                repo_root / "doc" / "thesis_sweeps" / "symbolic_refresh" / "manifest.json",
                {
                    "session_id": "symbolic_refresh",
                    "planned": [
                        {"run_id": "refresh_formula_1"},
                        {"run_id": "refresh_formula_2"},
                    ],
                    "runs": {"symbolic": ["refresh_formula_1", "refresh_formula_2"]},
                },
            )

            inputs = resolve_refresh_inputs(
                repo_root=repo_root,
                session_id="paperref",
                sync_from_sessions=["symbolic_refresh"],
                extra_run_ids=["manual_formula", "paper_symbolic"],
            )

        self.assertEqual(inputs.session_id, "paperref")
        self.assertEqual(inputs.comp_runs, {"load": "paper_load", "wind": "paper_wind"})
        self.assertEqual(
            inputs.run_ids,
            (
                "paper_train",
                "paper_symbolic",
                "refresh_formula_1",
                "refresh_formula_2",
                "manual_formula",
            ),
        )
        self.assertEqual(inputs.sync_run_ids, ("refresh_formula_1", "refresh_formula_2", "manual_formula", "paper_symbolic"))

    def test_refresh_session_syncs_then_collects_reference(self) -> None:
        from src.thesis_sweep.refresh_session import RefreshSessionInputs, refresh_session

        inputs = RefreshSessionInputs(
            session_id="paperref",
            session_dir=Path("/tmp/paperref"),
            run_ids=("paper_train", "refresh_formula"),
            sync_run_ids=("refresh_formula",),
            comp_runs={"load": "paper_load"},
        )

        with (
            mock.patch("src.thesis_sweep.refresh_session.sync_run") as sync_run,
            mock.patch("src.thesis_sweep.refresh_session.local_postprocess", return_value=["paper_train", "combo"]) as local_postprocess,
            mock.patch("src.thesis_sweep.refresh_session.local_py") as local_py,
        ):
            out = refresh_session(inputs, repo_root=Path("/repo"), collect_paper_reference=True)

        self.assertEqual(out, ["paper_train", "combo"])
        sync_run.assert_called_once_with("refresh_formula", dry_run=False)
        local_postprocess.assert_called_once_with(
            run_ids=["paper_train", "refresh_formula"],
            comp_runs={"load": "paper_load"},
            session_id="paperref",
            session_dir=Path("/tmp/paperref"),
        )
        local_py.assert_called_once_with(
            Path("/repo") / "scripts" / "collect_paper_reference.py",
            ["--session-id", "paperref"],
            dry_run=False,
        )


if __name__ == "__main__":
    unittest.main()
