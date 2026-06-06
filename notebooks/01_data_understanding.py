import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

print("Data path:", RAW_DIR)

files = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
}

for table_name, file_name in files.items():
    file_path = RAW_DIR / file_name

    print(f"\n{'='*50}")
    print(table_name)
    print(f"{'='*50}")

    df = pd.read_csv(file_path)

    print("Shape:", df.shape)
    print("Columns:")
    print(df.columns.tolist())