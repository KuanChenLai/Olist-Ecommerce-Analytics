import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# 讀資料

orders = pd.read_csv(
    RAW_DIR / "olist_orders_dataset.csv"
)

items = pd.read_csv(
    RAW_DIR / "olist_order_items_dataset.csv"
)

products = pd.read_csv(
    RAW_DIR / "olist_products_dataset.csv"
)

# Products清理

products["product_category_name"] = (
    products["product_category_name"]
    .fillna("Unknown")
)

# JOIN

fact_orders = (
    items
    .merge(
        orders[
            [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp"
            ]
        ],
        on="order_id",
        how="left"
    )
    .merge(
        products[
            [
                "product_id",
                "product_category_name"
            ]
        ],
        on="product_id",
        how="left"
    )
)

print(fact_orders.head())

print()
print("Shape:")
print(fact_orders.shape)

fact_orders.to_csv(
    PROCESSED_DIR / "fact_orders.csv",
    index=False
)

print()
print("fact_orders created")