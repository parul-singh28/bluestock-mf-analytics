-- 10 exploratory SQL queries for nifty100.db

-- 1. Count companies
SELECT COUNT(*) AS company_count FROM companies;

-- 2. Row counts per table
SELECT name, (SELECT COUNT(*) FROM sqlite_master WHERE type='table') FROM sqlite_master WHERE type='table';

-- 3. Companies with <5 years of data (P&L)
SELECT c.company_id, c.name, COUNT(p.year) as years
FROM companies c
LEFT JOIN profitandloss p ON c.company_id = p.company_id
GROUP BY c.company_id
HAVING years < 5
ORDER BY years ASC;

-- 4. Financial ratios sample
SELECT * FROM financial_ratios LIMIT 20;

-- 5. Latest stock price per company
SELECT company_id, MAX(trade_date) as last_date FROM stock_prices GROUP BY company_id;

-- 6. Balance sheet sanity check: assets vs liabilities
SELECT company_id, year, total_assets, total_liabilities, (total_assets - total_liabilities) as equity FROM balancesheet ORDER BY company_id LIMIT 50;

-- 7. Profitability: average OPM by sector
SELECT s.sector_name, AVG(p.opm) as avg_opm FROM profitandloss p JOIN companies c ON p.company_id=c.company_id JOIN sectors s ON c.sector_id=s.sector_id GROUP BY s.sector_name ORDER BY avg_opm DESC;

-- 8. Companies missing documents
SELECT c.company_id, c.name FROM companies c LEFT JOIN documents d ON c.company_id=d.company_id WHERE d.doc_id IS NULL;

-- 9. Peer groups sizes
SELECT peer_company_id, COUNT(*) as member_count FROM peer_groups GROUP BY peer_company_id ORDER BY member_count DESC LIMIT 20;

-- 10. Companies with negative net cash (potential red flag)
SELECT company_id, year, net_cash FROM cashflow WHERE net_cash < 0 ORDER BY net_cash ASC LIMIT 50;
