"""Run the complete Olist analytics pipeline in dependency order."""

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PIPELINE = [
    "etl/clean_data.py",
    "etl/build_fact_orders.py",
    "notebooks/04_revenue_analysis.py",
    "notebooks/05_monthly_revenue.py",
    "notebooks/06_top_sellers.py",
    "notebooks/07_customer_summary.py",
    "notebooks/08_repeat_purchase_analysis.py",
    "notebooks/09_rfm_analysis.py",
    "etl/load_to_sqlite.py",
]


def main():
    for relative_script in PIPELINE:
        script = BASE_DIR / relative_script
        print(f"\n=== Running {relative_script} ===", flush=True)
        subprocess.run(
            [sys.executable, str(script)],
            cwd=BASE_DIR,
            check=True,
        )

    print("\nPipeline completed; SQLite is ready for Power BI refresh.")


if __name__ == "__main__":
    main()
