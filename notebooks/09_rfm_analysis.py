
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# --------------------------------------------------
# 1. 讀取 RFM 基礎資料
# --------------------------------------------------

customer_summary = pd.read_csv(
    PROCESSED_DIR / "customer_summary.csv",
    parse_dates=["last_order_date"],
)

# Build RFM input from the canonical one-row-per-customer table. Keeping this
# step here avoids accidentally running the obsolete duplicate RFM script.
reference_date = customer_summary["last_order_date"].max()
rfm = customer_summary[["customer_unique_id"]].copy()
rfm["Recency"] = (
    reference_date - customer_summary["last_order_date"]
).dt.days
rfm["Frequency"] = customer_summary["order_count"]
rfm["Monetary"] = customer_summary["total_spent"]

rfm.to_csv(
    PROCESSED_DIR / "rfm_table.csv",
    index=False,
    encoding="utf-8-sig",
)

required_columns = {
    "customer_unique_id",
    "Recency",
    "Frequency",
    "Monetary"
}

missing_columns = required_columns - set(rfm.columns)

if missing_columns:
    raise ValueError(
        f"rfm_table.csv 缺少必要欄位：{sorted(missing_columns)}"
    )

# 數值欄位轉型與缺失值處理
for column in ["Recency", "Frequency", "Monetary"]:
    rfm[column] = pd.to_numeric(
        rfm[column],
        errors="coerce"
    )

rfm["Recency"] = rfm["Recency"].fillna(
    rfm["Recency"].max()
)

rfm["Frequency"] = rfm["Frequency"].fillna(0)

rfm["Monetary"] = rfm["Monetary"].fillna(0)

# --------------------------------------------------
# 2. 建立 RFM 分數
# --------------------------------------------------

# Recency 越小越好
# 使用 rank(method="average")，避免相同 Recency 被任意拆分
rfm["R_score"] = pd.qcut(
    rfm["Recency"].rank(method="average"),
    q=5,
    labels=[5, 4, 3, 2, 1]
).astype(int)

# Frequency 不使用 qcut。
# Olist 多數客戶只購買一次，若用 rank(method="first")
# 會將相同購買次數任意分散到不同分數。
def score_frequency(frequency):
    if frequency <= 1:
        return 1
    elif frequency == 2:
        return 2
    elif frequency == 3:
        return 3
    elif frequency == 4:
        return 4
    else:
        return 5


rfm["F_score"] = (
    rfm["Frequency"]
    .apply(score_frequency)
    .astype(int)
)

# Monetary 越高越好
rfm["M_score"] = pd.qcut(
    rfm["Monetary"].rank(method="average"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# 組合分數
rfm["RF_score"] = (
    rfm["R_score"].astype(str)
    + rfm["F_score"].astype(str)
)

rfm["RFM_score"] = (
    rfm["R_score"].astype(str)
    + rfm["F_score"].astype(str)
    + rfm["M_score"].astype(str)
)

# 方便比較客戶整體價值
rfm["RFM_total_score"] = (
    rfm["R_score"]
    + rfm["F_score"]
    + rfm["M_score"]
)

rfm["FM_value_score"] = (
    rfm["F_score"]
    + rfm["M_score"]
) / 2

# --------------------------------------------------
# 3. 客戶分群
# --------------------------------------------------

def assign_segment(row):
    r = row["R_score"]
    f = row["F_score"]
    m = row["M_score"]

    # 最近購買、具有回購行為且消費價值高
    if r >= 4 and f >= 3 and m >= 4:
        return "Champions"

    # 回購與消費表現穩定
    elif r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"

    # 最近購買，已有第二次以上消費潛力
    elif r >= 4 and f >= 2 and m >= 2:
        return "Potential Loyalists"

    # 最近第一次購買
    elif r == 5 and f == 1:
        return "New Customers"

    # 最近購買一次，而且消費金額偏高
    elif r == 4 and f == 1 and m >= 3:
        return "Promising"

    # 購買次數不多，但單次消費價值高
    elif f <= 2 and m == 5 and r >= 3:
        return "Big Spenders"

    # 曾經具有高回購與高消費價值，但近期未購買
    elif r <= 2 and f >= 4 and m >= 4:
        return "Cannot Lose Them"

    # 過去有回購與消費價值，但近期沉寂
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"

    # 活躍度與消費價值普通，需要進一步互動
    elif r == 3 and f <= 2 and m >= 2:
        return "Need Attention"

    # 已久未購買，但仍有一定消費價值
    elif r <= 2 and f <= 2 and m >= 3:
        return "Hibernating"

    # 已久未購買、只買一次且消費價值偏低
    elif r <= 2 and f == 1 and m <= 2:
        return "Lost Customers"

    else:
        return "Others"


rfm["Segment"] = rfm.apply(
    assign_segment,
    axis=1
)

# 建立 Power BI 使用的固定排序
segment_order = {
    "Champions": 1,
    "Loyal Customers": 2,
    "Potential Loyalists": 3,
    "New Customers": 4,
    "Promising": 5,
    "Big Spenders": 6,
    "Need Attention": 7,
    "At Risk": 8,
    "Cannot Lose Them": 9,
    "Hibernating": 10,
    "Lost Customers": 11,
    "Others": 12
}

rfm["Segment_Order"] = (
    rfm["Segment"]
    .map(segment_order)
    .fillna(99)
    .astype(int)
)

# --------------------------------------------------
# 4. 輸出客戶層級 RFM 資料
# --------------------------------------------------

rfm = rfm.sort_values(
    ["Segment_Order", "RFM_total_score", "Monetary"],
    ascending=[True, False, False]
)

rfm.to_csv(
    PROCESSED_DIR / "rfm_segments.csv",
    index=False,
    encoding="utf-8-sig"
)

# --------------------------------------------------
# 5. 建立分群摘要
# --------------------------------------------------

total_customers = rfm["customer_unique_id"].nunique()
total_revenue = rfm["Monetary"].sum()

rfm_summary = (
    rfm.groupby(
        ["Segment", "Segment_Order"],
        as_index=False
    )
    .agg(
        customers=("customer_unique_id", "nunique"),
        total_revenue=("Monetary", "sum"),
        avg_recency=("Recency", "mean"),
        avg_frequency=("Frequency", "mean"),
        avg_monetary=("Monetary", "mean"),
        avg_r_score=("R_score", "mean"),
        avg_f_score=("F_score", "mean"),
        avg_m_score=("M_score", "mean"),
        avg_rfm_total_score=("RFM_total_score", "mean")
    )
)

rfm_summary["customer_percentage"] = (
    rfm_summary["customers"] / total_customers
)

rfm_summary["revenue_percentage"] = (
    rfm_summary["total_revenue"] / total_revenue
)

rfm_summary = rfm_summary.sort_values(
    "Segment_Order"
)

rfm_summary.to_csv(
    PROCESSED_DIR / "rfm_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

# --------------------------------------------------
# 6. 顯示驗證結果
# --------------------------------------------------

print("RFM V3 analysis completed.")
print()

display_columns = [
    "Segment",
    "customers",
    "total_revenue",
    "avg_recency",
    "avg_frequency",
    "avg_monetary",
    "customer_percentage",
    "revenue_percentage"
]

print(
    rfm_summary[display_columns]
    .sort_values(
        "total_revenue",
        ascending=False
    )
    .to_string(index=False)
)

print()
print("Validation:")
print(f"Total customers: {total_customers:,}")
print(f"Segment customers: {rfm_summary['customers'].sum():,}")
print(f"Total revenue: {total_revenue:,.2f}")
print(
    "Revenue in summary: "
    f"{rfm_summary['total_revenue'].sum():,.2f}"
)
