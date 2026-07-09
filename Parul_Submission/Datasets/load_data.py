from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "bluestock_mf.db"
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

print(f"Connecting to {DB_PATH}...")
engine = create_engine(f"sqlite:///{DB_PATH}")

# Dictionary mapping our cleaned files to their corresponding database tables
# Use paths relative to the project root so the script works from any directory.
data_to_load = {
    DATA_DIR / "01_fund_master.csv": "dim_fund",
    PROCESSED_DIR / "nav_history_clean.csv": "fact_nav",
    PROCESSED_DIR / "investor_transactions_clean.csv": "fact_transactions",
    PROCESSED_DIR / "scheme_performance_clean.csv": "fact_performance",
}

print("\nStarting the data migration phase...")

for file_path, table_name in data_to_load.items():
    try:
        print(f"Reading {file_path}...")
        df = pd.read_csv(file_path)

        print(f" -> Pushing data into database table: '{table_name}'...")
        df.to_sql(table_name, con=engine, if_exists="append", index=False)

        print(f" -> Success! Verified row count loaded: {len(df)} rows.")

    except Exception as e:
        print(f" ❌ Error loading {file_path}: {e}")

print("\n🎉 Excellent work! All available datasets have been securely loaded into your SQLite database.")