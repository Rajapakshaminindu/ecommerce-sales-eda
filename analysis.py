import sqlite3
from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).parent
RAW_FILE = BASE_DIR / "orders.csv"
QUERIES_FILE = BASE_DIR / "queries.sql"


def load_data(file_path: Path | str) -> pd.DataFrame:
    """Load raw order data from CSV file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean order data:
    - Deduplicate by order_id
    - Coerce numeric and datetime fields
    - Impute missing discount values with 0
    - Drop rows missing mandatory fields
    - Calculate net revenue: quantity * unit_price * (1 - discount)
    """
    cleaned = df.drop_duplicates(subset="order_id").copy()
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["unit_price"] = pd.to_numeric(cleaned["unit_price"], errors="coerce")
    cleaned["discount"] = pd.to_numeric(cleaned["discount"], errors="coerce").fillna(0.0)
    cleaned["order_date"] = pd.to_datetime(cleaned["order_date"], errors="coerce")

    required_cols = ["customer", "category", "region", "quantity", "unit_price", "order_date"]
    cleaned = cleaned.dropna(subset=required_cols)
    cleaned["revenue"] = cleaned["quantity"] * cleaned["unit_price"] * (1 - cleaned["discount"])
    return cleaned


def run_sql_analysis(
    orders: pd.DataFrame,
    queries_file: Path | str,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Execute SQL business queries against an in-memory SQLite table."""
    connection = sqlite3.connect(":memory:")
    orders.to_sql("orders", connection, index=False)

    sql_text = Path(queries_file).read_text(encoding="utf-8")
    queries = [
        query.strip()
        for query in sql_text.split(";")
        if "SELECT" in query.upper()
    ]

    category_summary = pd.read_sql_query(queries[0], connection)
    region_summary = pd.read_sql_query(queries[1], connection)
    average_order_value = pd.read_sql_query(queries[2], connection)

    connection.close()
    return category_summary, region_summary, average_order_value


def calculate_statistics(orders: pd.DataFrame) -> Dict[str, float]:
    """Compute summary statistics for order revenue."""
    return {
        "mean": round(float(orders["revenue"].mean()), 2),
        "median": round(float(orders["revenue"].median()), 2),
        "min": round(float(orders["revenue"].min()), 2),
        "max": round(float(orders["revenue"].max()), 2),
        "std": round(float(orders["revenue"].std()), 2),
    }


def save_visualizations(
    category_summary: pd.DataFrame,
    region_summary: pd.DataFrame,
    output_dir: Path | str,
) -> None:
    """Generate and save EDA bar charts."""
    out_path = Path(output_dir)

    plt.figure(figsize=(7, 4))
    plt.bar(category_summary["category"], category_summary["total_revenue"])
    plt.title("Revenue by Category")
    plt.xlabel("Category")
    plt.ylabel("Revenue")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(out_path / "revenue_by_category.png")
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.bar(region_summary["region"], region_summary["total_revenue"], color="yellow")
    plt.title("Revenue by Region")
    plt.xlabel("Region")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(out_path / "revenue_by_region.png")
    plt.close()


def main() -> None:
    """Orchestrate the ETL and EDA analysis pipeline."""
    # Extract
    raw_orders = load_data(RAW_FILE)
    print("Raw rows:", len(raw_orders))
    print("\nMissing values before cleaning:")
    print(raw_orders.isna().sum())

    # Transform
    orders = clean_data(raw_orders)
    print("\nClean rows:", len(orders))

    # Load cleaned data
    clean_file = BASE_DIR / "clean_orders.csv"
    orders.to_csv(clean_file, index=False)

    # SQL Analysis
    category_summary, region_summary, average_order_value = run_sql_analysis(
        orders, QUERIES_FILE
    )

    print("Average order value:", average_order_value.loc[0, "average_order_value"])
    print("\nRevenue by category:")
    print(category_summary)
    print("\nRevenue by region:")
    print(region_summary)

    category_summary.to_csv(BASE_DIR / "category_summary.csv", index=False)
    region_summary.to_csv(BASE_DIR / "region_summary.csv", index=False)

    # EDA Visualizations
    save_visualizations(category_summary, region_summary, BASE_DIR)
    print("\nCreated: clean_orders.csv, category_summary.csv, region_summary.csv")
    print("Created: revenue_by_category.png, revenue_by_region.png")

    # Statistics
    stats = calculate_statistics(orders)
    print("\nStatistics:")
    print("Mean revenue:", stats["mean"])
    print("Median revenue:", stats["median"])
    print("Minimum revenue:", stats["min"])
    print("Maximum revenue:", stats["max"])
    print("Revenue standard deviation:", stats["std"])


if __name__ == "__main__":
    main()