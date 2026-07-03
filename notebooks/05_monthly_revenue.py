import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

df = pd.read_csv(
    BASE_DIR / "data" / "processed" / "fact_orders.csv"
)

df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"]
)

df["year_month"] = (
    df["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)

monthly_revenue = (
    df.groupby("year_month")["price"]
    .sum()
    .reset_index()
)

print(monthly_revenue)

monthly_revenue.to_csv(
    BASE_DIR / "data" / "processed" / "monthly_revenue.csv",
    index=False
)