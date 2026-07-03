import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

fact_orders = pd.read_csv(
    BASE_DIR / "data" / "processed" / "fact_orders.csv"
)

top_sellers = (
    fact_orders
    .groupby("seller_id")["price"]
    .sum()
    .reset_index()
    .sort_values("price", ascending=False)
)

print(top_sellers.head(10))

top_sellers.to_csv(
    BASE_DIR / "data" / "processed" / "top_sellers.csv",
    index=False
)