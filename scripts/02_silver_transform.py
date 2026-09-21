"""
SmartSaver - Silver Layer
Transform Bronze transaction data into account-level behaviour profiles
and a bank fee schedule for fee-erosion simulation.
"""

import pandas as pd
import os
import numpy as np

BRONZE_DIR = "./bronze"
SILVER_DIR = "./silver"
os.makedirs(SILVER_DIR, exist_ok=True)


file_path = "./bronze/transactions_raw.pkl"
df = pd.read_pickle(file_path)

df = df.drop(columns=['oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest',
                 'newbalanceDest', 'isFraud', 'isFlaggedFraud',
                 'nameDest', '_ingested_at', '_source_file'])
print(f"Remaining columns: {df.columns.tolist()}")


agg = df.groupby("nameOrig").agg(
 total_txns=("amount", "count"),
 total_volume=("amount", "sum"),
 avg_amount=("amount", "mean"),
)
counts = df.groupby(["nameOrig", "type"]).size().unstack(fill_value=0)
pct = counts.div(counts.sum(axis=1), axis=0)
pct.columns = ["pct_" + c.lower() for c in pct.columns]
dim_account = agg.join(pct).reset_index().rename(columns={"nameOrig": "account_id"})

print(f"dim_account shape: {dim_account.shape}")
print(dim_account.head(5))

dim_bank_fee_schedule = pd.DataFrame([
 {"bank": "Capitec",  "account_type": "Global One",     "monthly_fee": 7.50, "cash_withdrawal_fee_per_1000": 10.00, "instant_payment_fee": 6.00, "debit_order_fee": 3.00, "eligibility": "none"},
 {"bank": "Absa",     "account_type": "Student Cheque", "monthly_fee": 0.00, "cash_withdrawal_fee_per_1000":  0.00, "instant_payment_fee": 0.00, "debit_order_fee": 0.00, "eligibility": "age 18-27"},
 {"bank": "TymeBank", "account_type": "GoTyme",         "monthly_fee": 0.00, "cash_withdrawal_fee_per_1000":  0.00, "instant_payment_fee": 0.00, "debit_order_fee": 0.00, "eligibility": "none"},
 {"bank": "FNB",      "account_type": "Easy Zero",      "monthly_fee": 0.00, "cash_withdrawal_fee_per_1000":  5.00, "instant_payment_fee": 0.00, "debit_order_fee": 4.00, "eligibility": "none"},
])
fact = df.merge(dim_bank_fee_schedule, how="cross")

conditions = [
    fact["type"] == "CASH_OUT",
    fact["type"] == "TRANSFER",
    fact["type"] == "PAYMENT",
    fact["type"] == "DEBIT",
    fact["type"] == "CASH_IN",
    ]

values = [
    (fact["amount"] / 1000) * fact["cash_withdrawal_fee_per_1000"],
    fact["instant_payment_fee"],
    fact["instant_payment_fee"],
    fact["debit_order_fee"],
    0.0,
    ]

fact["fee"] = np.select(conditions, values, default=0.0)
fact_transaction_fees = fact[[
    "step", "type", "amount", "nameOrig",
    "bank", "account_type", "fee"
]].rename(columns={"nameOrig": "account_id"})
print(f"fact_transaction_fees shape: {fact_transaction_fees.shape}")
print(fact_transaction_fees.head(5))

fact_transaction_fees.to_pickle(os.path.join(SILVER_DIR, "fact_transaction_fees.pkl"))
dim_account.to_pickle(os.path.join(SILVER_DIR, "dim_account.pkl"))
dim_bank_fee_schedule.to_pickle(os.path.join(SILVER_DIR, "dim_bank_fee_schedule.pkl"))

print(f"dim_account rows: {len(dim_account):,}")
print(f"dim_bank_fee_schedule rows: {len(dim_bank_fee_schedule)}")
print(dim_account.head(5))
print(dim_bank_fee_schedule)