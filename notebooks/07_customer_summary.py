import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
fact_orders = pd.read_csv(PROCESSED_DIR / "fact_orders.csv")

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

order_revenue = (
    fact_orders
    .groupby("order_id")["price"]
    .sum()
    .reset_index()
    .rename(columns={"price": "order_value"})
)

orders_with_revenue = orders.merge(
    order_revenue,
    on="order_id",
    how="left"
)

customer_orders = orders_with_revenue.merge(
    customers,
    on="customer_id",
    how="left"
)

customer_summary = (
    customer_orders
    .groupby(
        [
            "customer_unique_id",
            "customer_state",
            "customer_city"
        ]
    )
    .agg(
        order_count=("order_id", "nunique"),
        total_spent=("order_value", "sum"),
        avg_order_value=("order_value", "mean"),
        first_order_date=("order_purchase_timestamp", "min"),
        last_order_date=("order_purchase_timestamp", "max")
    )
    .reset_index()
)

customer_summary = customer_summary.sort_values(
    "total_spent",
    ascending=False
)

customer_summary.to_csv(
    PROCESSED_DIR / "customer_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

top_customers = customer_summary.head(10)

top_customers.to_csv(
    PROCESSED_DIR / "top_customers.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Customer summary created")
print(customer_summary.head(10))
print()
print("Rows:", len(customer_summary))