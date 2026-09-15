SmartSaver
A data engineering pipeline that analyses low-income earner bank transaction behaviour to identify wealth erosion points — fees, cash withdrawal patterns, and balance leaks — and generates bank-switching recommendations.

Project Overview
SmartSaver ingests raw banking transaction data, transforms it through a medallion architecture (Bronze → Silver → Gold), and surfaces actionable insights for users earning R5,000 or less per month. The end goal is prescriptive: not just where money leaks, but what to do about it (e.g., switching from a R7.50/month account to a R0 student account).

This project focuses on the data engineering pipeline — ingestion, cleaning, dimensional modelling, feature engineering, and orchestration — rather than the front-end product.

Architecture
text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Source    │────▶│   Bronze    │────▶│   Silver    │────▶│    Gold     │
│  (Raw CSV)  │     │  (Parquet)  │     │  (Modelled) │     │ (Analytics) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                   │
                    Immutable raw        Cleaned, typed,      Erosion scores,
                    + lineage metadata   star schema          recommendations
Bronze — Raw data landed as-is in Parquet. Only additions are lineage columns (_ingested_at, _source_file). No cleaning, no filtering.

Silver — Cleaned, typed, and modelled into a star schema. Fact and dimension tables. Wealth erosion features computed here.

Gold — Aggregated analytical tables. Per-account erosion scores, bank-switching recommendations, segment summaries.

Data Source
Field	Detail
Dataset	Cifer Fraud Detection Dataset (AF)
Rows used	1,500,000 (part 1 of 8)
Format	CSV → Parquet
Key columns	step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest
The dataset simulates mobile money transactions. The oldbalanceOrg and newbalanceOrig columns allow direct computation of balance deltas — the foundation of the wealth erosion metric.

Download:

powershell
hf download CiferAI/Cifer-Fraud-Detection-Dataset-AF --repo-type dataset --include "Cifer-Fraud-Detection-Dataset-AF-part-1-8.csv" --local-dir ./data
Project Structure
text
Smart-saver/
├── data/                          # Raw downloads (git-ignored)
├── bronze/                        # Raw Parquet + lineage (git-ignored)
├── silver/                        # Cleaned, modelled tables (git-ignored)
├── gold/                          # Analytical outputs (git-ignored)
├── scripts/
│   ├── 01_bronze_ingest.py        # Ingest raw CSV → Bronze Parquet
│   ├── 02_silver_transform.py     # Clean, model, engineer features
│   └── 03_gold_aggregate.py       # Aggregate to analytical tables
├── notebooks/                     # Analysis and visualisation
├── .gitignore
├── requirements.txt
└── README.md
Getting Started
Prerequisites
Python 3.12+ (3.14 tested)

pip

Installation
powershell
pip install -r requirements.txt
requirements.txt:

text
pandas
pyarrow
duckdb
Run the Pipeline
powershell
# Step 1: Ingest raw data into Bronze
python scripts/01_bronze_ingest.py

# Step 2: Transform into Silver
python scripts/02_silver_transform.py

# Step 3: Aggregate into Gold
python scripts/03_gold_aggregate.py
Design Decisions
Why Parquet over CSV?
Columnar storage, built-in compression, and schema preservation. A 138 MB CSV becomes ~45 MB Parquet, and downstream tools (DuckDB, pandas, Spark) read it faster because types are known upfront.

Why a medallion architecture?
Separating Bronze/Silver/Gold means each layer has one job. If Silver logic has a bug, re-run Silver without re-downloading. If Gold needs a new metric, it reads from stable Silver tables. This is the industry-standard pattern for analytical pipelines.

Why lineage columns in Bronze?
_ingested_at and _source_file let you trace any row back to its origin file and ingestion time. Essential for debugging and auditing.

Why index=False in to_parquet()?
Prevents pandas from writing its internal row index as an extra column, which would pollute the schema for every downstream consumer.

Limitations & Future Work
Synthetic data — The Cifer dataset simulates mobile money, not real South African bank transactions. Real integration would require Open Banking APIs (e.g., Stitch) with user consent.

Static fee table — Bank fee comparisons use a manually curated lookup table. Production would require scheduled scraping or a bank partnership.

No live pipeline — Orchestration is script-based. A production version would use Prefect, Airflow, or Dagster with scheduling and retries.

No user-facing app — This project delivers the data engineering foundation, not the end-user product.

Author
Zoe — Data Engineering Project, September 2026

License
This project is for academic purposes. The Cifer dataset is subject to its own license terms on Hugging Face.
