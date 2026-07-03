import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(exist_ok=True)

products = pd.read_csv(
    RAW_DIR / "olist_products_dataset.csv"
)

products["product_category_name"] = (
    products["product_category_name"]
    .fillna("Unknown")
)

products.to_csv(
    PROCESSED_DIR / "products_clean.csv",
    index=False
)

print("Products cleaned")