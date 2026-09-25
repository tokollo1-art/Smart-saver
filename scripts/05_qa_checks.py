import pandas as pd
import os

SILVER_DIR = "./silver"
GOLD_DIR = "./gold"

def check_silver():
    dim_account = pd.read_pickle(os.path.join(SILVER_DIR, "dim_account.pkl"))
    fact = pd.read_pickle(os.path.join(SILVER_DIR, "fact_transaction_fees.pkl"))

    # Row count checks
    assert len(dim_account) > 0, "dim_account is empty"
    assert len(fact) > 0, "fact_transaction_fees is empty"

    # Null checks
    assert dim_account["account_id"].isna().sum() == 0, "Null account IDs"
    assert fact["fee"].isna().sum() == 0, "Null fees in fact table"

    # Range checks
    assert fact["fee"].min() >= 0, "Negative fee detected"
    assert fact["amount"].min() >= 0, "Negative transaction amount"

    # Uniqueness checks
    assert fact["bank"].nunique() == 4, f"Expected 4 banks, got {fact['bank'].nunique()}"

    print(" Silver checks passed")

def check_gold():
    bank_comparison = pd.read_pickle(os.path.join(GOLD_DIR, "bank_comparison.pkl"))

    assert len(bank_comparison) == 4, "bank_comparison should have 4 rows"
    assert bank_comparison["fee_rate_pct"].min() >= 0, "Negative fee rate"

    print(" Gold checks passed")

if __name__ == "__main__":
    check_silver()
    check_gold()