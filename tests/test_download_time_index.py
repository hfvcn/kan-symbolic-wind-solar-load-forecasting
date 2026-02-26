import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np
import pandas as pd


class TestDownloadTimeIndex(unittest.TestCase):
    def test_load_hdf5_handles_tz_aware_strings(self) -> None:
        from src.data.download import load_hdf5_to_dataframe

        times = np.asarray(
            [
                b"2018-01-01T00:00:00+00:00",
                b"2018-01-01T00:05:00+00:00",
            ],
            dtype="S",
        )
        meta = np.asarray([b"c0", b"c1"], dtype="S")
        actuals = np.asarray([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64)

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.h5"
            with h5py.File(path, "w") as f:
                f.create_dataset("time_index", data=times)
                f.create_dataset("meta", data=meta)
                f.create_dataset("actuals", data=actuals)

            df = load_hdf5_to_dataframe(path)

        self.assertIsInstance(df.index, pd.DatetimeIndex)
        self.assertIsNotNone(df.index.tz)
        self.assertEqual(df.index[0], pd.Timestamp("2018-01-01T00:00:00Z"))
        self.assertEqual(df.index[1], pd.Timestamp("2018-01-01T00:05:00Z"))
        self.assertListEqual(list(df.columns), ["c0", "c1"])
        self.assertAlmostEqual(float(df.iloc[0, 0]), 1.0, places=12)
        self.assertAlmostEqual(float(df.iloc[1, 1]), 4.0, places=12)

    def test_load_hdf5_handles_time_dash_and_1d(self) -> None:
        from src.data.download import load_hdf5_to_dataframe

        times = np.asarray(
            [
                b"2018-01-01 00:00:00+00:00",
                b"2018-01-01 00:05:00+00:00",
                b"2019-01-01 00:00:00+00:00",
                b"2019-01-01 00:05:00+00:00",
            ],
            dtype="O",
        )
        meta = np.asarray([b"BA", b"37774.967"], dtype="O")
        actuals = np.asarray([1.0, 2.0, 3.0, 4.0], dtype=np.float64)

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "variant.h5"
            with h5py.File(path, "w") as f:
                f.create_dataset("time-index", data=times)
                f.create_dataset("meta", data=meta)
                f.create_dataset("actuals", data=actuals)

            df = load_hdf5_to_dataframe(path, year=2018, default_column_name="MISO")

        self.assertIsInstance(df.index, pd.DatetimeIndex)
        self.assertIsNotNone(df.index.tz)
        self.assertEqual(len(df), 2)
        self.assertListEqual(list(df.columns), ["MISO"])
        self.assertAlmostEqual(float(df.iloc[0, 0]), 1.0, places=12)
        self.assertAlmostEqual(float(df.iloc[1, 0]), 2.0, places=12)


if __name__ == "__main__":
    unittest.main()
