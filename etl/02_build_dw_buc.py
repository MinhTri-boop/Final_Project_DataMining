"""
Task T02-A — Star Schema Data Warehouse & Iceberg Cube with optimized BUC-style pruning
Input : gtd_cleaned.csv
Output: SQLite star schema database + Iceberg cube CSV/table

Run:
    python etl/02_build_dw_buc.py --input ../data/processed/outputs_t01/gtd_cleaned.csv --outdir ../data/processed/outputs_t02 --min_sup 100
"""

from __future__ import annotations

import argparse
import itertools
import sqlite3
import time
from pathlib import Path

import numpy as np
import pandas as pd

DATE_KEYS = ["event_date", "iyear", "imonth", "iday", "quarter", "decade", "day_period", "date_precision"]
LOCATION_KEYS = ["country", "country_txt", "region", "region_txt", "provstate", "city", "lat_bin_10", "lon_bin_10", "geo_grid_10", "coord_missing"]
ATTACK_KEYS = ["attacktype1", "attacktype1_txt", "targtype1", "targtype1_txt", "weaptype1", "weaptype1_txt", "weapsubtype1", "weapsubtype1_txt"]
ACTOR_KEYS = ["gname", "individual", "claimed"]
OUTCOME_KEYS = ["success", "suicide", "extended", "multiple", "property", "ishostkid", "ransom"]
FACT_MEASURES = [
    "nkill", "nwound", "nkillter", "nwoundte", "total_casualties", "event_count",
    "nkill_missing", "nwound_missing", "nkillter_missing", "nwoundte_missing",
]

CUBE_DIMS = ["decade", "region_txt", "country_txt", "attacktype1_txt", "targtype1_txt", "weaptype1_txt", "casualty_level"]
CUBE_MEASURES = ["nkill", "nwound", "total_casualties"]


def add_surrogate_key(df: pd.DataFrame, key_name: str) -> pd.DataFrame:
    out = df.drop_duplicates().reset_index(drop=True).copy()
    out.insert(0, key_name, np.arange(1, len(out) + 1, dtype="int64"))
    return out


def build_star_schema(df: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    date_dim = df[DATE_KEYS].drop_duplicates().reset_index(drop=True).copy()
    date_dt = pd.to_datetime(date_dim["event_date"], errors="coerce")
    # Fix NaT to int64 crash: fill invalid/missing dates with 19700101
    date_dim.insert(0, "date_id", date_dt.dt.strftime("%Y%m%d").fillna("19700101").astype("int64"))
    date_dim = date_dim.drop_duplicates(subset=["date_id"]).reset_index(drop=True)

    loc_dim = add_surrogate_key(df[LOCATION_KEYS], "location_id")
    attack_dim = add_surrogate_key(df[ATTACK_KEYS], "attack_id")
    actor_dim = add_surrogate_key(df[ACTOR_KEYS], "actor_id")
    outcome_dim = add_surrogate_key(df[OUTCOME_KEYS], "outcome_id")

    fact = df[["eventid"] + DATE_KEYS + LOCATION_KEYS + ATTACK_KEYS + ACTOR_KEYS + OUTCOME_KEYS + FACT_MEASURES].copy()
    fact["date_id"] = pd.to_datetime(fact["event_date"], errors="coerce").dt.strftime("%Y%m%d").fillna("19700101").astype("int64")
    fact = fact.merge(loc_dim, on=LOCATION_KEYS, how="left")
    fact = fact.merge(attack_dim, on=ATTACK_KEYS, how="left")
    fact = fact.merge(actor_dim, on=ACTOR_KEYS, how="left")
    fact = fact.merge(outcome_dim, on=OUTCOME_KEYS, how="left")

    # Safety to avoid NaNs propagating to required FKs if merges fail (though inner columns shouldn't be null)
    for fk in ["location_id", "attack_id", "actor_id", "outcome_id"]:
        fact[fk] = fact[fk].fillna(0).astype("int64")

    fact_cols = ["eventid", "date_id", "location_id", "attack_id", "actor_id", "outcome_id"] + FACT_MEASURES
    fact = fact[fact_cols].copy()

    dims = {
        "dim_date": date_dim,
        "dim_location": loc_dim,
        "dim_attack": attack_dim,
        "dim_actor": actor_dim,
        "dim_outcome": outcome_dim,
    }
    return dims, fact


def schema_sql(min_sup: int) -> str:
    return f"""
PRAGMA foreign_keys = ON;

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    event_date TEXT,
    iyear INTEGER,
    imonth INTEGER,
    iday INTEGER,
    quarter TEXT,
    decade TEXT,
    day_period TEXT,
    date_precision TEXT
);

CREATE TABLE dim_location (
    location_id INTEGER PRIMARY KEY,
    country INTEGER,
    country_txt TEXT,
    region INTEGER,
    region_txt TEXT,
    provstate TEXT,
    city TEXT,
    lat_bin_10 TEXT,
    lon_bin_10 TEXT,
    geo_grid_10 TEXT,
    coord_missing INTEGER
);

CREATE TABLE dim_attack (
    attack_id INTEGER PRIMARY KEY,
    attacktype1 INTEGER,
    attacktype1_txt TEXT,
    targtype1 INTEGER,
    targtype1_txt TEXT,
    weaptype1 INTEGER,
    weaptype1_txt TEXT,
    weapsubtype1 INTEGER,
    weapsubtype1_txt TEXT
);

CREATE TABLE dim_actor (
    actor_id INTEGER PRIMARY KEY,
    gname TEXT,
    individual INTEGER,
    claimed INTEGER
);

CREATE TABLE dim_outcome (
    outcome_id INTEGER PRIMARY KEY,
    success INTEGER,
    suicide INTEGER,
    extended INTEGER,
    multiple INTEGER,
    property INTEGER,
    ishostkid INTEGER,
    ransom INTEGER
);

CREATE TABLE fact_events (
    eventid INTEGER PRIMARY KEY,
    date_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    attack_id INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    outcome_id INTEGER NOT NULL,
    nkill REAL,
    nwound REAL,
    nkillter REAL,
    nwoundte REAL,
    total_casualties REAL,
    event_count INTEGER,
    nkill_missing INTEGER,
    nwound_missing INTEGER,
    nkillter_missing INTEGER,
    nwoundte_missing INTEGER,
    FOREIGN KEY(date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY(location_id) REFERENCES dim_location(location_id),
    FOREIGN KEY(attack_id) REFERENCES dim_attack(attack_id),
    FOREIGN KEY(actor_id) REFERENCES dim_actor(actor_id),
    FOREIGN KEY(outcome_id) REFERENCES dim_outcome(outcome_id)
);

CREATE TABLE iceberg_cube_min_sup_{min_sup} (
    decade TEXT,
    region_txt TEXT,
    country_txt TEXT,
    attacktype1_txt TEXT,
    targtype1_txt TEXT,
    weaptype1_txt TEXT,
    casualty_level TEXT,
    support INTEGER,
    total_killed REAL,
    total_wounded REAL,
    total_casualties REAL,
    avg_casualties_per_event REAL,
    cuboid_level INTEGER
);

CREATE INDEX idx_fact_date ON fact_events(date_id);
CREATE INDEX idx_fact_location ON fact_events(location_id);
CREATE INDEX idx_fact_attack ON fact_events(attack_id);
CREATE INDEX idx_fact_actor ON fact_events(actor_id);
CREATE INDEX idx_fact_outcome ON fact_events(outcome_id);
""".strip()


def write_schema_sql(path: Path, min_sup: int) -> None:
    path.write_text(schema_sql(min_sup), encoding="utf-8")


def write_to_sqlite(db_path: Path, dims: dict[str, pd.DataFrame], fact: pd.DataFrame, cube: pd.DataFrame, min_sup: int) -> None:
    if db_path.exists():
        db_path.unlink()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql(min_sup))
        for name, table in dims.items():
            table.to_sql(name, conn, if_exists="append", index=False)
        fact.to_sql("fact_events", conn, if_exists="append", index=False)
        cube.to_sql(f"iceberg_cube_min_sup_{min_sup}", conn, if_exists="append", index=False)
        
        # Real foreign key check
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise ValueError(f"Dữ liệu vi phạm khóa ngoại! Chi tiết: {violations}")
            
        conn.commit()


def buc_iceberg_cube_fast(df: pd.DataFrame, dims: list[str], min_sup: int) -> pd.DataFrame:
    data = df[dims + CUBE_MEASURES].copy()
    for d in dims:
        data[d] = data[d].fillna("Unknown").astype(str).str.strip().replace({"": "Unknown", "nan": "Unknown"})

    for m in CUBE_MEASURES:
        data[m] = pd.to_numeric(data[m], errors="coerce").fillna(0)

    output_parts: list[pd.DataFrame] = []

    all_total = float(data["total_casualties"].sum())
    all_row = {d: "ALL" for d in dims}
    all_row.update({
        "support": len(data),
        "total_killed": float(data["nkill"].sum()),
        "total_wounded": float(data["nwound"].sum()),
        "total_casualties": all_total,
        "avg_casualties_per_event": all_total / len(data) if len(data) else 0.0,
        "cuboid_level": 0,
    })
    output_parts.append(pd.DataFrame([all_row]))

    for level in range(1, len(dims) + 1):
        for combo in itertools.combinations(dims, level):
            grouped = (
                data.groupby(list(combo), dropna=False)
                .agg(
                    support=("nkill", "size"),
                    total_killed=("nkill", "sum"),
                    total_wounded=("nwound", "sum"),
                    total_casualties=("total_casualties", "sum"),
                )
                .reset_index()
            )
            grouped = grouped[grouped["support"] > min_sup]
            if grouped.empty:
                continue
            for d in dims:
                if d not in combo:
                    grouped[d] = "ALL"
            grouped["avg_casualties_per_event"] = grouped["total_casualties"] / grouped["support"]
            grouped["cuboid_level"] = level
            output_parts.append(grouped[dims + ["support", "total_killed", "total_wounded", "total_casualties", "avg_casualties_per_event", "cuboid_level"]])

    cube = pd.concat(output_parts, ignore_index=True)
    cube = cube.sort_values(["cuboid_level", "support"], ascending=[True, False]).reset_index(drop=True)
    return cube


def save_metadata(outdir: Path, dims: dict[str, pd.DataFrame], fact: pd.DataFrame, cube: pd.DataFrame, min_sup: int) -> None:
    lines = [
        "# Data Warehouse & Iceberg Cube Report",
        "",
        "## Star schema table sizes",
    ]
    for name, table in dims.items():
        lines.append(f"- `{name}`: {len(table):,} rows")
    lines.append(f"- `fact_events`: {len(fact):,} rows")
    lines.append("")
    lines.append("## Iceberg Cube")
    lines.append(f"- Dimensions: {', '.join(CUBE_DIMS)}")
    lines.append(f"- Condition: support > {min_sup}")
    lines.append(f"- Output rows: {len(cube):,}")
    lines.append("- Measures: support, total_killed, total_wounded, total_casualties, avg_casualties_per_event")
    lines.append("")
    lines.append("## Main files")
    lines.append("- `gtd_star_schema.sqlite`")
    lines.append("- `schema_star.sql`")
    lines.append(f"- `iceberg_cube_min_sup_{min_sup}.csv`")
    (outdir / "DW_Cube_Report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="../data/processed/outputs_t01/gtd_cleaned.csv")
    parser.add_argument("--outdir", default="../data/processed/outputs_t02")
    parser.add_argument("--min_sup", type=int, default=100)
    args = parser.parse_args()

    start = time.time()
    
    # Paths resolved relative to the script location (in etl/)
    base_dir = Path(__file__).parent
    input_path = (base_dir / args.input).resolve()
    outdir = (base_dir / args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist. Please run 01_preprocess_eda.py first.")
        return

    # Use dtype=str to avoid low_memory=False and guessing overhead
    df = pd.read_csv(input_path, dtype=str)
    for c in CUBE_DIMS + ["provstate", "city", "gname", "weapsubtype1_txt"]:
        if c in df.columns:
            df[c] = df[c].fillna("Unknown").astype(str).str.strip().replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})

    # Convert known numeric columns
    for c in FACT_MEASURES + ["iyear", "imonth", "iday", "country", "region", "success", "suicide", "extended", "multiple", "property", "ishostkid", "ransom", "attacktype1", "targtype1", "weaptype1", "weapsubtype1", "individual", "claimed"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    print("Building star schema...")
    dims, fact = build_star_schema(df)

    print("Building fast BUC-style iceberg cube...")
    cube = buc_iceberg_cube_fast(df, CUBE_DIMS, args.min_sup)

    for name, table in dims.items():
        table.to_csv(outdir / f"{name}.csv", index=False, encoding="utf-8-sig")
    fact.to_csv(outdir / "fact_events.csv", index=False, encoding="utf-8-sig")
    cube.to_csv(outdir / f"iceberg_cube_min_sup_{args.min_sup}.csv", index=False, encoding="utf-8-sig")

    write_schema_sql(outdir / "schema_star.sql", args.min_sup)
    write_to_sqlite(outdir / "gtd_star_schema.sqlite", dims, fact, cube, args.min_sup)
    save_metadata(outdir, dims, fact, cube, args.min_sup)

    print(f"Done in {time.time() - start:.1f}s")
    print(f"Output folder: {outdir}")


if __name__ == "__main__":
    main()
