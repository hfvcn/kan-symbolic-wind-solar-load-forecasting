from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.reconstruct_predictions import _load_processed_split, _resolve_reconstruction_source


class TestReconstructPredictions(unittest.TestCase):
    def test_load_processed_split_only_requires_requested_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            processed_dir = Path(tmp_dir)
            index = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC", name="timestamp")
            test_df = pd.DataFrame({"load": [1.0, 2.0]}, index=index)
            test_df.to_parquet(processed_dir / "test_demo.parquet")

            loaded = _load_processed_split(processed_dir, split="test", timestamp="demo")

            self.assertEqual(list(loaded.columns), ["load"])
            self.assertEqual(len(loaded), 2)

    def test_resolve_reconstruction_source_prefers_aligned_data_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_run_dir = Path(tmp_dir) / "derived_run"
            (data_run_dir / "processed").mkdir(parents=True)
            (data_run_dir / "artifacts").mkdir(parents=True)
            (data_run_dir / "processed" / "test_demo.parquet").write_bytes(b"PAR1")
            (data_run_dir / "artifacts" / "scaler_params.json").write_text("{}")

            run_id, timestamp = _resolve_reconstruction_source(data_run_dir, data_timestamp="demo")

            self.assertEqual(run_id, data_run_dir.name)
            self.assertEqual(timestamp, "demo")


if __name__ == "__main__":
    unittest.main()
