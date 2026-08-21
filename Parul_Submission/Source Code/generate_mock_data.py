from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("Generating mock dataset files for your capstone project...")

    # 1. 01_fund_master.csv
    fund_master = pd.DataFrame({
        'amfi_code': ['125497', '102345', '145678'],
        'fund_house': ['HDFC Mutual Fund', 'SBI Mutual Fund', 'Axis Mutual Fund'],
        'scheme_name': ['HDFC Top 100 Direct', 'SBI Bluechip Fund', 'Axis Midcap Fund'],
        'category': ['Equity', 'Equity', 'Equity'],
        'sub_category': ['Large Cap', 'Large Cap', 'Mid Cap'],
        'plan': ['Direct', 'Regular', 'Direct'],
        'launch_date': ['2013-01-01', '2006-02-14', '2011-11-27'],
        'benchmark': ['NIFTY 100 TRI', 'S&P BSE 100 TRI', 'NIFTY Midcap 150 TRI'],
        'expense_ratio_pct': [1.05, 1.65, 0.55],
        'exit_load_pct': [1.0, 1.0, 1.0],
        'fund_manager': ['Rahul Baijal', 'Sohini Andani', 'Shreyash Devalkar'],
        'risk_category': ['Very High', 'Very High', 'Very High'],
        'sebi_category_code': ['EC01', 'EC01', 'EC03']
    })
    fund_master.to_csv(DATA_DIR / "01_fund_master.csv", index=False)

    # 2. 02_nav_history.csv
    dates = [datetime(2026, 6, 1) + timedelta(days=i) for i in range(10)]
    nav_history = pd.DataFrame({
        'amfi_code': ['125497'] * 10 + ['102345'] * 10 + ['145678'] * 10,
        'date': [d.strftime('%Y-%m-%d') for d in dates] * 3,
        'nav': list(np.random.uniform(500, 600, 10)) + list(np.random.uniform(50, 70, 10)) + list(np.random.uniform(80, 100, 10))
    })
    # Inject a couple of missing rows/bad rows to give your cleaning script some work!
    nav_history.loc[5, 'nav'] = np.nan
    nav_history.loc[12, 'nav'] = -10.5
    nav_history.to_csv(DATA_DIR / "02_nav_history.csv", index=False)

    # 3. 04_monthly_sip_inflows.csv
    sip_inflows = pd.DataFrame({
        'month': ['2026-01', '2026-02', '2026-03'],
        'sip_inflow_crore': [21000.50, 21500.75, 22000.20],
        'active_sip_accounts_crore': [8.2, 8.4, 8.6],
        'new_sip_accounts_lakh': [45.2, 47.1, 50.5],
        'sip_aum_lakh_crore': [13.5, 13.8, 14.2],
        'yoy_growth_pct': [15.2, 16.1, 17.5]
    })
    sip_inflows.to_csv(DATA_DIR / "04_monthly_sip_inflows.csv", index=False)

    # 4. 07_scheme_performance.csv
    performance = pd.DataFrame({
        'amfi_code': ['125497', '102345', '145678'],
        'return_1yr_pct': [18.5, 14.2, 22.1],
        'return_3yr_pct': [15.3, 12.1, 19.4],
        'return_5yr_pct': [14.1, 11.5, 17.2],
        'benchmark_3yr_pct': [14.0, 14.0, 18.0],
        'alpha': [1.3, -1.9, 1.4],
        'beta': [0.95, 0.88, 1.02],
        'sharpe_ratio': [1.2, 0.85, 1.45],
        'sortino_ratio': [1.5, 0.95, 1.8],
        'std_dev_ann_pct': [12.5, 11.2, 14.1],
        'max_drawdown_pct': [-15.2, -18.4, -13.5],
        'morningstar_rating': [4, 3, 5],
        'expense_ratio_pct': [1.05, 1.65, 0.55]  # added to match validation logic
    })
    performance.to_csv(DATA_DIR / "07_scheme_performance.csv", index=False)

    # 5. 08_investor_transactions.csv
    investor_tx = pd.DataFrame({
        'investor_id': ['INV000001', 'INV000002', 'INV000003'],
        'transaction_date': ['2026-06-15', '2026-06-16', '2026-06-17'],
        'amfi_code': ['125497', '102345', '145678'],
        'transaction_type': ['sip ', 'Lumpsum', 'Redemption'],  # purposely left a space in 'sip ' to test cleaning
        'amount_inr': [5000, 50000, -1000],  # negative to catch bad records
        'state': ['Delhi', 'Maharashtra', 'Karnataka'],
        'city': ['New Delhi', 'Mumbai', 'Bengaluru'],
        'city_tier': ['T30', 'T30', 'T30'],
        'age_group': ['26-35', '36-45', '18-25'],
        'gender': ['Female', 'Male', 'Female'],
        'annual_income_lakh': [12.5, 24.0, 6.5],
        'payment_mode': ['UPI', 'Net Banking', 'Mandate'],
        'kyc_status': ['verified', 'pending', 'verified']
    })
    investor_tx.to_csv(DATA_DIR / "08_investor_transactions.csv", index=False)

    print(f"🎉 Mock files successfully created in {DATA_DIR}!")


if __name__ == "__main__":
    main()