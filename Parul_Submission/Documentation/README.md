# Bluestock Mutual Fund Power BI Report

This folder contains a Power BI report blueprint and the cleaned source data that can be imported into Power BI Desktop.

## Source files
- data/01_fund_master.csv
- data/processed/nav_history_clean.csv
- data/processed/investor_transactions_clean.csv
- data/processed/scheme_performance_clean.csv
- bluestock_mf.db

## Expected report pages
1. Industry Overview
2. Fund Performance
3. Investor Analytics
4. SIP & Market Trends
5. NAV Detail

## Notes
- Relationships should be created on amfi_code and date.
- The report is designed to use the existing cleaned CSVs and SQLite database.
