import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

rfm = pd.read_csv(PROCESSED_DIR / "rfm_segments.csv")

total_customers = rfm["customer_unique_id"].nunique()
total_revenue = rfm["Monetary"].sum()

summary = (
    rfm.groupby("Segment")
    .agg(
        customers=("customer_unique_id", "nunique"),
        total_revenue=("Monetary", "sum"),
        avg_recency=("Recency", "mean"),
        avg_frequency=("Frequency", "mean"),
        avg_monetary=("Monetary", "mean")
    )
    .reset_index()
)

summary["customer_percentage"] = (
    summary["customers"] / total_customers
)

summary["revenue_percentage"] = (
    summary["total_revenue"] / total_revenue
)

summary = summary.sort_values(
    "total_revenue",
    ascending=False
)

summary.to_csv(
    PROCESSED_DIR / "rfm_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("RFM summary created.")
print(summary)