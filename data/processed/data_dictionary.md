# Bluestock Mutual Fund Analytics Data Dictionary

## 1. dim_fund (Dimension Table)
Contains master configurations for all tracking mutual fund schemes.

| Column Name | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | TEXT | Primary Key | AMFI unique identifier code for the scheme |
| `fund_house` | TEXT | None | Name of the Asset Management Company (AMC) |
| `scheme_name` | TEXT | None | Official registered fund scheme title |
| `category` | TEXT | None | Asset allocation type (Equity, Debt, Hybrid) |
| `expense_ratio_pct` | REAL | None | Annualized operation fees charged in percentage |

## 2. fact_transactions (Fact Table)
Stores absolute granular records of investor transaction footprints.

| Column Name | Data Type | Key Type | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | Primary Key | Auto-incrementing identifier |
| `investor_id` | TEXT | None | Unique masked consumer identification |
| `amfi_code` | TEXT | Foreign Key | Maps structural properties back to `dim_fund` |
| `transaction_type`| TEXT | None | Standardized method (SIP, Lumpsum, Redemption) |
| `amount_inr` | INTEGER | None | Monetary transaction volume in Indian Rupees |
| `state` | TEXT | None | Registered residential geographic state |