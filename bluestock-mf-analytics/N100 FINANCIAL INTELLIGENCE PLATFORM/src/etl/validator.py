"""Data quality validator implementing DQ-01 .. DQ-16 (stubs)

The module exposes `run_all_rules(db_path)` which writes `output/validation_failures.csv`.
Each rule returns a list of dicts with keys: rule_id, table, row_id, severity, message
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"


def dq_01_pk_uniqueness(conn):
    # DQ-01: PK uniqueness for `companies`
    cur = conn.cursor()
    failures = []
    try:
        cur.execute(
            "SELECT company_id, COUNT(*) as cnt FROM companies GROUP BY company_id HAVING cnt>1"
        )
        for row in cur.fetchall():
            failures.append({
                "rule_id": "DQ-01",
                "table": "companies",
                "row_id": row[0],
                "severity": "CRITICAL",
                "message": f"Duplicate company_id {row[0]} ({row[1]} occurrences)",
            })
    except Exception:
        pass
    return failures


def dq_02_company_year_pk(conn):
    # DQ-02: (company_id, year) uniqueness in profitandloss, balancesheet, cashflow
    failures = []
    cur = conn.cursor()
    for tbl in ("profitandloss", "balancesheet", "cashflow"):
        try:
            cur.execute(
                f"SELECT company_id||'|'||year as keyval, COUNT(*) as cnt FROM {tbl} GROUP BY company_id, year HAVING cnt>1"
            )
            for r in cur.fetchall():
                failures.append({
                    "rule_id": "DQ-02",
                    "table": tbl,
                    "row_id": r[0],
                    "severity": "CRITICAL",
                    "message": f"Duplicate (company_id, year) in {tbl}: {r[0]} ({r[1]} occurrences)",
                })
        except Exception:
            continue
    return failures


def dq_03_fk_integrity(conn):
    # DQ-03: Foreign key integrity (use PRAGMA foreign_key_check)
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA foreign_key_check;")
        for r in cur.fetchall():
            # PRAGMA foreign_key_check returns (table, rowid, parent)
            failures.append({
                "rule_id": "DQ-03",
                "table": r[0],
                "row_id": r[1],
                "severity": "CRITICAL",
                "message": f"Foreign key check failed referencing {r[2]}",
            })
    except Exception:
        pass
    return failures


def dq_04_balance_sheet_balance(conn):
    # DQ-04: Balance sheet balance check: assets vs liabilities within 1%
    failures = []
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT company_id, year, total_assets, total_liabilities FROM balancesheet WHERE total_assets IS NOT NULL AND total_liabilities IS NOT NULL"
        )
        for company_id, year, assets, liabilities in cur.fetchall():
            denom = max(abs(assets), 1)
            if abs(assets - liabilities) / denom > 0.01:
                failures.append({
                    "rule_id": "DQ-04",
                    "table": "balancesheet",
                    "row_id": f"{company_id}|{year}",
                    "severity": "WARNING",
                    "message": f"Assets and liabilities diverge by more than 1% (assets={assets}, liabilities={liabilities})",
                })
    except Exception:
        pass
    return failures


def dq_05_opm_crosscheck(conn):
    # DQ-05: OPM plausibility: check opm is within reasonable bounds and consistent with sales
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT company_id, year, sales, opm FROM profitandloss WHERE opm IS NOT NULL")
        for company_id, year, sales, opm in cur.fetchall():
            if opm is None:
                continue
            # OPM outside -500%..500% flagged
            if abs(opm) > 500:
                failures.append({
                    "rule_id": "DQ-05",
                    "table": "profitandloss",
                    "row_id": f"{company_id}|{year}",
                    "severity": "WARNING",
                    "message": f"Unreasonable OPM {opm} for {company_id} {year}",
                })
    except Exception:
        pass
    return failures


def dq_06_positive_sales(conn):
    # DQ-06: Sales must be positive
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT company_id, year, sales FROM profitandloss WHERE sales IS NOT NULL AND sales<=0")
        for company_id, year, sales in cur.fetchall():
            failures.append({
                "rule_id": "DQ-06",
                "table": "profitandloss",
                "row_id": f"{company_id}|{year}",
                "severity": "CRITICAL",
                "message": f"Non-positive sales {sales}",
            })
    except Exception:
        pass
    return failures


def dq_07_net_cash_check(conn):
    # DQ-07: net cash reasonable (flag very negative values)
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT company_id, year, net_cash FROM cashflow WHERE net_cash IS NOT NULL")
        for company_id, year, net_cash in cur.fetchall():
            if net_cash < -1e8:  # arbitrary large negative threshold
                failures.append({
                    "rule_id": "DQ-07",
                    "table": "cashflow",
                    "row_id": f"{company_id}|{year}",
                    "severity": "WARNING",
                    "message": f"Very large negative net cash {net_cash}",
                })
    except Exception:
        pass
    return failures


def dq_08_tax_rate_range(conn):
    # DQ-08: tax rate within 0..100 if available in analysis.metric='tax_rate'
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT company_id, year, value FROM analysis WHERE metric='tax_rate' AND value IS NOT NULL")
        for company_id, year, value in cur.fetchall():
            if value < 0 or value > 100:
                failures.append({
                    "rule_id": "DQ-08",
                    "table": "analysis",
                    "row_id": f"{company_id}|{year}",
                    "severity": "WARNING",
                    "message": f"Tax rate out of bounds: {value}",
                })
    except Exception:
        pass
    return failures


def dq_09_dividend_payout_cap(conn):
    # DQ-09: dividend payout should not exceed a cap (e.g., 100%)
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT company_id, year, value FROM analysis WHERE metric='dividend_payout' AND value IS NOT NULL")
        for company_id, year, value in cur.fetchall():
            if value > 200:
                failures.append({
                    "rule_id": "DQ-09",
                    "table": "analysis",
                    "row_id": f"{company_id}|{year}",
                    "severity": "CRITICAL",
                    "message": f"Dividend payout unusually high: {value}%",
                })
    except Exception:
        pass
    return failures


def dq_10_url_valid(conn):
    # DQ-10: document URLs should be valid (basic check: start with http)
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT doc_id, url FROM documents WHERE url IS NOT NULL")
        for doc_id, url in cur.fetchall():
            if not str(url).lower().startswith("http"):
                failures.append({
                    "rule_id": "DQ-10",
                    "table": "documents",
                    "row_id": doc_id,
                    "severity": "WARNING",
                    "message": f"Document URL does not appear valid: {url}",
                })
    except Exception:
        pass
    return failures


def dq_11_eps_sign_consistency(conn):
    # DQ-11: EPS sign vs profitability (if EPS negative while sales and opm strongly positive)
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT company_id, year, ratio_value FROM financial_ratios WHERE ratio_name='EPS' AND ratio_value IS NOT NULL")
        eps_rows = cur.fetchall()
        for company_id, year, eps in eps_rows:
            cur.execute(
                "SELECT sales, opm FROM profitandloss WHERE company_id=? AND year=?",
                (company_id, year),
            )
            r = cur.fetchone()
            if r:
                sales, opm = r
                if eps < 0 and sales and opm and opm > 0:
                    failures.append({
                        "rule_id": "DQ-11",
                        "table": "financial_ratios",
                        "row_id": f"{company_id}|{year}",
                        "severity": "WARNING",
                        "message": f"Negative EPS {eps} despite positive sales/opm",
                    })
    except Exception:
        pass
    return failures


def dq_12_bse_balance_flag(conn):
    # DQ-12: placeholder for BSE balance check — flag companies with missing stock_prices
    failures = []
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT c.company_id FROM companies c LEFT JOIN stock_prices s ON c.company_id=s.company_id WHERE s.company_id IS NULL"
        )
        for (company_id,) in cur.fetchall():
            failures.append({
                "rule_id": "DQ-12",
                "table": "stock_prices",
                "row_id": company_id,
                "severity": "WARNING",
                "message": "No stock price rows found (possible BSE listing missing)",
            })
    except Exception:
        pass
    return failures


def dq_13_year_coverage(conn):
    # DQ-13: coverage — companies should have at least 5 years of P&L
    failures = []
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT c.company_id, COUNT(p.year) as years FROM companies c LEFT JOIN profitandloss p ON c.company_id=p.company_id GROUP BY c.company_id HAVING years<5"
        )
        for company_id, years in cur.fetchall():
            failures.append({
                "rule_id": "DQ-13",
                "table": "profitandloss",
                "row_id": company_id,
                "severity": "WARNING",
                "message": f"Insufficient year coverage: {years} years",
            })
    except Exception:
        pass
    return failures


def dq_14_duplicate_documents(conn):
    # DQ-14: duplicate document URLs
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT url, COUNT(*) as cnt FROM documents WHERE url IS NOT NULL GROUP BY url HAVING cnt>1")
        for url, cnt in cur.fetchall():
            failures.append({
                "rule_id": "DQ-14",
                "table": "documents",
                "row_id": url,
                "severity": "WARNING",
                "message": f"Duplicate document URL ({cnt} occurrences)",
            })
    except Exception:
        pass
    return failures


def dq_15_peer_group_selfref(conn):
    # DQ-15: peer_groups should not reference the same company
    failures = []
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, company_id FROM peer_groups WHERE company_id=peer_company_id")
        for id_, company_id in cur.fetchall():
            failures.append({
                "rule_id": "DQ-15",
                "table": "peer_groups",
                "row_id": id_,
                "severity": "WARNING",
                "message": "Peer group references itself",
            })
    except Exception:
        pass
    return failures


def dq_16_misc_coverage(conn):
    # DQ-16: miscellaneous placeholder checks (no-op when no data)
    return []


# Placeholder stubs for other rules — real implementations should query DB
RULES = [
    dq_01_pk_uniqueness,
    dq_02_company_year_pk,
    dq_03_fk_integrity,
    dq_04_balance_sheet_balance,
    dq_05_opm_crosscheck,
    dq_06_positive_sales,
    dq_07_net_cash_check,
    dq_08_tax_rate_range,
    dq_09_dividend_payout_cap,
    dq_10_url_valid,
    dq_11_eps_sign_consistency,
    dq_12_bse_balance_flag,
    dq_13_year_coverage,
    dq_14_duplicate_documents,
    dq_15_peer_group_selfref,
    dq_16_misc_coverage,
]


def write_failures(failures):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    out = OUTPUT / "validation_failures.csv"
    with open(out, "w", encoding="utf-8") as f:
        f.write("rule_id,table,row_id,severity,message\n")
        for r in failures:
            f.write(f"{r['rule_id']},{r['table']},{r['row_id']},{r['severity']},\"{r['message']}\"\n")
    print(f"Wrote validation failures to {out}")


def run_all_rules(db_path: str = None):
    db = db_path or ROOT / "nifty100.db"
    conn = sqlite3.connect(str(db))
    conn.execute("PRAGMA foreign_keys = ON;")
    all_failures = []
    for rule in RULES:
        all_failures.extend(rule(conn))
    write_failures(all_failures)
    conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="Path to SQLite DB", default=str(ROOT / "nifty100.db"))
    args = parser.parse_args()
    run_all_rules(args.db)
