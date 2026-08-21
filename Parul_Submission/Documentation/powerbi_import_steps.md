# Power BI Desktop import steps

1. Open Power BI Desktop.
2. Choose Get data > Excel.
3. Select powerbi_report/data/bluestock_powerbi_data.xlsx.
4. Import the four sheets: dim_fund, fact_nav, fact_transactions, fact_performance.
5. In Model view, create relationships:
   - dim_fund[amfi_code] -> fact_nav[amfi_code]
   - dim_fund[amfi_code] -> fact_transactions[amfi_code]
   - dim_fund[amfi_code] -> fact_performance[amfi_code]
6. Create a date table if needed for monthly trend visuals.
7. Add the measures from dax_measures.txt.
8. Build the pages described in page_layout.json.
9. Use the Bluestock theme colors and add the logo to the report header.
10. Publish or export as PDF/PNG from Power BI Desktop.
