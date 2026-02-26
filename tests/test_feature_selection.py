import unittest

import pandas as pd


class TestPickFeatureColumns(unittest.TestCase):
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

