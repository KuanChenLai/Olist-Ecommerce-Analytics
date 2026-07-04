import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

customer_summary = pd.read_csv(
    PROCESSED_DIR / "customer_summary.csv"
)

# 轉成 datetime
customer_summary["last_order_date"] = pd.to_datetime(
    customer_summary["last_order_date"]
)

# Reference Date
reference_date = customer_summary["last_order_date"].max()

# Recency
customer_summary["Recency"] = (
    reference_date - customer_summary["last_order_date"]
).dt.days

# Frequency
customer_summary["Frequency"] = customer_summary["order_count"]

# Monetary
customer_summary["Monetary"] = customer_summary["total_spent"]

# 建立 RFM Table
rfm_table = customer_summary[
    [
        "customer_unique_id",
        "Recency",
        "Frequency",
        "Monetary"
    ]
]

rfm_table.to_csv(
    PROCESSED_DIR / "rfm_table.csv",
    index=False,
    encoding="utf-8-sig"
)

rfm = pd.read_csv(PROCESSED_DIR / "rfm_table.csv")

# 避免 Monetary 有空值
rfm["Monetary"] = rfm["Monetary"].fillna(0)

# R：Recency 越小越好，所以分數反過來
rfm["R_score"] = pd.qcut(
    rfm["Recency"],
    q=5,
    labels=[5, 4, 3, 2, 1],
    duplicates="drop"
)

# F：Frequency 越大越好
rfm["F_score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5],
    duplicates="drop"
)

# M：Monetary 越大越好
rfm["M_score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5],
    duplicates="drop"
)

rfm["R_score"] = rfm["R_score"].astype(int)
rfm["F_score"] = rfm["F_score"].astype(int)
rfm["M_score"] = rfm["M_score"].astype(int)

rfm["RFM_Score"] = (
    rfm["R_score"].astype(str)
    + rfm["F_score"].astype(str)
    + rfm["M_score"].astype(str)
)

def assign_segment(row):
    r = row["R_score"]
    f = row["F_score"]
    m = row["M_score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champion"
    elif r >= 3 and f >= 3:
        return "Loyal Customer"
    elif r >= 4 and f <= 2:
        return "New Customer"
    elif r <= 2 and f >= 3:
        return "At Risk"
    elif r <= 2 and f <= 2:
        return "Lost Customer"
    elif m >= 4:
        return "Big Spender"
    else:
        return "Others"

rfm["Segment"] = rfm.apply(assign_segment, axis=1)

rfm.to_csv(
    PROCESSED_DIR / "rfm_segments.csv",
    index=False,
    encoding="utf-8-sig"
)

segment_summary = (
    rfm.groupby("Segment")
    .agg(
        customers=("customer_unique_id", "count"),
        avg_recency=("Recency", "mean"),
        avg_frequency=("Frequency", "mean"),
        avg_monetary=("Monetary", "mean"),
        total_monetary=("Monetary", "sum")
    )
    .reset_index()
    .sort_values("customers", ascending=False)
)

segment_summary.to_csv(
    PROCESSED_DIR / "rfm_segment_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("RFM analysis completed.")
print("\nSegment Summary:")
print(segment_summary)