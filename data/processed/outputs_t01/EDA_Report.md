# EDA Report — GTD cleaned dataset

## Dataset size
- Rows after de-duplication by eventid: 181,691
- Columns in cleaned output: 60
- Year range: 1970–2017

## Cleaning decisions
1. Dropped very sparse/repeated/free-text fields by only keeping 52 core columns useful for mining and cube construction.
2. Casualty columns (`nkill`, `nwound`, `nkillter`, `nwoundte`) were imputed with 0, while missing flags were retained (`*_missing`).
3. Text dimensions were filled with `Unknown` to prevent NULL groups in the data warehouse/cube.
4. Time was discretized into `quarter`, `decade`, `day_period`, and `date_precision`.
5. Coordinates were discretized into 10-degree bands: `lat_bin_10`, `lon_bin_10`, `geo_grid_10`.
6. Casualties were discretized into `casualty_level` and `fatality_level`.

## Main output files
- `gtd_cleaned.csv`
- `eda_missing_report.csv`
- `eda_year_counts.csv`
- `eda_top20_countries.csv`
- `eda_attacktype_counts.csv`
- PNG plots in this folder.
