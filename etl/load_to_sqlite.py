import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "olist.db"

conn = sqlite3.connect(DB_PATH)

tables = {
    # raw tables
    "customers": RAW_DIR / "olist_customers_dataset.csv",
    "orders": RAW_DIR / "olist_orders_dataset.csv",
    "order_items": RAW_DIR / "olist_order_items_dataset.csv",
    "products": RAW_DIR / "olist_products_dataset.csv",
    "sellers": RAW_DIR / "olist_sellers_dataset.csv",
    "reviews": RAW_DIR / "olist_order_reviews_dataset.csv",

    # processed tables
    "fact_orders": PROCESSED_DIR / "fact_orders.csv",
    "customer_summary": PROCESSED_DIR / "customer_summary.csv",
    "monthly_revenue": PROCESSED_DIR / "monthly_revenue.csv",
    "top_categories": PROCESSED_DIR / "top_categories.csv",
    "top_sellers": PROCESSED_DIR / "top_sellers.csv",
    "repeat_purchase_summary": PROCESSED_DIR / "repeat_purchase_summary.csv",
    "rfm_segments": PROCESSED_DIR / "rfm_segments.csv",
    "rfm_summary": PROCESSED_DIR / "rfm_summary.csv",
}

for table_name, file_path in tables.items():
    if not file_path.exists():
        print(f"Skipped: {table_name} - file not found: {file_path}")
        continue

    df = pd.read_csv(file_path)

    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False
    )

    print(f"Loaded {table_name}: {len(df)} rows")

conn.close()

print()
print(f"SQLite database created at: {DB_PATH}")