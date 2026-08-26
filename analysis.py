import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).parent
RAW_FILE = BASE_DIR / "orders.csv"

# Extract: load the raw CSV file.
orders = pd.read_csv(RAW_FILE)
print("Raw rows:", len(orders))
print("\nMissing values before cleaning:")
print(orders.isna().sum())

# Transform: remove duplicate orders and clean required fields.
orders = orders.drop_duplicates(subset="order_id").copy()
orders["quantity"] = pd.to_numeric(orders["quantity"], errors="coerce")
orders["unit_price"] = pd.to_numeric(orders["unit_price"], errors="coerce")
orders["discount"] = pd.to_numeric(orders["discount"], errors="coerce").fillna(0)
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
orders = orders.dropna(subset=["customer", "category", "region", "quantity", "unit_price", "order_date"])
orders["revenue"] = orders["quantity"] * orders["unit_price"] * (1 - orders["discount"])

# Load: save the cleaned data for reuse.
clean_file = BASE_DIR / "clean_orders.csv"
orders.to_csv(clean_file, index=False)

# SQL analysis: use SQLite to answer business questions.
connection = sqlite3.connect(":memory:")
orders.to_sql("orders", connection, index=False)

queries_file = BASE_DIR / "queries.sql"
sql_text = queries_file.read_text(encoding="utf-8")
queries = [
    query.strip()
    for query in sql_text.split(";")
    if "SELECT" in query.upper()
]

category_summary = pd.read_sql_query(queries[0], connection)
region_summary = pd.read_sql_query(queries[1], connection)
average_order_value = pd.read_sql_query(queries[2], connection)

print("\nClean rows:", len(orders))
print("Average order value:", average_order_value.loc[0, "average_order_value"])
print("\nRevenue by category:")
print(category_summary)
print("\nRevenue by region:")
print(region_summary)

category_summary.to_csv(BASE_DIR / "category_summary.csv", index=False)
region_summary.to_csv(BASE_DIR / "region_summary.csv", index=False)

# EDA: create charts that make the summaries easy to compare.
plt.figure(figsize=(7, 4))
plt.bar(category_summary["category"], category_summary["total_revenue"])
plt.title("Revenue by Category")
plt.xlabel("Category")
plt.ylabel("Revenue")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(BASE_DIR / "revenue_by_category.png")
plt.close()

plt.figure(figsize=(7, 4))
plt.bar(region_summary["region"], region_summary["total_revenue"], color="darkorange")
plt.title("Revenue by Region")
plt.xlabel("Region")
plt.ylabel("Revenue")
plt.tight_layout()
plt.savefig(BASE_DIR / "revenue_by_region.png")
plt.close()

connection.close()
print("\nCreated: clean_orders.csv, category_summary.csv, region_summary.csv")
print("Created: revenue_by_category.png, revenue_by_region.png")
