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


if __name__ == "__main__":
    unittest.main()
