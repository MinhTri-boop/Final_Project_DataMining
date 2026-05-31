import argparse
import os
import time
from pathlib import Path

import pandas as pd
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine

import importlib

# Use importlib to import modules that start with numbers
mod_01 = importlib.import_module("etl.01_preprocess_eda")
GTDDataCleaner = mod_01.GTDDataCleaner
GTDDataLoader = mod_01.GTDDataLoader
EDAGenerator = mod_01.EDAGenerator

mod_02 = importlib.import_module("etl.02_build_dw_buc")
CUBE_DIMS = mod_02.CUBE_DIMS
CUBE_MEASURES = mod_02.CUBE_MEASURES
IcebergCubeBuilder = mod_02.IcebergCubeBuilder
StarSchemaBuilder = mod_02.StarSchemaBuilder


class PostgresManager:
    """Manages connection and bulk insertion into PostgreSQL."""

    def __init__(self):
        load_dotenv()
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        dbname = os.getenv("DB_NAME", "gtd_dw")

        db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
        self.engine = create_engine(db_url)

    def write_data(self, dims: dict[str, pd.DataFrame], fact: pd.DataFrame, cube: pd.DataFrame, min_sup: int) -> None:
        print("Connecting to PostgreSQL to bulk insert data...")
        with self.engine.begin() as connection:
            # Insert Dimensions
            for name, table in dims.items():
                print(f"  Inserting {name} ({len(table):,} rows)...")
                table.to_sql(name, con=connection, if_exists="replace", index=False)

            # Insert Fact
            print(f"  Inserting fact_events ({len(fact):,} rows)...")
            fact.to_sql("fact_events", con=connection, if_exists="replace", index=False)

            # Insert Cube
            cube_table_name = f"iceberg_cube_min_sup_{min_sup}"
            print(f"  Inserting {cube_table_name} ({len(cube):,} rows)...")
            cube.to_sql(cube_table_name, con=connection, if_exists="replace", index=False)
            
        print("Data successfully inserted into PostgreSQL.")


class ETLPipeline:
    """Unified Orchestrator for the entire ETL process."""

    def __init__(self, input_path: str, eda_outdir: str, min_sup: int):
        base_dir = Path(__file__).parent.parent
        self.input_path = (base_dir / input_path).resolve()
        self.eda_outdir = (base_dir / eda_outdir).resolve()
        self.min_sup = min_sup
        
        # We still generate EDA reports as required by T01
        self.eda_outdir.mkdir(parents=True, exist_ok=True)
        
        self.loader = GTDDataLoader(self.input_path)
        self.cleaner = GTDDataCleaner()
        self.eda = EDAGenerator(self.eda_outdir)
        self.schema_builder = StarSchemaBuilder()
        self.cube_builder = IcebergCubeBuilder(CUBE_DIMS, CUBE_MEASURES)
        self.db_manager = PostgresManager()

    def run(self) -> None:
        overall_start = time.time()
        print(f"=== Starting Unified ETL Pipeline ===")
        print(f"Input: {self.input_path}")
        
        # --- STEP 1: LOAD ---
        raw_csv = self.loader.get_raw_csv_path(self.eda_outdir)
        if not raw_csv:
            return

        # --- STEP 2: CLEAN ---
        cleaned_df, missing_report = self.cleaner.clean(raw_csv)
        
        # Generate EDA plots and reports to disk (as requested)
        self.eda.generate(cleaned_df, missing_report)

        # --- STEP 3: TRANSFORM (STAR SCHEMA & CUBE) ---
        print("\nBuilding Star Schema (in-memory)...")
        dims, fact = self.schema_builder.build(cleaned_df)

        print(f"Building BUC-style Iceberg Cube (min_sup={self.min_sup}) (in-memory)...")
        cube = self.cube_builder.build_fast(cleaned_df, self.min_sup)

        # --- STEP 4: LOAD TO POSTGRESQL ---
        print("\nLoading to PostgreSQL Database...")
        try:
            self.db_manager.write_data(dims, fact, cube, self.min_sup)
        except Exception as e:
            print(f"Database error (Is PostgreSQL running and .env configured?): {e}")

        print(f"\n=== Unified ETL Pipeline completed in {time.time() - overall_start:.1f}s ===")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/globalterrorismdb_0718dist.csv", help="Path to GTD file (.xlsx or .csv)")
    parser.add_argument("--eda_outdir", default="data/processed/outputs_t01", help="Output folder for EDA reports")
    parser.add_argument("--min_sup", type=int, default=100, help="Minimum support for Iceberg Cube")
    args = parser.parse_args()

    pipeline = ETLPipeline(args.input, args.eda_outdir, args.min_sup)
    pipeline.run()


if __name__ == "__main__":
    main()
