import json
import unittest
from datetime import date
from unittest import mock

import pandas as pd

from src.data.meteorology import (
    OpenMeteoRequest,
    _build_open_meteo_archive_url,
    _open_meteo_hourly_json_to_df,
    align_hourly_to_index,
)


class TestMeteorology(unittest.TestCase):
    def test_build_url_contains_expected_params(self) -> None:
        req = OpenMeteoRequest(
            latitude=31.0,
            longitude=-100.0,
            start_date=date(2018, 1, 1),
            end_date=date(2018, 1, 2),
        )
        url = _build_open_meteo_archive_url(req)
        self.assertIn("archive-api.open-meteo.com", url)
        self.assertIn("latitude=31.0", url)
        self.assertIn("longitude=-100.0", url)
        self.assertIn("start_date=2018-01-01", url)
        self.assertIn("end_date=2018-01-02", url)
        self.assertIn("hourly=temperature_2m%2Cwind_speed_10m%2Csurface_pressure%2Cshortwave_radiation", url)
        self.assertIn("timezone=UTC", url)

    def test_json_to_df_converts_units_and_names(self) -> None:
        payload = {
            "hourly": {
                "time": ["2018-01-01T00:00", "2018-01-01T01:00"],
                "temperature_2m": [0.0, 1.0],
                "wind_speed_10m": [36.0, 18.0],  # km/h
                "surface_pressure": [1000.0, 1001.0],
                "shortwave_radiation": [0.0, 10.0],
            }
        }
        df = _open_meteo_hourly_json_to_df(payload)
        self.assertListEqual(
            list(df.columns),
            ["temp_2m_c", "surface_pressure_hpa", "ghi_w_m2", "wind_speed_10m_m_s"],
        )
        # 36 km/h = 10 m/s
        self.assertAlmostEqual(float(df["wind_speed_10m_m_s"].iloc[0]), 10.0, places=6)
        self.assertTrue(isinstance(df.index, pd.DatetimeIndex))
        self.assertIsNotNone(df.index.tz)

    def test_align_hourly_to_5min_index_no_nan(self) -> None:
        idx = pd.date_range("2018-01-01", periods=3, freq="h", tz="UTC")
        met = pd.DataFrame(
            {
                "temp_2m_c": [0.0, 1.0, 2.0],
                "wind_speed_10m_m_s": [1.0, 2.0, 3.0],
                "surface_pressure_hpa": [1000.0, 1001.0, 1002.0],
                "ghi_w_m2": [0.0, 10.0, 20.0],
            },
            index=idx,
        )
        target_idx = pd.date_range("2018-01-01", periods=25, freq="5min", tz="UTC")
        aligned = align_hourly_to_index(met, target_idx)
        self.assertEqual(len(aligned), len(target_idx))
        self.assertFalse(aligned.isna().any().any())


if __name__ == "__main__":
    unittest.main()

