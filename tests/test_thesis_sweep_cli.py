import argparse
import unittest


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


if __name__ == "__main__":
    unittest.main()
