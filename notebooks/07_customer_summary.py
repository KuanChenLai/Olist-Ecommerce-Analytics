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

# Keep the customer and revenue KPIs on the same completed-order basis.
orders = orders.loc[orders["order_status"].eq("delivered")].copy()

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

customer_metrics = (
    customer_orders
    .groupby("customer_unique_id")
    .agg(
        order_count=("order_id", "nunique"),
        total_spent=("order_value", "sum"),
        avg_order_value=("order_value", "mean"),
        first_order_date=("order_purchase_timestamp", "min"),
        last_order_date=("order_purchase_timestamp", "max")
    )
    .reset_index()
)

# A customer can use more than one delivery address. Keep the location from the
# latest order as descriptive data, while retaining exactly one row per person.
latest_location = (
    customer_orders
    .sort_values("order_purchase_timestamp")
    .drop_duplicates("customer_unique_id", keep="last")
    [["customer_unique_id", "customer_state", "customer_city"]]
)

customer_summary = customer_metrics.merge(
    latest_location,
    on="customer_unique_id",
    how="left",
)

customer_summary = customer_summary[
    [
        "customer_unique_id",
        "customer_state",
        "customer_city",
        "order_count",
        "total_spent",
        "avg_order_value",
        "first_order_date",
        "last_order_date",
    ]
]

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
