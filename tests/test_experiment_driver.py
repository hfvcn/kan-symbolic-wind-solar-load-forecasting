import importlib.util
import json
import unittest
from pathlib import Path


def _load_driver_module():
    repo_root = Path(__file__).resolve().parents[1]
    driver_path = repo_root / "scripts" / "experiment_driver.py"
    spec = importlib.util.spec_from_file_location("experiment_driver", driver_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestExperimentDriverJsonExtraction(unittest.TestCase):
    def test_extract_last_json_with_trailing_logs(self) -> None:
        mod = _load_driver_module()
        payload = {"run_id": "abc", "status": "completed", "x": 1}
        text = "\n".join(
            [
                "some log line",
                json.dumps(payload, indent=2),
                "[sync] something happened after JSON",
            ]
        )
        obj = mod.extract_last_json(text)
        self.assertEqual(obj["run_id"], "abc")
        self.assertEqual(obj["status"], "completed")

    def test_extract_last_json_prefers_run_payload(self) -> None:
        mod = _load_driver_module()
        text = "\n".join(
            [
                "log",
                json.dumps({"hello": "world"}, indent=2),
                "more log",
                json.dumps({"run_id": "xyz", "status": "completed"}, indent=2),
                "tail log",
            ]
        )
        obj = mod.extract_last_json(text)
        self.assertEqual(obj["run_id"], "xyz")


if __name__ == "__main__":
    unittest.main()
