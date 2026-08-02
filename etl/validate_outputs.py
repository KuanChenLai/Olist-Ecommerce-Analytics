"""Validate the analytical outputs used by SQLite and Power BI."""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def close_enough(left, right, tolerance=0.01):
    return abs(float(left) - float(right)) <= tolerance


def main():
    fact_orders = pd.read_csv(PROCESSED_DIR / "fact_orders.csv")
    customer_summary = pd.read_csv(PROCESSED_DIR / "customer_summary.csv")
    monthly_revenue = pd.read_csv(PROCESSED_DIR / "monthly_revenue.csv")
    top_categories = pd.read_csv(PROCESSED_DIR / "top_categories.csv")
    top_sellers = pd.read_csv(PROCESSED_DIR / "top_sellers.csv")
    rfm_segments = pd.read_csv(PROCESSED_DIR / "rfm_segments.csv")
    rfm_summary = pd.read_csv(PROCESSED_DIR / "rfm_summary.csv")

    revenue = fact_orders["price"].sum()
    customer_count = customer_summary["customer_unique_id"].nunique()

    checks = {
        "fact_orders contains delivered orders only":
            set(fact_orders["order_status"].dropna().unique()) == {"delivered"},
        "customer_summary is one row per customer":
            len(customer_summary) == customer_count,
        "rfm_segments is one row per customer":
            len(rfm_segments) == rfm_segments["customer_unique_id"].nunique(),
        "customer and RFM populations match":
            customer_count == rfm_segments["customer_unique_id"].nunique(),
        "RFM segment customers reconcile":
            int(rfm_summary["customers"].sum()) == customer_count,
        "RFM customer percentages equal 100%":
            close_enough(rfm_summary["customer_percentage"].sum(), 1, 1e-8),
        "RFM revenue percentages equal 100%":
            close_enough(rfm_summary["revenue_percentage"].sum(), 1, 1e-8),
        "monthly revenue reconciles":
            close_enough(monthly_revenue["price"].sum(), revenue),
        "category revenue reconciles":
            close_enough(top_categories["price"].sum(), revenue),
        "seller revenue reconciles":
            close_enough(top_sellers["price"].sum(), revenue),
        "RFM revenue reconciles":
            close_enough(rfm_summary["total_revenue"].sum(), revenue),
    }

    for description, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {description}")

    failed = [description for description, passed in checks.items() if not passed]
    if failed:
        raise SystemExit(f"Validation failed: {', '.join(failed)}")

    orders = fact_orders["order_id"].nunique()
    print()
    print(f"Revenue: R${revenue:,.2f}")
    print(f"Orders: {orders:,}")
    print(f"Customers: {customer_count:,}")
    print(f"Average order value: R${revenue / orders:,.2f}")


if __name__ == "__main__":
    main()
