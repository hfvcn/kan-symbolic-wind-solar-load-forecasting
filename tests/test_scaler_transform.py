import unittest

import numpy as np
import pandas as pd


class TestScalerTransform(unittest.TestCase):
    def test_transform_inverse_roundtrip(self) -> None:
        from src.data.split import inverse_transform, transform

        df = pd.DataFrame(
            {
                "a": np.asarray([0.0, 1.0, 2.0], dtype=np.float64),
                "b": np.asarray([-1.0, 0.0, 1.0], dtype=np.float64),
                "y": np.asarray([10.0, 11.0, 12.0], dtype=np.float64),
            }
        )
        params = {
            "mean": [1.0, 0.0],
            "scale": [2.0, 4.0],
            "feature_names": ["a", "b"],
            "excluded_cols": ["y"],
        }

        df_z = transform(df, params)
        df_back = inverse_transform(df_z, params)

        # y is excluded and should remain untouched.
        self.assertTrue(np.allclose(df_back["y"].to_numpy(), df["y"].to_numpy()))
        self.assertTrue(np.allclose(df_back["a"].to_numpy(), df["a"].to_numpy()))
        self.assertTrue(np.allclose(df_back["b"].to_numpy(), df["b"].to_numpy()))


if __name__ == "__main__":
    unittest.main()

