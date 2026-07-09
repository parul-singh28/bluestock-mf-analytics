-- Query 1: Average NAV calculation grouped by fund scheme
SELECT 
    amfi_code,
    AVG(nav) AS average_nav
FROM fact_nav
GROUP BY amfi_code;

-- Query 2: Breakdown of transactions mapped out by individual states
SELECT 
    state,
    COUNT(*) AS total_transactions,
    SUM(amount_inr) AS total_amount_invested
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_invested DESC;

-- Query 3: Comprehensive list of mutual funds keeping their expense ratio strictly below 1%
SELECT 
    amfi_code,
    scheme_name,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0;

-- Query 4: Total amount invested grouped by Gender profile
SELECT 
    gender,
    COUNT(*) AS transaction_count,
    SUM(amount_inr) AS total_volume
FROM fact_transactions
GROUP BY gender;

-- Query 5: Average investor age segment distribution for transactions
SELECT 
    age_group,
    COUNT(*) AS total_investors
FROM fact_transactions
GROUP BY age_group
ORDER BY total_investors DESC;