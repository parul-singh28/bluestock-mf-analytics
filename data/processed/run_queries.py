from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "bluestock_mf.db"

conn = sqlite3.connect(DB_PATH)

print("--- Testing Query 2: Transaction Breakdown by State ---")
query = """
SELECT state, COUNT(*) AS total_transactions, SUM(amount_inr) AS total_amount_invested
FROM fact_transactions GROUP BY state ORDER BY total_amount_invested DESC;
"""
df = pd.read_sql_query(query, conn)
print(df)

conn.close()