# Data Warehouse & Iceberg Cube Report

## Star schema table sizes
- `dim_date`: 16,081 rows
- `dim_location`: 41,669 rows
- `dim_attack`: 1,945 rows
- `dim_actor`: 4,464 rows
- `dim_outcome`: 150 rows
- `fact_events`: 181,691 rows

## Iceberg Cube
- Dimensions: decade, region_txt, country_txt, attacktype1_txt, targtype1_txt, weaptype1_txt, casualty_level
- Condition: support > 100
- Output rows: 28,719
- Measures: support, total_killed, total_wounded, total_casualties, avg_casualties_per_event

## Main files
- `gtd_star_schema.sqlite`
- `schema_star.sql`
- `iceberg_cube_min_sup_100.csv`