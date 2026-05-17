import argparse
import unittest


class TestPlanSymbolic(unittest.TestCase):
    def _make_args(self, **overrides):
        base = {
            "no_symbolic": False,
            "sweeps": "s0,s3",
            "symbolic_train_run_id": [],
            "symbolic_grid_mode": "auto_reduced",
            "use_gpu": False,
        }
        base.update(overrides)
        return argparse.Namespace(**base)

    def test_auto_reduced_uses_full_grid_for_formula_focused_runs(self) -> None:
        from src.thesis_sweep.plan_symbolic import plan_symbolic

        args = self._make_args()
        planned, _run_ids, _train_ids = plan_symbolic(
            args,
            session_id="paperref",
            detached=False,
            kan_train_run_ids=[
                "s3_comp_load_delta_h6",
                "s0p_solar_delta_h6",
                "s1_delta_net_load_h6",
            ],
        )

        load_cmds = [p for p in planned if "s3_comp_load_delta_h6" in " ".join(p.cmd)]
        solar_cmds = [p for p in planned if "s0p_solar_delta_h6" in " ".join(p.cmd)]
        net_cmds = [p for p in planned if "s1_delta_net_load_h6" in " ".join(p.cmd)]

        self.assertEqual(len(load_cmds), 9)
        self.assertEqual(len(solar_cmds), 9)
        self.assertEqual(len(net_cmds), 3)

        joined_load = " ".join(" ".join(p.cmd) for p in load_cmds)
        joined_net = " ".join(" ".join(p.cmd) for p in net_cmds)
        self.assertIn("x,x^2,x^3,sin,cos,abs,exp", joined_load)
        self.assertIn("x,x^2,x^3,x^4,sin,cos,abs", joined_load)
        self.assertNotIn("x,x^2,x^3,sin,cos,abs,exp", joined_net)
        self.assertNotIn("x,x^2,x^3,x^4,sin,cos,abs", joined_net)

    def test_symbolic_plan_ignores_global_use_gpu_flag(self) -> None:
        from src.thesis_sweep.plan_symbolic import plan_symbolic

        args = self._make_args(use_gpu=True)
        planned, _run_ids, _train_ids = plan_symbolic(
            args,
            session_id="paperref",
            detached=False,
            kan_train_run_ids=["s3_comp_load_delta_h6"],
        )

        self.assertTrue(planned)
        joined = " ".join(" ".join(p.cmd) for p in planned)
        self.assertNotIn("--use-gpu", joined)

    def test_detached_symbolic_plan_uses_submit_only_instead_of_modal_dash_d(self) -> None:
        from src.thesis_sweep.plan_symbolic import plan_symbolic

        args = self._make_args()
        planned, _run_ids, _train_ids = plan_symbolic(
            args,
            session_id="paperref",
            detached=True,
            kan_train_run_ids=["s3_comp_load_delta_h6"],
        )

        self.assertTrue(planned)
        first = planned[0].cmd
        self.assertEqual(first[:3], ["modal", "run", "-d"])
        self.assertIn("::extract_symbolic_cpu_cli", first[3])
        self.assertIn("--lib-csv", first)
        self.assertNotIn("--submit-only", first)


if __name__ == "__main__":
    unittest.main()
