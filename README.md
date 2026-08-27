# E-commerce Sales Analysis

A beginner portfolio project combining Python, Pandas, data cleaning, SQL, and exploratory data analysis (EDA).

## Business questions
- Which category generates the most revenue?
- Which region generates the most revenue?
- What is the average order value?

## Workflow
1. Load raw order data with Pandas.
2. Inspect missing values.
3. Remove duplicate orders.
4. Convert numeric and date columns.
5. Fill missing discounts with zero.
6. Remove rows missing required fields.
7. Calculate discounted revenue.
8. Run SQL summaries with SQLite.
9. Save cleaned outputs and EDA charts.

## Run the project
Open a terminal in this folder and run:

```powershell
python analysis.py
```

If your Python command is not `python`, use the full interpreter command configured in VS Code.

## Files
- `orders.csv` - raw input data
- `analysis.py` - cleaning, SQL, and EDA pipeline
- `queries.sql` - SQL questions used in the analysis
- `requirements.txt` - external Python packages
- generated CSV files - cleaned data and summaries
- generated PNG files - EDA charts

## Skills demonstrated
- Pandas DataFrames
- Data Cleansing
- missing-value handling
- duplicate removal
- feature creation
- SQL `GROUP BY`, `SUM`, `AVG`, and `ORDER BY`
- business-focused EDA
- Matplotlib charts
