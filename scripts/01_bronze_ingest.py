"""
SmartSaver - Bronze Layer
TODO: Write a one-line description of what this script does.
"""

import pandas as pd
import os
from datetime import datetime, timezone

RAW_DIR = "./data"
BRONZE_DIR = "./bronze"

# TODO 1: Create BRONZE_DIR if it doesn't exist (hint: os.makedirs with exist_ok=True)
os.makedirs(BRONZE_DIR, exist_ok=True)
# TODO 2: Find the raw CSV file in RAW_DIR
#         - List files in RAW_DIR
#         - Filter for files ending in ".csv"
raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".csv")]

#         - Raise FileNotFoundError if empty
if not raw_files:
    raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

#         - Store the filename in a variable called raw_files and the full path in raw_path
raw_path = os.path.join(RAW_DIR, raw_files[0])
print(f"Ingesting: {raw_path}")
# TODO 3: Read the CSV into a DataFrame called df
#         - Use pd.read_csv(raw_path)
df = pd.read_csv(raw_path)
#         - Do NOT pass any cleaning arguments

# TODO 4: Add two lineage columns to df:
#         - "_ingested_at" = current UTC timestamp as ISO string
df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
#         - "_source_file" = the raw filename
df["_source_file"] = raw_files[0]
# TODO 5: Write df to BRONZE_DIR as "transactions_raw.parquet"
#         - Use df.to_parquet(path, index=False)
bronze_path = os.path.join(BRONZE_DIR, "transactions_raw.parquet")
df.to_parquet(bronze_path, index=False)
# TODO 6: Print three things:
#         - Row count (use f-string with :, formatting)
print(f"Rows ingested: {len(df):,}")
#         - Column list
print(f"Columns: {list(df.columns)}")
#         - df.head(3)
print(df.head(3))