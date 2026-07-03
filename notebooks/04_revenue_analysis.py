import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

fact_orders = pd.read_csv(
    BASE_DIR / "data" / "processed" / "fact_orders.csv"
)

category_revenue = (
    fact_orders
    .groupby("product_category_name")
    ["price"]
    .sum()
    .reset_index()
    .sort_values("price", ascending=False)
)

print(category_revenue.head(10))

category_revenue.to_csv(
    BASE_DIR / "data" / "processed" / "top_categories.csv",
    index=False
)