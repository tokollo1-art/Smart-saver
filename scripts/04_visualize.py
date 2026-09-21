"""
SmartSaver - Visualizations
Read Gold outputs and produce charts for the README and presentation.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

GOLD_DIR = "./gold"
CHART_DIR = "./charts"
os.makedirs(CHART_DIR, exist_ok=True)

bank_comparison = pd.read_pickle(os.path.join(GOLD_DIR, "bank_comparison.pkl"))
bank_by_size = pd.read_pickle(os.path.join(GOLD_DIR, "bank_by_size.pkl"))
behaviour_insights = pd.read_pickle(os.path.join(GOLD_DIR, "behaviour_insights.pkl"))

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(
    bank_comparison["bank"],
    bank_comparison["fee_rate_pct"],
    color=["#2ecc71", "#2ecc71", "#f39c12", "#e74c3c"],
)
ax.set_ylabel("Fee rate (% of transaction value)")
ax.set_title("Effective fee rate by bank (all 1.5M transactions)")
for i, v in enumerate(bank_comparison["fee_rate_pct"]):
    ax.text(i, v + 0.005, f"{v:.3f}%", ha="center")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "01_fee_rate_by_bank.png"), dpi=150)
plt.close()

print("Chart 1 saved.")

bank_by_size = pd.read_pickle(os.path.join(GOLD_DIR, "bank_by_size.pkl"))

fig, ax = plt.subplots(figsize=(9, 5))

bucket_order = ["micro", "small", "medium", "large"]

for bank in bank_by_size["bank"].unique():
    subset = bank_by_size[bank_by_size["bank"] == bank].set_index("size_bucket")
    subset = subset.reindex(bucket_order)
    ax.plot(bucket_order, subset["fee_rate_pct"], marker="o", label=bank, linewidth=2)

ax.set_xlabel("Transaction size bucket")
ax.set_ylabel("Fee rate (% of transaction value)")
ax.set_title("Fee rates are regressive: small transactions cost proportionally more")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "02_fee_rate_by_size.png"), dpi=150)
plt.close()

print("Chart 2 saved.")

behaviour_insights = pd.read_pickle(os.path.join(GOLD_DIR, "behaviour_insights.pkl"))
behaviour_insights.columns = behaviour_insights.columns.droplevel(0)
behaviour_insights = behaviour_insights / 1_000_000      # scale BEFORE plotting

fig, ax = plt.subplots(figsize=(9, 5))

behaviour_insights.plot(
    kind="bar",
    stacked=True,
    ax=ax,
    color=["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"],
)

ax.set_xlabel("Bank")
ax.set_ylabel("Transactions (millions)")
ax.set_title("Fee distribution: how many transactions incur a fee")
ax.legend(title="Fee bucket")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "03_fee_distribution.png"), dpi=150)
plt.close()

print("Chart 3 saved.")
fig, ax = plt.subplots(figsize=(8, 4))

pivot = bank_by_size.pivot(index="bank", columns="size_bucket", values="fee_rate_pct")
pivot = pivot[["micro", "small", "medium", "large"]]

im = ax.imshow(pivot.values, cmap="Reds", aspect="auto")
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)

for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        ax.text(j, i, f"{pivot.values[i, j]:.2f}%",
                ha="center", va="center",
                color="white" if pivot.values[i, j] > 5 else "black",
                fontsize=10)

plt.colorbar(im, label="Fee rate (%)")
ax.set_title("Fee rate heatmap by bank and transaction size")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "04_fee_heatmap.png"), dpi=150)
plt.close()

print("Chart 4 saved.")