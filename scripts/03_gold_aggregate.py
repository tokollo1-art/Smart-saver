"""
SmartSaver - Gold Layer
Aggregate Silver fee simulation into bank comparison and insight tables.
"""

import pandas as pd
import os

SILVER_DIR = "./silver"
GOLD_DIR = "./gold"
os.makedirs(GOLD_DIR, exist_ok=True)

df = pd.read_pickle(os.path.join(SILVER_DIR, "fact_transaction_fees.pkl"))

df["size_bucket"] = pd.cut(
    df["amount"],
    bins=[0, 100, 1000, 10000, float("inf")],
    labels=["micro", "small", "medium", "large"],
)

# Bank comparison overall
bank_comparison = (
    df.groupby(["bank", "account_type"])
    .agg(
        total_fees=("fee", "sum"),
        total_volume=("amount", "sum"),
        txn_count=("fee", "count"),
        avg_fee=("fee", "mean"),
    )
    .reset_index()
)
bank_comparison["fee_rate_pct"] = (
        bank_comparison["total_fees"] / bank_comparison["total_volume"] * 100
)
bank_comparison = bank_comparison.sort_values("fee_rate_pct")

print(bank_comparison)

bank_by_size = (
    df.groupby(["bank", "size_bucket"], observed=True)
    .agg(
        total_fees=("fee", "sum"),
        total_volume=("amount", "sum"),
        txn_count=("fee", "count"),
        avg_fee=("fee", "mean"),
    )
    .reset_index()
)
bank_by_size["fee_rate_pct"] = (
        bank_by_size["total_fees"] / bank_by_size["total_volume"] * 100
)
bank_by_size = bank_by_size.sort_values(["bank", "size_bucket"])

print(bank_by_size)

df["fee_bucket"] = pd.cut(
    df["fee"],
    bins=[-0.01, 0, 10, 50, float("inf")],
    labels=["R0", "R1-10", "R10-50", "R50+"],
)

behaviour_insights = (
    df.groupby(["bank", "fee_bucket"], observed=True)
    .agg(txn_count=("fee", "count"))
    .unstack(fill_value=0)
)

print(behaviour_insights)

bank_comparison.to_pickle(os.path.join(GOLD_DIR, "bank_comparison.pkl"))
bank_by_size.to_pickle(os.path.join(GOLD_DIR, "bank_by_size.pkl"))
behaviour_insights.to_pickle(os.path.join(GOLD_DIR, "behaviour_insights.pkl"))

print(f"\nGold outputs written to {GOLD_DIR}")
print(f"bank_comparison: {bank_comparison.shape}")
print(f"bank_by_size: {bank_by_size.shape}")
print(f"behaviour_insights: {behaviour_insights.shape}")