import argparse
import unittest
from pathlib import Path


class TestThesisSweepCli(unittest.TestCase):
    def _make_args(self, **overrides):
        base = {
            "source_data_run_id": "source_run",
            "source_timestamp": "2026-03-06_041853",
            "derived_data_run_id": "",
            "horizons": "6",
            "execute": False,
            "dry_run": True,
            "detached_remote": False,
            "no_auto_sync": True,
            "use_gpu": False,
            "kan_hidden_width": "10",
            "kan_hidden_layers": "",
            "no_warmup_update_grid": True,
            "no_symbolic": True,
            "sweeps": "s1",
            "symbolic_train_run_id": [],
            "symbolic_grid_mode": "auto_reduced",
            "baseline_protocols": "matched,best_effort",
            "baseline_models": "mlp,lstm",
            "rolling_origin_index": -1,
            "rolling_origin_step_steps": 0,
            "session_id": "",
            "sparsify_lamb": None,
            "sparsify_lamb_entropy": None,
        }
        base.update(overrides)
        return argparse.Namespace(**base)

    def test_downstream_commands_drop_source_timestamp_when_using_existing_derived_run(self) -> None:
        from src.thesis_sweep.cli import build_plan

        args = self._make_args(derived_data_run_id="derived_run")
        _manifest, planned, _run_ids, _comp_runs = build_plan(args, session_id="paperref", detached=False)

        self.assertGreaterEqual(len(planned), 1)
        self.assertTrue(all("--data-timestamp" not in cmd.cmd for cmd in planned))

    def test_downstream_commands_drop_source_timestamp_after_new_derive(self) -> None:
        from src.thesis_sweep.cli import build_plan

        args = self._make_args(derived_data_run_id="", sweeps="s1,s3")
        _manifest, planned, _run_ids, _comp_runs = build_plan(args, session_id="paperref", detached=False)

        derive_cmd = planned[0].cmd
        kan_cmds = [p.cmd for p in planned[1:]]

        self.assertIn("--source-timestamp", derive_cmd)
        self.assertTrue(kan_cmds)
        self.assertTrue(all("--data-timestamp" not in cmd for cmd in kan_cmds))

    def test_plan_s2b_uses_canonical_no_base_direct_pairs(self) -> None:
        from src.thesis_sweep.plan_kan import plan_s2b

        args = self._make_args(sweeps="s2b")
        planned, _mapping = plan_s2b(args, session_id="paperref", detached=False, derived_id="derived_run")

        direct_unblocked = [p for p in planned if "s2b_direct_unblocked_seed" in p.run_id]
        direct_blocked = [p for p in planned if "s2b_direct_blocked_seed" in p.run_id]

        self.assertEqual(len(direct_unblocked), 5)
        self.assertEqual(len(direct_blocked), 5)

        sample_unblocked = " ".join(direct_unblocked[0].cmd)
        sample_blocked = " ".join(direct_blocked[0].cmd)

        self.assertIn("--target delta_net_load_h6", sample_unblocked)
        self.assertIn("--no-include-base", sample_unblocked)
        self.assertIn("--no-warmup-update-grid", sample_unblocked)
        self.assertIn("--lag-series load,wind,solar", sample_unblocked)

        self.assertIn("--target delta_net_load_h6", sample_blocked)
        self.assertIn("--no-include-base", sample_blocked)
        self.assertIn("--no-warmup-update-grid", sample_blocked)
        self.assertIn("--lag-series load", sample_blocked)
        self.assertNotIn("--lag-series load,wind,solar", sample_blocked)

    def test_plan_s2c_uses_full_lag_blocking_direct_runs(self) -> None:
        from src.thesis_sweep.plan_kan import plan_s2c

        args = self._make_args(sweeps="s2c")
        planned, _mapping = plan_s2c(args, session_id="paperref", detached=False, derived_id="derived_run")

        direct_fully_blocked = [p for p in planned if "s2c_direct_fully_blocked_seed" in p.run_id]

        self.assertEqual(len(direct_fully_blocked), 5)

        sample_blocked = " ".join(direct_fully_blocked[0].cmd)
        self.assertIn("--target delta_net_load_h6", sample_blocked)
        self.assertIn("--no-include-base", sample_blocked)
        self.assertIn("--no-warmup-update-grid", sample_blocked)
        self.assertIn("--lag-series none", sample_blocked)
        self.assertIn("--lag-steps none", sample_blocked)

    def test_plan_s1_forces_no_warmup_grid_update(self) -> None:
        from src.thesis_sweep.plan_kan import plan_s1

        args = self._make_args(sweeps="s1", no_warmup_update_grid=False)
        planned, _mapping = plan_s1(args, session_id="paperref", detached=False, derived_id="derived_run")

        self.assertEqual(len(planned), 1)
        sample = " ".join(planned[0].cmd)
        self.assertIn("--target delta_net_load_h6", sample)
        self.assertIn("--no-warmup-update-grid", sample)

    def test_plan_s3_uses_thesis_26_feature_profile(self) -> None:
        from src.thesis_sweep.plan_kan import plan_s3

        args = self._make_args(sweeps="s3")
        planned, _mapping, _comp_runs = plan_s3(args, session_id="paperref", detached=False, derived_id="derived_run")

        self.assertEqual(len(planned), 3)
        for cmd in planned:
            sample = " ".join(cmd.cmd)
            self.assertIn("--feature-profile thesis_26", sample)
            self.assertIn("--no-include-base", sample)

    def test_derive_command_passes_rolling_origin_args(self) -> None:
        from src.thesis_sweep.plan_derive import plan_derive_dataset

        args = self._make_args(
            sweeps="s1",
            derived_data_run_id="",
            rolling_origin_index=2,
            rolling_origin_step_steps=96,
        )
        planned, _run_ids, derived_id = plan_derive_dataset(args, session_id="paperref", detached=False)

        self.assertEqual(len(planned), 1)
        cmd = " ".join(planned[0].cmd)
        self.assertIn("--rolling-origin-index 2", cmd)
        self.assertIn("--rolling-origin-step-steps 96", cmd)
        self.assertIn("derived_h1_6_ro02", derived_id)

    def test_cli_module_has_script_entrypoint(self) -> None:
        source = Path("src/thesis_sweep/cli.py").read_text(encoding="utf-8")
        self.assertIn('if __name__ == "__main__":', source)
        self.assertIn("main()", source)

    def test_build_plan_emits_lstm_baseline_runs_by_default(self) -> None:
        from src.thesis_sweep.cli import build_plan

        args = self._make_args(derived_data_run_id="derived_run", sweeps="s1")
        manifest, _planned, _run_ids, _comp_runs = build_plan(args, session_id="paperref", detached=False)

        baseline_runs = manifest["runs"]["baselines"]
        self.assertTrue(any("baseline_torch_lstm_matched" in run_id for run_id in baseline_runs))
        self.assertTrue(any("baseline_torch_mlp_matched" in run_id for run_id in baseline_runs))


if __name__ == "__main__":
    unittest.main()
