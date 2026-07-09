from pathlib import Path
import pandas as pd

# Setting up directories relative to this script's location
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Starting the data cleaning process...")

# --- 1. CLEANING NAV HISTORY ---
try:
    print("Processing: 02_nav_history.csv...")
    nav_df = pd.read_csv(DATA_DIR / "02_nav_history.csv")
    nav_df["date"] = pd.to_datetime(nav_df["date"])
    nav_df = nav_df.sort_values(by=["amfi_code", "date"])
    nav_df["nav"] = nav_df.groupby("amfi_code")["nav"].ffill()
    nav_df = nav_df.drop_duplicates()
    nav_df = nav_df[nav_df["nav"] > 0]
    nav_df.to_csv(PROCESSED_DIR / "nav_history_clean.csv", index=False)
    print(" -> Successfully cleaned NAV History!")
except Exception as e:
    print(f" -> Error processing NAV history: {e}")

# --- 2. CLEANING INVESTOR TRANSACTIONS ---
try:
    print("Processing: 08_investor_transactions.csv...")
    tx_df = pd.read_csv(DATA_DIR / "08_investor_transactions.csv")
    tx_df["transaction_date"] = pd.to_datetime(tx_df["transaction_date"])
    # Clean up categories
    tx_df["transaction_type"] = tx_df["transaction_type"].str.strip().str.upper()
    tx_df["kyc_status"] = tx_df["kyc_status"].str.strip().str.capitalize()
    # Remove negative or zero transaction amounts
    tx_df = tx_df[tx_df["amount_inr"] > 0]
    tx_df.to_csv(PROCESSED_DIR / "investor_transactions_clean.csv", index=False)
    print(" -> Successfully cleaned Investor Transactions!")
except Exception as e:
    print(f" -> Error processing Transactions: {e}")

# --- 3. CLEANING SCHEME PERFORMANCE ---
try:
    print("Processing: 07_scheme_performance.csv...")
    perf_df = pd.read_csv(DATA_DIR / "07_scheme_performance.csv")
    # Turn return profiles into numeric columns
    for col in ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct"]:
        if col in perf_df.columns:
            perf_df[col] = pd.to_numeric(perf_df[col], errors="coerce")
    
    # Enforce valid expense ratio limits (0.1% to 2.5%)
    if "expense_ratio_pct" in perf_df.columns:
        perf_df["expense_ratio_pct"] = pd.to_numeric(perf_df["expense_ratio_pct"], errors="coerce")
        perf_df = perf_df[(perf_df["expense_ratio_pct"] >= 0.1) & (perf_df["expense_ratio_pct"] <= 2.5)]
    
    perf_df.to_csv(PROCESSED_DIR / "scheme_performance_clean.csv", index=False)
    print(" -> Successfully cleaned Scheme Performance!")
except Exception as e:
    print(f" -> Error processing Performance: {e}")

print("\n🚀 All done! Check your 'data/processed' folder to see your clean files.")