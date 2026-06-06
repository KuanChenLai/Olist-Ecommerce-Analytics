import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
}

missing_report = []

for table_name, file_name in files.items():
    df = pd.read_csv(RAW_DIR / file_name)

    total_rows = len(df)
    missing_counts = df.isnull().sum()

    for column_name, missing_count in missing_counts.items():
        if missing_count > 0:
            missing_rate = missing_count / total_rows

            missing_report.append({
                "table": table_name,
                "column": column_name,
                "missing_count": int(missing_count),
                "total_rows": int(total_rows),
                "missing_rate": round(missing_rate, 4)
            })

missing_df = pd.DataFrame(missing_report)

print("\nMissing Value Report")
print("=" * 80)
print(missing_df)

output_path = OUTPUT_DIR / "missing_value_report.csv"
missing_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\nSaved report to:")
print(output_path)