import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

customer_summary = pd.read_csv(
    PROCESSED_DIR / "customer_summary.csv"
)

total_customers = len(customer_summary)

repeat_customers = customer_summary[
    customer_summary["order_count"] > 1
]

one_time_customers = customer_summary[
    customer_summary["order_count"] == 1
]

repeat_customer_count = len(repeat_customers)
one_time_customer_count = len(one_time_customers)

repeat_purchase_rate = repeat_customer_count / total_customers

avg_spent_per_customer = customer_summary["total_spent"].mean()
avg_order_count_per_customer = customer_summary["order_count"].mean()

repeat_avg_spent = repeat_customers["total_spent"].mean()
one_time_avg_spent = one_time_customers["total_spent"].mean()

summary = pd.DataFrame({
    "metric": [
        "Total Customers",
        "Repeat Customers",
        "One-time Customers",
        "Repeat Purchase Rate",
        "Average Spend per Customer",
        "Average Orders per Customer",
        "Repeat Customer Average Spend",
        "One-time Customer Average Spend"
    ],
    "value": [
        total_customers,
        repeat_customer_count,
        one_time_customer_count,
        repeat_purchase_rate,
        avg_spent_per_customer,
        avg_order_count_per_customer,
        repeat_avg_spent,
        one_time_avg_spent
    ]
})

summary.to_csv(
    PROCESSED_DIR / "repeat_purchase_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Repeat purchase analysis completed")
print(summary)