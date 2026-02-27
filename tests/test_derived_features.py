import unittest

import numpy as np
import pandas as pd


class TestDerivedFeatures(unittest.TestCase):
    def test_net_load_definition(self) -> None:
        from src.data.derived import compute_net_load

        load = pd.Series([100.0, 110.0], dtype=np.float64)
        wind = pd.Series([10.0, 20.0], dtype=np.float64)
        solar = pd.Series([5.0, 3.0], dtype=np.float64)
        net = compute_net_load(load, wind, solar)
        self.assertTrue(np.allclose(net.to_numpy(), np.asarray([85.0, 87.0], dtype=np.float64)))

    def test_delta_computation(self) -> None:
        from src.data.derived import compute_delta

        cur = pd.Series([10.0, 11.0, 13.0], dtype=np.float64)
        prev = pd.Series([9.0, 10.0, 11.0], dtype=np.float64)
        d = compute_delta(cur, prev)
        self.assertTrue(np.allclose(d.to_numpy(), np.asarray([1.0, 1.0, 2.0], dtype=np.float64)))

    def test_degree_features(self) -> None:
        from src.data.derived import add_degree_features

        df = pd.DataFrame({"temp_2m_c": [20.0, 16.0]}, dtype=np.float64)
        out = add_degree_features(df, base_c=18.0)
        self.assertTrue(np.allclose(out["cdd_18c"].to_numpy(), np.asarray([2.0, 0.0], dtype=np.float64)))
        self.assertTrue(np.allclose(out["hdd_18c"].to_numpy(), np.asarray([0.0, 2.0], dtype=np.float64)))

    def test_wind_cubic_feature(self) -> None:
        from src.data.derived import add_wind_cubic_feature

        df = pd.DataFrame({"wind_speed_10m_m_s": [2.0, -3.0]}, dtype=np.float64)
        out = add_wind_cubic_feature(df)
        self.assertTrue(np.allclose(out["wind_speed_10m_m_s_cubed"].to_numpy(), np.asarray([8.0, -27.0], dtype=np.float64)))

    def test_daylight_ghi_feature(self) -> None:
        from src.data.derived import add_daylight_ghi_feature

        df = pd.DataFrame({"ghi_w_m2": [0.0, 100.0], "is_night": [True, False]})
        out = add_daylight_ghi_feature(df)
        self.assertTrue(np.allclose(out["ghi_day_w_m2"].to_numpy(dtype=np.float64), np.asarray([0.0, 100.0], dtype=np.float64)))


if __name__ == "__main__":
    unittest.main()

