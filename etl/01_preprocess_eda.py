"""
Task T01-A — Preprocess & EDA for Global Terrorism Database (GTD)
Input : globalterrorismdb_0522dist.xlsx or .csv
Output: cleaned data + EDA reports/plots

Run:
    python etl/01_preprocess_eda.py --input ../data/raw/globalterrorismdb_0718dist.csv --outdir ../data/processed/outputs_t01

Notes:
- The script only keeps columns useful for EDA, mining, star schema and cube.
- Casualty missing values are imputed as 0 AND missing flags are retained to avoid hiding unknown values.
"""

from __future__ import annotations

import argparse
import csv
import math
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

KEEP_COLS = [
    "eventid", "iyear", "imonth", "iday", "extended",
    "country", "country_txt", "region", "region_txt", "provstate", "city",
    "latitude", "longitude", "specificity", "vicinity",
    "crit1", "crit2", "crit3", "doubtterr", "multiple", "success", "suicide",
    "attacktype1", "attacktype1_txt", "targtype1", "targtype1_txt",
    "natlty1", "natlty1_txt", "gname", "guncertain1", "individual",
    "nperps", "nperpcap", "claimed",
    "weaptype1", "weaptype1_txt", "weapsubtype1", "weapsubtype1_txt",
    "nkill", "nkillter", "nwound", "nwoundte", "property",
    "propextent", "propextent_txt", "ishostkid", "ransom",
    "dbsource", "INT_LOG", "INT_IDEO", "INT_MISC", "INT_ANY",
]

TEXT_COLS = [
    "country_txt", "region_txt", "provstate", "city", "attacktype1_txt",
    "targtype1_txt", "natlty1_txt", "gname", "weaptype1_txt",
    "weapsubtype1_txt", "propextent_txt", "dbsource",
]

CASUALTY_COLS = ["nkill", "nwound", "nkillter", "nwoundte"]
BINARY_UNKNOWN_COLS = ["multiple", "guncertain1", "claimed", "ishostkid", "ransom"]


class GTDDataLoader:
    """Handles loading and extracting GTD data from XLSX or CSV formats."""
    
    def __init__(self, input_path: Path):
        self.input_path = input_path

    @staticmethod
    def _col_to_idx(cell_ref: str) -> int:
        """Convert Excel cell reference A1/AA1 to 1-based column index."""
        n = 0
        for ch in cell_ref:
            if "A" <= ch <= "Z":
                n = n * 26 + (ord(ch) - 64)
            else:
                break
        return n

    @staticmethod
    def _load_shared_strings(z: ZipFile) -> list[str]:
        strings: list[str] = []
        with z.open("xl/sharedStrings.xml") as f:
            for _, elem in ET.iterparse(f, events=("end",)):
                if elem.tag == NS + "si":
                    text = "".join((t.text or "") for t in elem.iter(NS + "t"))
                    strings.append(text)
                    elem.clear()
        return strings

    @staticmethod
    def _get_cell_value(cell, shared_strings: list[str]) -> str:
        cell_type = cell.attrib.get("t")
        if cell_type == "inlineStr":
            is_el = cell.find(NS + "is")
            return "".join((x.text or "") for x in is_el.iter(NS + "t")) if is_el is not None else ""

        v = cell.find(NS + "v")
        if v is None:
            return ""
        raw = v.text or ""
        if cell_type == "s":
            try:
                return shared_strings[int(raw)] if raw else ""
            except (ValueError, IndexError):
                return ""
        return raw

    def extract_selected_xlsx_to_csv(self, csv_path: Path, keep_cols: list[str]) -> None:
        """Fast dependency-light extraction of selected columns from a large XLSX file."""
        print(f"Extracting columns from XLSX: {self.input_path.name}...")
        start = time.time()
        with ZipFile(self.input_path) as z:
            shared = self._load_shared_strings(z)
            selected_indices: set[int] | None = None
            ordered_indices: list[int] | None = None
            headers: list[str] | None = None
            name_to_idx: dict[str, int] = {}
            rows_written = 0

            with z.open("xl/worksheets/sheet1.xml") as f, csv_path.open("w", newline="", encoding="utf-8-sig") as out:
                writer = csv.writer(out)
                for _, row in ET.iterparse(f, events=("end",)):
                    if row.tag != NS + "row":
                        continue

                    values_by_idx = {}
                    for cell in row.findall(NS + "c"):
                        idx = self._col_to_idx(cell.attrib.get("r", ""))
                        if selected_indices is None or idx in selected_indices:
                            values_by_idx[idx] = self._get_cell_value(cell, shared)

                    row_number = int(row.attrib.get("r", "0"))
                    if row_number == 1:
                        max_idx = max(values_by_idx) if values_by_idx else 0
                        all_headers = [values_by_idx.get(i, "") for i in range(1, max_idx + 1)]
                        name_to_idx = {name: i + 1 for i, name in enumerate(all_headers)}
                        headers = [c for c in keep_cols if c in name_to_idx]
                        missing_headers = [c for c in keep_cols if c not in name_to_idx]
                        if missing_headers:
                            print("Warning: these requested columns were not found:", missing_headers)
                        selected_indices = {name_to_idx[c] for c in headers}
                        ordered_indices = [name_to_idx[c] for c in headers]
                        writer.writerow(headers)
                    else:
                        if headers is not None and ordered_indices is not None:
                            writer.writerow([values_by_idx.get(i, "") for i in ordered_indices])
                            rows_written += 1

                    if rows_written and rows_written % 50_000 == 0:
                        print(f"Extracted {rows_written:,} rows...")
                    row.clear()

        print(f"Extraction completed: {rows_written:,} rows in {time.time() - start:.1f}s")

    def get_raw_csv_path(self, outdir: Path) -> Path | None:
        """Returns the path to the ready-to-process raw CSV."""
        if self.input_path.suffix.lower() == ".xlsx":
            if not self.input_path.exists():
                print(f"Error: Input file {self.input_path} does not exist.")
                return None
            raw_csv = outdir / "gtd_selected_raw.csv"
            self.extract_selected_xlsx_to_csv(raw_csv, KEEP_COLS)
            return raw_csv
        else:
            if not self.input_path.exists():
                print(f"Error: Raw CSV {self.input_path} does not exist.")
                return None
            return self.input_path


class GTDDataCleaner:
    """Handles data transformation and cleaning logic."""

    @staticmethod
    def make_lat_band(x) -> str:
        if pd.isna(x):
            return "Unknown"
        try:
            val = float(x)
            if math.isnan(val):
                return "Unknown"
            lower = int(np.floor(val / 10) * 10)
            lower = max(-90, min(80, lower))
            return f"[{lower},{lower + 10})"
        except (ValueError, TypeError):
            return "Unknown"

    @staticmethod
    def make_lon_band(x) -> str:
        if pd.isna(x):
            return "Unknown"
        try:
            val = float(x)
            if math.isnan(val):
                return "Unknown"
            lower = int(np.floor(val / 10) * 10)
            lower = max(-180, min(170, lower))
            return f"[{lower},{lower + 10})"
        except (ValueError, TypeError):
            return "Unknown"

    @staticmethod
    def make_day_period(day) -> str:
        if pd.isna(day) or int(day) <= 0:
            return "Unknown"
        day = int(day)
        if day <= 10:
            return "Early_month_01_10"
        if day <= 20:
            return "Mid_month_11_20"
        return "Late_month_21_31"

    @staticmethod
    def make_casualty_level(x) -> str:
        if pd.isna(x) or x == 0:
            return "0_None"
        if x <= 5:
            return "1_Low_1_5"
        if x <= 20:
            return "2_Medium_6_20"
        if x <= 100:
            return "3_High_21_100"
        return "4_Mass_100_plus"

    def clean(self, raw_csv: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        print("Cleaning dataset...")
        # Use dtype=str to avoid low_memory=False and guessing overhead
        df = pd.read_csv(raw_csv, dtype=str, encoding="latin1")
        df = df.drop_duplicates(subset=["eventid"]).copy()

        # Convert numeric columns safely.
        for col in df.columns:
            if col not in TEXT_COLS:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Text fields: keep a clear Unknown category for cube and star dimensions.
        for col in TEXT_COLS:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .fillna("Unknown")
                    .astype(str)
                    .str.strip()
                    .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
                )

        # Flags before imputation. Use pd.concat for performance.
        new_cols = {}
        for col in CASUALTY_COLS:
            if col in df.columns:
                new_cols[f"{col}_missing"] = df[col].isna().astype(int)
                df[col] = df[col].fillna(0).clip(lower=0)

        for col in ["nperps", "nperpcap"]:
            if col in df.columns:
                new_cols[f"{col}_missing"] = df[col].isna().astype(int)
                df[col] = df[col].fillna(0)

        if new_cols:
            df = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)

        # Unknown binary/coded values in GTD are usually -9; use -9 for actual missing too.
        for col in BINARY_UNKNOWN_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(-9).astype(int)

        # Valid date components and derived time bins.
        derived_cols = {}
        derived_cols["month_known"] = df["imonth"].between(1, 12).astype(int)
        derived_cols["day_known"] = df["iday"].between(1, 31).astype(int)
        derived_cols["month_safe"] = df["imonth"].where(derived_cols["month_known"].eq(1), 1).astype(int)
        derived_cols["day_safe"] = df["iday"].where(derived_cols["day_known"].eq(1), 1).astype(int)
        derived_cols["event_date"] = pd.to_datetime(
            dict(year=df["iyear"].astype(float).fillna(1970).astype(int), 
                 month=derived_cols["month_safe"], 
                 day=derived_cols["day_safe"]),
            errors="coerce",
        )
        derived_cols["quarter"] = np.where(derived_cols["month_known"].eq(1), "Q" + (((df["imonth"] - 1) // 3) + 1).astype(float).fillna(1).astype(int).astype(str), "Unknown")
        derived_cols["decade"] = (df["iyear"].fillna(1970) // 10 * 10).astype(int).astype(str) + "s"
        derived_cols["day_period"] = df["iday"].apply(self.make_day_period)
        derived_cols["date_precision"] = np.select(
            [derived_cols["month_known"].eq(1) & derived_cols["day_known"].eq(1), derived_cols["month_known"].eq(1)],
            ["Full_date", "Year_month_only"],
            default="Year_only",
        )

        # Coordinate bins. Keep original latitude/longitude and use Unknown for missing bins.
        derived_cols["coord_missing"] = (df["latitude"].isna() | df["longitude"].isna()).astype(int)
        derived_cols["lat_bin_10"] = df["latitude"].apply(self.make_lat_band)
        derived_cols["lon_bin_10"] = df["longitude"].apply(self.make_lon_band)
        derived_cols["geo_grid_10"] = derived_cols["lat_bin_10"] + " / " + derived_cols["lon_bin_10"]

        # Casualty measures and bins.
        derived_cols["total_casualties"] = df["nkill"].fillna(0) + df["nwound"].fillna(0)
        derived_cols["casualty_level"] = derived_cols["total_casualties"].apply(self.make_casualty_level)
        derived_cols["fatality_level"] = df["nkill"].fillna(0).apply(self.make_casualty_level)
        derived_cols["event_count"] = 1

        df = pd.concat([df, pd.DataFrame(derived_cols, index=df.index)], axis=1)

        # Clean target columns frequently needed by DW/cube.
        final_cols = [
            "eventid", "event_date", "iyear", "imonth", "iday", "quarter", "decade", "day_period", "date_precision",
            "country", "country_txt", "region", "region_txt", "provstate", "city", "latitude", "longitude",
            "coord_missing", "lat_bin_10", "lon_bin_10", "geo_grid_10",
            "attacktype1", "attacktype1_txt", "targtype1", "targtype1_txt", "weaptype1", "weaptype1_txt",
            "weapsubtype1", "weapsubtype1_txt", "gname", "individual", "claimed", "success", "suicide", "extended",
            "multiple", "property", "ishostkid", "ransom", "nkill", "nwound", "nkillter", "nwoundte", "total_casualties",
            "casualty_level", "fatality_level", "event_count", "nkill_missing", "nwound_missing", "nkillter_missing", "nwoundte_missing",
            "nperps", "nperpcap", "nperps_missing", "nperpcap_missing", "INT_LOG", "INT_IDEO", "INT_MISC", "INT_ANY", "dbsource",
        ]
        final_cols = [c for c in final_cols if c in df.columns]

        missing_report = (
            df[KEEP_COLS]
            .isna()
            .mean()
            .mul(100)
            .round(2)
            .reset_index()
            .rename(columns={"index": "column", 0: "missing_pct"})
            .sort_values("missing_pct", ascending=False)
        )

        return df[final_cols].copy(), missing_report


class EDAGenerator:
    """Handles generating EDA plots and reports."""

    def __init__(self, outdir: Path):
        self.outdir = outdir

    def generate(self, df: pd.DataFrame, missing_report: pd.DataFrame) -> None:
        print("Generating EDA reports and plots...")
        self.outdir.mkdir(parents=True, exist_ok=True)
        missing_report.to_csv(self.outdir / "eda_missing_report.csv", index=False, encoding="utf-8-sig")

        df.groupby("iyear").size().reset_index(name="event_count").to_csv(self.outdir / "eda_year_counts.csv", index=False)
        df["country_txt"].value_counts().head(20).rename_axis("country_txt").reset_index(name="event_count").to_csv(
            self.outdir / "eda_top20_countries.csv", index=False, encoding="utf-8-sig"
        )
        df["attacktype1_txt"].value_counts().rename_axis("attacktype1_txt").reset_index(name="event_count").to_csv(
            self.outdir / "eda_attacktype_counts.csv", index=False, encoding="utf-8-sig"
        )

        # Plot 1: events by year.
        year_counts = df.groupby("iyear").size()
        plt.figure(figsize=(11, 5))
        plt.plot(year_counts.index, year_counts.values, marker="o", linewidth=1)
        plt.title("Number of Terrorism Events by Year")
        plt.xlabel("Year")
        plt.ylabel("Event count")
        plt.tight_layout()
        plt.savefig(self.outdir / "plot_events_by_year.png", dpi=160)
        plt.close()

        # Plot 2: top countries.
        top_countries = df["country_txt"].value_counts().head(15).sort_values()
        plt.figure(figsize=(10, 6))
        plt.barh(top_countries.index, top_countries.values)
        plt.title("Top 15 Countries by Event Count")
        plt.xlabel("Event count")
        plt.tight_layout()
        plt.savefig(self.outdir / "plot_top15_countries.png", dpi=160)
        plt.close()

        # Plot 3: attack types.
        attack_counts = df["attacktype1_txt"].value_counts().sort_values()
        plt.figure(figsize=(10, 6))
        plt.barh(attack_counts.index, attack_counts.values)
        plt.title("Events by Attack Type")
        plt.xlabel("Event count")
        plt.tight_layout()
        plt.savefig(self.outdir / "plot_attack_types.png", dpi=160)
        plt.close()

        # Plot 4: top missing columns from raw selected subset.
        top_missing = missing_report.head(20).sort_values("missing_pct")
        plt.figure(figsize=(9, 6))
        plt.barh(top_missing["column"], top_missing["missing_pct"])
        plt.title("Top 20 Missing Columns in Selected Raw Columns")
        plt.xlabel("Missing percentage (%)")
        plt.tight_layout()
        plt.savefig(self.outdir / "plot_missing_top20.png", dpi=160)
        plt.close()

        # Boxplot: cap at 99th percentile for legibility but keep full values in CSV.
        positive = df.loc[df["total_casualties"] > 0, "total_casualties"]
        if not positive.empty:
            cap = positive.quantile(0.99)
            plt.figure(figsize=(8, 4))
            plt.boxplot(df["total_casualties"].clip(upper=cap), vert=False)
            plt.title(f"Total Casualties Boxplot, capped at p99={cap:.0f}")
            plt.xlabel("Total casualties")
            plt.tight_layout()
            plt.savefig(self.outdir / "plot_casualties_boxplot_capped.png", dpi=160)
            plt.close()

        report = f"""# EDA Report — GTD cleaned dataset

## Dataset size
- Rows after de-duplication by eventid: {len(df):,}
- Columns in cleaned output: {df.shape[1]}
- Year range: {int(df['iyear'].min(skipna=True))}–{int(df['iyear'].max(skipna=True))}

## Cleaning decisions
1. Dropped very sparse/repeated/free-text fields by only keeping {len(KEEP_COLS)} core columns useful for mining and cube construction.
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
"""
        (self.outdir / "EDA_Report.md").write_text(report, encoding="utf-8")


