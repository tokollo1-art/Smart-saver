"""
SmartSaver - Bronze Layer

Ingest raw Cifer transaction CSV into Bronze pickle format with lineage metadata.
Fallback to pickle because Windows Smart App Control blocks pyarrow's Parquet DLL.
"""


import pandas as pd
import os
from datetime import datetime, timezone

RAW_DIR = "./data"
BRONZE_DIR = "./bronze"
os.makedirs(BRONZE_DIR, exist_ok=True)

raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".csv")]
if not raw_files:
    raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

raw_path = os.path.join(RAW_DIR, raw_files[0])
print(f"Ingesting: {raw_path}")

df = pd.read_csv(raw_path)
df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
df["_source_file"] = raw_files[0]
bronze_path = os.path.join(BRONZE_DIR, "transactions_raw.pkl")
df.to_pickle(bronze_path)

print(f"Rows ingested: {len(df):,}")
print(f"Columns: {list(df.columns)}")
print(df.head(3))