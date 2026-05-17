import unittest

import pandas as pd


class TestPickFeatureColumns(unittest.TestCase):
    def test_feature_groups_include_fine_grained_groups(self) -> None:
        from src.data.features import get_feature_groups

        groups = get_feature_groups()
        for k in [
            "cyclic",
            "solar",
            "meteorology",
            "lag_pattern",
            "solar_geom",
            "solar_flag",
            "meteo_irradiance",
            "meteo_wind",
            "meteo_temp",
            "meteo_degree",
        ]:
            self.assertIn(k, groups)

        self.assertTrue(set(groups["solar"]).issuperset(set(groups["solar_geom"])))
        self.assertTrue(set(groups["solar"]).issuperset(set(groups["solar_flag"])))
        self.assertTrue(set(groups["meteorology"]).issuperset(set(groups["meteo_irradiance"])))

    def test_can_disable_groups_and_lags(self) -> None:
        from src.kan_sr.dataset import pick_feature_columns

        df = pd.DataFrame(
            {
                "load": [1.0, 2.0],
                "wind": [0.1, 0.2],
                "solar": [0.0, 0.5],
                "temp_2m_c": [10.0, 11.0],
                "hour_sin": [0.0, 0.1],
                "solar_altitude": [5.0, 10.0],
                "load_lag_1": [0.9, 1.9],
                "wind_lag_1": [0.05, 0.15],
            }
        )

        cols = pick_feature_columns(
            df,
            target_col="load",
            include_base=True,
            include_groups=[],
            lag_steps=[],
            lag_series=[],
        )
        self.assertEqual(cols, ["wind", "solar"])

    def test_raises_if_no_features_selected(self) -> None:
        from src.kan_sr.dataset import pick_feature_columns

        df = pd.DataFrame({"load": [1.0, 2.0]})
        with self.assertRaises(ValueError):
            _ = pick_feature_columns(
                df,
                target_col="load",
                include_base=False,
                include_groups=[],
                lag_steps=[],
                lag_series=[],
            )

    def test_trend_and_seasonal_core_profiles_return_fixed_features(self) -> None:
        from src.kan_sr.dataset import pick_feature_columns

        df = pd.DataFrame(
            {
                "delta_net_load_h6": [1.0, 2.0],
                "temp_2m_c": [10.0, 11.0],
                "surface_pressure_hpa": [1000.0, 1002.0],
                "cdd_18c": [0.0, 0.0],
                "hdd_18c": [8.0, 7.0],
                "load_lag_12": [0.8, 1.8],
                "load_lag_24": [0.7, 1.7],
                "load_lag_48": [0.6, 1.6],
                "hour_sin": [0.0, 0.1],
                "hour_cos": [1.0, 0.9],
                "dow_sin": [0.0, 0.0],
                "dow_cos": [1.0, 1.0],
                "month_sin": [0.5, 0.5],
                "month_cos": [0.8, 0.8],
                "solar_altitude": [5.0, 10.0],
                "solar_azimuth": [120.0, 130.0],
                "is_night": [1.0, 0.0],
                "ghi_w_m2": [0.0, 100.0],
                "ghi_day_w_m2": [0.0, 80.0],
            }
        )

        trend_cols = pick_feature_columns(df, target_col="delta_net_load_h6", include_base=False, include_groups=[], lag_steps=[], lag_series=[], feature_profile="trend_core")
        seasonal_cols = pick_feature_columns(df, target_col="delta_net_load_h6", include_base=False, include_groups=[], lag_steps=[], lag_series=[], feature_profile="seasonal_core")

        self.assertEqual(
            trend_cols,
            ["temp_2m_c", "surface_pressure_hpa", "cdd_18c", "hdd_18c", "load_lag_12", "load_lag_24", "load_lag_48"],
        )
        self.assertEqual(
            seasonal_cols,
            ["hour_sin", "hour_cos", "dow_sin", "dow_cos", "month_sin", "month_cos", "solar_altitude", "solar_azimuth", "is_night", "ghi_w_m2", "ghi_day_w_m2"],
        )

    def test_thesis_26_profile_excludes_new_physics_columns(self) -> None:
        from src.kan_sr.dataset import pick_feature_columns

        df = pd.DataFrame(
            {
                "load": [1.0, 2.0],
                "wind": [0.1, 0.2],
                "solar": [0.0, 0.5],
                "hour_sin": [0.0, 0.1],
                "hour_cos": [1.0, 0.9],
                "dow_sin": [0.0, 0.0],
                "dow_cos": [1.0, 1.0],
                "month_sin": [0.5, 0.5],
                "month_cos": [0.8, 0.8],
                "solar_altitude": [5.0, 10.0],
                "solar_azimuth": [90.0, 95.0],
                "is_night": [False, False],
                "temp_2m_c": [10.0, 11.0],
                "wind_speed_10m_m_s": [4.0, 5.0],
                "wind_speed_10m_m_s_cubed": [64.0, 125.0],
                "wind_speed_hub_est": [5.5, 6.8],
                "surface_pressure_hpa": [1010.0, 1011.0],
                "ghi_w_m2": [500.0, 510.0],
                "ghi_day_w_m2": [500.0, 510.0],
                "ghi_temp_corr_w_m2": [480.0, 490.0],
                "cdd_18c": [0.0, 0.0],
                "hdd_18c": [8.0, 7.0],
                "wind_lag_24": [0.05, 0.15],
                "wind_lag_48": [0.03, 0.12],
            }
        )

        cols = pick_feature_columns(
            df,
            target_col="delta_wind_h6",
            include_base=False,
            include_groups=["cyclic", "meteo_wind"],
            lag_steps=[24, 48],
            lag_series=["wind"],
            feature_profile="thesis_26",
        )
        self.assertNotIn("wind_speed_hub_est", cols)
        self.assertNotIn("ghi_temp_corr_w_m2", cols)
        self.assertEqual(cols, ["hour_sin", "hour_cos", "dow_sin", "dow_cos", "month_sin", "month_cos", "wind_speed_10m_m_s", "wind_speed_10m_m_s_cubed", "wind_lag_24", "wind_lag_48"])


if __name__ == "__main__":
    unittest.main()
