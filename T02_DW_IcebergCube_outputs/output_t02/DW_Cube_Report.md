# Data Warehouse & Iceberg Cube Report

## Star schema table sizes
- `dim_date`: 16,933 rows
- `dim_location`: 48,322 rows
- `dim_attack`: 2,006 rows
- `dim_actor`: 4,682 rows
- `dim_outcome`: 155 rows
- `fact_events`: 203,931 rows

## Iceberg Cube
- Dimensions: decade, region_txt, country_txt, attacktype1_txt, targtype1_txt, weaptype1_txt, casualty_level
- Condition: support > 100
- Output rows: 31,209
- Measures: support, total_killed, total_wounded, total_casualties, avg_casualties_per_event

## Main files
- `gtd_star_schema.sqlite`
- `schema_star.sql`
- `iceberg_cube_min_sup_100.csv`