SmartSaver
A data engineering pipeline that analyses bank transaction behaviour to identify wealth erosion points — fees that disproportionately affect low-income earners — and quantifies the savings available from switching banks.

Project Overview
SmartSaver ingests raw banking transaction data, transforms it through a medallion architecture (Bronze → Silver → Gold), and produces a fee simulation that answers a single question:

Given a user's transaction pattern, what would each bank charge them?

The pipeline compares four South African bank accounts against 1.5 million real transaction patterns and measures fee erosion as a percentage of transaction value — not absolute rand — because percentage is what a low-income earner can reason about.

Headline finding: Capitec's Global One account charges 13.70% of transaction value on payments under R100, versus 0.10% at FNB Easy Zero. For low-income earners transacting frequently in small amounts, this regressive structure is the single largest source of wealth erosion.

Architecture
text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Source    │────▶│   Bronze    │────▶│   Silver    │────▶│    Gold     │
│  (Raw CSV)  │     │  (Pickle)   │     │  (Modelled) │     │ (Analytics) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
│                   │                   │
Immutable raw        Cleaned, typed,      Fee simulation
+ lineage metadata   account profiles     + comparisons
Bronze — Raw data landed as-is in pickle format with lineage columns (_ingested_at, _source_file). No cleaning, no filtering.

Silver — Cleaned and modelled into a star schema. Account behaviour profiles, bank fee schedule, and a 6-million-row fact table from cross-joining transactions with fee rules.

Gold — Aggregated analytical tables. Bank comparison, size-bucket breakdown, and fee distribution.

Data Source
Field	Detail
Dataset	Cifer Fraud Detection Dataset (AF)
Rows used	1,500,000
Format	CSV → Pickle
Key columns	step, type, amount, nameOrig
The dataset simulates mobile money transactions across five transaction types: CASH_OUT, PAYMENT, CASH_IN, TRANSFER, DEBIT.

Download:

PowerShell
hf download CiferAI/Cifer-Fraud-Detection-Dataset-AF --repo-type dataset --include "Cifer-Fraud-Detection-Dataset-AF-part-1-14.csv" --local-dir ./data
Project Structure
text
Smart-saver/
├── data/                          # Raw downloads (git-ignored)
├── bronze/                        # Raw pickle + lineage (git-ignored)
├── silver/                        # Modelled tables (git-ignored)
├── gold/                          # Analytical outputs (git-ignored)
├── charts/                        # Visualizations (git-ignored)
├── scripts/
│   ├── 01_bronze_ingest.py        # Ingest raw CSV → Bronze pickle
│   ├── 02_silver_transform.py     # Clean, model, simulate fees
│   ├── 03_gold_aggregate.py       # Aggregate to analytical tables
│   └── 04_visualize.py            # Produce charts
├── .gitignore
└── README.md

Pipeline
Step 1: Bronze — Ingest
PowerShell
python scripts\01_bronze_ingest.py
Reads the raw CSV, adds _ingested_at and _source_file lineage columns, writes to bronze/transactions_raw.pkl.

Result: 1,500,000 rows × 13 columns.

Step 2: Silver — Model and Simulate
PowerShell
python scripts\02_silver_transform.py
Produces three tables:

dim_account — 1,481,624 accounts with transaction count, volume, average amount, and type distribution percentages.

dim_bank_fee_schedule — Four SA bank accounts with 2026 pricing:

Bank	Account	Cash Withdrawal	Instant Payment	Debit Order
Capitec	Global One	R10 per R1,000	R6.00	R3.00
Absa	Student Cheque	Free	Free	Free
TymeBank	GoTyme	Free	Free	Free
FNB	Easy Zero	R5 per R1,000	Free	R4.00
fact_transaction_fees — 6,000,000 rows. Cross join of 1.5M transactions × 4 banks,
with fees computed via np.select based on transaction type.

Step 3: Gold — Aggregate
powershell
python scripts\03_gold_aggregate.py
Produces three analytical tables: bank_comparison, bank_by_size, behaviour_insights.

Step 4: Visualize
powershell
python scripts\04_visualize.py
Produces four charts in charts/.

Key Findings
1. Aggregate fee rate: Capitec is 2x FNB, Absa and TymeBank are free
   https://charts/01_fee_rate_by_bank.png

Across all 1.5M transactions:

Capitec: 0.367% of transaction value

FNB: 0.183%

Absa, TymeBank: 0.000%

2. Fee rates are regressive — small transactions cost proportionally more
   https://charts/02_fee_rate_by_size.png

Bank	Micro (<R100)	Small	Medium	Large
Capitec	13.70%	1.16%	0.37%	0.37%
FNB	0.10%	0.11%	0.15%	0.18%
Absa	0%	0%	0%	0%
TymeBank	0%	0%	0%	0%

Capitec's fee rate on micro transactions is 137x higher than FNB's. The smaller the transaction, the worse the erosion.

3. Capitec charges on 78% of transactions; FNB on 36%
   https://charts/03_fee_distribution.png

Capitec applies a fee to almost every action. FNB leaves most small payments free. The yellow band (R1–10 fees) is 18x larger at Capitec than FNB — those are the flat R6 instant payment fees that hit low-income users hardest.

4. The heatmap view
   https://charts/04_fee_heatmap.png

The darkest cell — Capitec × micro at 13.70% — is the entire project in one image.

Methodology Notes
Why balance columns were dropped
Initial analysis assumed oldbalanceOrg and newbalanceOrig preserved chronological arithmetic (oldbalanceOrg - newbalanceOrig == amount). Verification showed this fails for all 1.5M rows — the Cifer dataset is shuffled to prevent machine learning data leakage. The balance-delta approach was abandoned.

Why the analysis reframed from account to transaction
Analysis of dim_account showed 98.8% of accounts appear in exactly 1 transaction (max: 4). There is no account history to build a behaviour profile from. The analysis was reframed as transaction-level fee attribution rather than per-account fee accumulation.

Why monthly fees are excluded
The dataset does not provide sufficient account continuity to attribute monthly fees accurately. The comparison focuses on variable transaction fees — the fees users most directly control through behaviour.

Why pickle instead of Parquet
Windows Smart App Control blocks pyarrow's unsigned _parquet.pyd DLL. Pickle preserves pandas dtypes equivalently. In production, Parquet would be the correct format.

Commercialisation Path
SmartSaver's data asset is the fee simulation engine — a method for quantifying what any transaction pattern costs under any bank's pricing. The business model follows existing South African precedents.

Precedent: Discovery Bank uses transaction data to build detailed client profiles that feed directly into insurance pricing. Capitec has accumulated nearly 2 trillion data points and employs 500+ people in data roles. Platform-based financial data monetisation is already proven in this market.

Regulatory path: South Africa's Open Finance framework (FSCA position paper, Reserve Bank support) is maturing, with API standards targeted for March 2026. POPIA's prior-authorisation regime (Chapter 6) applies when combining datasets across responsible parties — the safe structure is B2B2C.

The engine exists. The remaining work is access to real transaction data and regulatory clearance.

Limitations
Synthetic data. Cifer simulates mobile money, not SA retail banking. Real integration requires Open Banking APIs with user consent.

Static fee schedule. Bank rates are hard-coded from 2026 public pricing. Production would require scheduled scraping or bank partnership.


WTC-GR5NDYRA
No income data. The dataset has no income field. Behaviour-based segmentation is a proxy.

Script-based orchestration. No scheduler or retry logic. Production would use Prefect, Airflow, or Dagster.
