import pandas as pd

dim = pd.read_pickle("silver/dim_account.pkl")

print(dim["total_txns"].describe())
print()
print("Accounts by txn count:")
print(dim["total_txns"].value_counts().head(10))
print()
print(f"Accounts with >1 txn:  {(dim['total_txns'] > 1).sum():,}")
print(f"Accounts with >=5 txns: {(dim['total_txns'] >= 5).sum():,}")
print(f"Accounts with >=10 txns: {(dim['total_txns'] >= 10).sum():,}")