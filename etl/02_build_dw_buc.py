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

CUBE_DIMS = ["iyear", "region_txt", "country_txt", "attacktype1_txt", "targtype1_txt", "weaptype1_txt", "casualty_level", "gname"]
CUBE_MEASURES = ["nkill", "nwound", "total_casualties"]


class StarSchemaBuilder:
    """Handles the extraction and transformation of flat data into a Star Schema."""

    @staticmethod
    def _add_surrogate_key(df: pd.DataFrame, key_name: str) -> pd.DataFrame:
        out = df.drop_duplicates().reset_index(drop=True).copy()
        out.insert(0, key_name, np.arange(1, len(out) + 1, dtype="int64"))
        return out

    def build(self, df: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
        date_dim = df[DATE_KEYS].drop_duplicates().reset_index(drop=True).copy()
        date_dt = pd.to_datetime(date_dim["event_date"], errors="coerce")
        # Fix NaT to int64 crash: fill invalid/missing dates with 19700101
        date_dim.insert(0, "date_id", date_dt.dt.strftime("%Y%m%d").fillna("19700101").astype("int64"))
        date_dim = date_dim.drop_duplicates(subset=["date_id"]).reset_index(drop=True)

        loc_dim = self._add_surrogate_key(df[LOCATION_KEYS], "location_id")
        attack_dim = self._add_surrogate_key(df[ATTACK_KEYS], "attack_id")
        actor_dim = self._add_surrogate_key(df[ACTOR_KEYS], "actor_id")
        outcome_dim = self._add_surrogate_key(df[OUTCOME_KEYS], "outcome_id")

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


class IcebergCubeBuilder:
    """Handles the creation of the Iceberg Cube using BUC-style pruning."""

    def __init__(self, dims: list[str], measures: list[str]):
        self.dims = dims
        self.measures = measures

    def build_fast(self, df: pd.DataFrame, min_sup: int) -> pd.DataFrame:
        data = df[self.dims + self.measures + ["eventid"]].copy()
        for d in self.dims:
            data[d] = data[d].fillna("Unknown").astype(str).str.strip().replace({"": "Unknown", "nan": "Unknown"})

        for m in self.measures:
            data[m] = pd.to_numeric(data[m], errors="coerce").fillna(0)

        output_parts: list[pd.DataFrame] = []

        all_total = float(data["total_casualties"].sum())
        all_row = {d: "ALL" for d in self.dims}
        all_row.update({
            "support": len(data),
            "total_killed": float(data["nkill"].sum()),
            "total_wounded": float(data["nwound"].sum()),
            "total_casualties": all_total,
            "avg_casualties_per_event": all_total / len(data) if len(data) else 0.0,
            "cuboid_level": 0,
        })
        output_parts.append(pd.DataFrame([all_row]))

        for level in range(1, len(self.dims) + 1):
            for combo in itertools.combinations(self.dims, level):
                grouped = (
                    data.groupby(list(combo), dropna=False)
                    .agg(
                        support=("eventid", "count"),
                        total_killed=("nkill", "sum"),
                        total_wounded=("nwound", "sum"),
                        total_casualties=("total_casualties", "sum"),
                    )
                    .reset_index()
                )
                grouped = grouped[grouped["support"] > min_sup]
                if grouped.empty:
                    continue
                for d in self.dims:
                    if d not in combo:
                        grouped[d] = "ALL"
                grouped["avg_casualties_per_event"] = grouped["total_casualties"] / grouped["support"]
                grouped["cuboid_level"] = level
                output_parts.append(grouped[self.dims + ["support", "total_killed", "total_wounded", "total_casualties", "avg_casualties_per_event", "cuboid_level"]])

        cube = pd.concat(output_parts, ignore_index=True)
        cube = cube.sort_values(["cuboid_level", "support"], ascending=[True, False]).reset_index(drop=True)
        return cube




