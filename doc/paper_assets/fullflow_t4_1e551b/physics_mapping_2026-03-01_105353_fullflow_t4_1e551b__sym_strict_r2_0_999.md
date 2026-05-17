# Physics Mapping Report: 2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999

- target: `delta_net_load_h6`
- data_run: `2026-03-01_105353_fullflow_t4_1e551b__derived_h1_6_12_24` (timestamp: `2026-03-01_105504`)
- score: `0.0` (n_checks=2)
- json: `doc/paper_assets/fullflow_t4_1e551b/physics_mapping_2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999.json`

## Extracted Formula (LaTeX)

$$
435.280060843279 \left|{2.83869505503449 \sin{\left(1.0483619896655 hour_{cos} - 3.62304456315341 \right)} + 0.860919895626679 \left|{0.18900503029273 solar_{altitude} - 1.23325907458231}\right| + 0.170376928016367 \left|{0.000331381574060675 solar_{lag 12} - 11.4597375184222}\right| - 10.9246843390619}\right| - 2104.98765124376 \left|{0.0703531271870772 \left|{0.000546842466402175 solar_{lag 12} - 13.0581674792722}\right| - 0.692623956831294 \left|{6.76749673359431 \cdot 10^{-5} wind_{lag 12} + 8.3329110972453}\right| + 0.882238289904173 \left|{6.22412731829587 \cdot 10^{-5} wind_{lag 48} + 7.58591153222722}\right| - 2.62882622060852}\right| - 588.049835553 \left|{2.04996493233755 is_{night} + 20.6666972562898 \sin{\left(1.13686929956997 hour_{sin} - 7.59658962562569 \right)} + 0.972843515393166 \left|{13.3386977194559 hour_{cos} + 1.6036239549666}\right| + 0.0883206488418438 \left|{0.170625235039008 solar_{altitude} - 3.38220645041846}\right| - 0.0315169644953786 \left|{0.000597967735296131 solar_{lag 12} - 10.1991019331769}\right| + 2.74037572983258 \left|{5.47339545598433 \cdot 10^{-5} solar_{lag 24} + 6.62875021255848}\right| - 14.9938110505217}\right| + 2298.30776496642
$$

## Checks

| name | passed | score | var | pct_positive | pct_negative | power_counts |
| --- | --- | --- | --- | --- | --- | --- |
| wind_proxy_monotone_decreasing | False | 0.0 | wind_speed_10m_m_s_cubed | 0.0 | 0.0 |  |
| ghi_proxy_monotone_decreasing | False | 0.0 | ghi_day_w_m2 | 0.0 | 0.0 |  |

