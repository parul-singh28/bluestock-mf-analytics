"""FastAPI application for the Nifty 100 financial intelligence platform."""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "nifty100.db"

SECTORS = [
    "Information Technology",
    "Financials",
    "FMCG",
    "Energy",
    "Healthcare",
    "Automobile",
    "Metals",
    "Infrastructure",
    "Consumer Durables",
    "Telecom",
    "Chemicals",
]

TICKERS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "ITC", "LT", "SBIN", "HINDUNILVR",
    "AXISBANK", "BAJFINANCE", "KOTAKBANK", "M&M", "SUNPHARMA", "MARUTI", "NTPC", "HCLTECH", "TITAN",
    "ULTRACEMCO", "TATAMOTORS", "POWERGRID", "ASIANPAINT", "BAJAJFINSV", "ONGC", "NESTLEIND", "COALINDIA",
    "WIPRO", "JSWSTEEL", "ADANIENT", "TATASTEEL", "TECHM", "GRASIM", "HINDALCO", "CIPLA", "DRREDDY",
    "BRITANNIA", "EICHERMOT", "DIVISLAB", "APOLLOHOSP", "HEROMOTOCO", "BPCL", "TATACONSUM", "BAJAJ-AUTO",
    "INDUSINDBK", "ADANIPORTS", "SHRIRAMFIN", "HDFCLIFE", "SBILIFE", "ICICIPRULI", "DLF", "PIDILITIND",
    "GODREJCP", "DABUR", "HAVELLS", "AMBUJACEM", "SIEMENS", "ABB", "VEDL", "BANKBARODA", "PNB", "CANBK",
    "UNIONBANK", "TVSMOTOR", "TRENT", "ZOMATO", "DMART", "NAUKRI", "IRCTC", "BEL", "HAL", "BHEL",
    "ADANIGREEN", "ADANIPOWER", "JIOFIN", "LTIM", "PERSISTENT", "OFSS", "MPHASIS", "LUPIN", "TORNTPHARM",
    "BIOCON", "MOTHERSON", "BOSCHLTD", "INDIGO", "GAIL", "IOC", "PETRONET", "COLPAL", "MARICO", "BERGEPAINT",
    "SHREECEM",
]

app = FastAPI(title="Nifty 100 Analytics API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


@app.middleware("http")
async def add_request_logging(request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed_ms = round((time.time() - start) * 1000, 2)
    print(f"{request.method} {request.url.path} {response.status_code} {elapsed_ms}ms")
    return response


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def seed_database():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS companies (company_id TEXT PRIMARY KEY, name TEXT, ticker TEXT, broad_sector TEXT, roe_percentage REAL, roce_percentage REAL, debt_to_equity REAL DEFAULT 0, free_cash_flow REAL DEFAULT 0, revenue_cagr_5yr REAL DEFAULT 0, pat_cagr_5yr REAL DEFAULT 0, pe_ratio REAL DEFAULT 0, pb_ratio REAL DEFAULT 0, market_cap REAL DEFAULT 0)"
    )
    conn.execute("CREATE TABLE IF NOT EXISTS profitandloss (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, year INTEGER, sales REAL, opm REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS balancesheet (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, year INTEGER, total_assets REAL, total_liabilities REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS cashflow (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, year INTEGER, net_cash REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS financial_ratios (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, year INTEGER, ratio_name TEXT, ratio_value REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, title TEXT, document_type TEXT, url TEXT)")

    company_columns = [row[1] for row in conn.execute("PRAGMA table_info(companies)").fetchall()]
    for column_name, column_type in {
        "debt_to_equity": "REAL DEFAULT 0",
        "free_cash_flow": "REAL DEFAULT 0",
        "revenue_cagr_5yr": "REAL DEFAULT 0",
        "pat_cagr_5yr": "REAL DEFAULT 0",
        "pe_ratio": "REAL DEFAULT 0",
        "pb_ratio": "REAL DEFAULT 0",
        "market_cap": "REAL DEFAULT 0",
    }.items():
        if column_name not in company_columns:
            conn.execute(f"ALTER TABLE companies ADD COLUMN {column_name} {column_type}")

    if conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
        for idx, ticker in enumerate(TICKERS[:92], start=1):
            sector = SECTORS[(idx - 1) % len(SECTORS)]
            name = ticker.replace("-", " ").title()
            roe = round(8 + ((idx * 7) % 22), 2)
            roce = round(roe + 3 + (idx % 5), 2)
            debt = round((idx % 8) * 0.35, 2)
            fcf = round(15 + idx * 2.3, 2)
            revenue_cagr = round(4 + (idx % 12) * 0.8, 2)
            pat_cagr = round(5 + (idx % 10) * 0.7, 2)
            pe = round(10 + (idx % 18) * 1.5, 2)
            pb = round(1.2 + (idx % 7) * 0.25, 2)
            market_cap = float(1000 + idx * 125)
            conn.execute(
                "INSERT INTO companies (company_id, name, ticker, broad_sector, roe_percentage, roce_percentage, debt_to_equity, free_cash_flow, revenue_cagr_5yr, pat_cagr_5yr, pe_ratio, pb_ratio, market_cap) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f"C{idx:03d}", name, ticker, sector, roe, roce, debt, fcf, revenue_cagr, pat_cagr, pe, pb, market_cap),
            )
            for year in range(2015, 2025):
                sales = 500 + idx * 120 + (year - 2015) * 45
                opm = 10 + (idx % 12)
                conn.execute(
                    "INSERT INTO profitandloss (company_id, year, sales, opm) VALUES (?, ?, ?, ?)",
                    (f"C{idx:03d}", year, sales, opm),
                )
                conn.execute(
                    "INSERT INTO balancesheet (company_id, year, total_assets, total_liabilities) VALUES (?, ?, ?, ?)",
                    (f"C{idx:03d}", year, sales * 1.5, sales * 0.7),
                )
                conn.execute(
                    "INSERT INTO cashflow (company_id, year, net_cash) VALUES (?, ?, ?)",
                    (f"C{idx:03d}", year, sales * 0.12),
                )
                conn.execute(
                    "INSERT INTO financial_ratios (company_id, year, ratio_name, ratio_value) VALUES (?, ?, ?, ?)",
                    (f"C{idx:03d}", year, "roe", roe),
                )
            conn.execute(
                "INSERT INTO documents (company_id, title, document_type, url) VALUES (?, ?, ?, ?)",
                (f"C{idx:03d}", f"Annual Report {idx}", "annual-report", f"https://example.com/{ticker.lower()}.pdf"),
            )
    conn.commit()
    conn.close()


seed_database()


@app.get("/api/v1/health")
def health():
    counts = {}
    if DB_PATH.exists():
        with get_db_connection() as conn:
            tables = [
                "analysis",
                "balancesheet",
                "cashflow",
                "companies",
                "documents",
                "financial_ratios",
                "peer_groups",
                "profitandloss",
                "prosandcons",
                "sectors",
                "stock_prices",
            ]
            for table in tables:
                try:
                    row = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                    counts[table] = row["count"] if row else 0
                except sqlite3.OperationalError:
                    counts[table] = 0
    return {
        "status": "ok",
        "db_row_counts": counts,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": app.version,
    }


@app.get("/api/v1/companies")
def list_companies(
    sector: str | None = None,
    market_cap_category: str | None = None,
    search: str | None = None,
):
    with get_db_connection() as conn:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(companies)").fetchall()]
    selected = [
        c for c in ["company_id", "name", "broad_sector", "ticker", "roe_percentage", "roce_percentage"]
        if c in columns
    ]
    if not selected:
        selected = columns[:]

    query = f"SELECT {', '.join(selected)} FROM companies"
    params = []
    clauses = []
    if sector:
        clauses.append("LOWER(COALESCE(broad_sector, '')) = LOWER(?)")
        params.append(sector)
    if search:
        clauses.append("(LOWER(COALESCE(company_id, '')) LIKE LOWER(?) OR LOWER(COALESCE(name, '')) LIKE LOWER(?) OR LOWER(COALESCE(ticker, '')) LIKE LOWER(?))")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    with get_db_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/v1/companies/{ticker}")
def get_company_profile(ticker: str):
    key = ticker.strip().upper()
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM companies WHERE UPPER(COALESCE(company_id, '')) = UPPER(?) OR UPPER(COALESCE(ticker, '')) = UPPER(?) OR UPPER(COALESCE(name, '')) = UPPER(?) LIMIT 1",
            (key, key, key),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return dict(row)


@app.get("/api/v1/companies/{ticker}/pl")
def get_company_pl(ticker: str, from_year: str | None = None, to_year: str | None = None):
    company_key = ticker.strip().upper()
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM profitandloss WHERE company_id = (SELECT company_id FROM companies WHERE UPPER(COALESCE(company_id, '')) = UPPER(?) OR UPPER(COALESCE(ticker, '')) = UPPER(?) LIMIT 1)",
            (company_key, company_key),
        ).fetchall()
    items = [dict(r) for r in rows]
    if from_year:
        items = [r for r in items if int(r["year"]) >= int(from_year[:4])]
    if to_year:
        items = [r for r in items if int(r["year"]) <= int(to_year[:4])]
    return {"ticker": company_key, "history": items}


@app.get("/api/v1/companies/{ticker}/bs")
def get_company_bs(ticker: str, from_year: str | None = None, to_year: str | None = None):
    company_key = ticker.strip().upper()
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM balancesheet WHERE company_id = (SELECT company_id FROM companies WHERE UPPER(COALESCE(company_id, '')) = UPPER(?) OR UPPER(COALESCE(ticker, '')) = UPPER(?) LIMIT 1)",
            (company_key, company_key),
        ).fetchall()
    items = [dict(r) for r in rows]
    if from_year:
        items = [r for r in items if int(r["year"]) >= int(from_year[:4])]
    if to_year:
        items = [r for r in items if int(r["year"]) <= int(to_year[:4])]
    return {"ticker": company_key, "history": items}


@app.get("/api/v1/companies/{ticker}/cashflow")
def get_company_cashflow(ticker: str, from_year: str | None = None, to_year: str | None = None):
    company_key = ticker.strip().upper()
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM cashflow WHERE company_id = (SELECT company_id FROM companies WHERE UPPER(COALESCE(company_id, '')) = UPPER(?) OR UPPER(COALESCE(ticker, '')) = UPPER(?) LIMIT 1)",
            (company_key, company_key),
        ).fetchall()
    items = [dict(r) for r in rows]
    if from_year:
        items = [r for r in items if int(r["year"]) >= int(from_year[:4])]
    if to_year:
        items = [r for r in items if int(r["year"]) <= int(to_year[:4])]
    return {"ticker": company_key, "history": items}


@app.get("/api/v1/companies/{ticker}/ratios")
def get_company_ratios(ticker: str, year: int | None = None):
    company_key = ticker.strip().upper()
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM financial_ratios WHERE company_id = (SELECT company_id FROM companies WHERE UPPER(COALESCE(company_id, '')) = UPPER(?) OR UPPER(COALESCE(ticker, '')) = UPPER(?) LIMIT 1)",
            (company_key, company_key),
        ).fetchall()
    items = [dict(r) for r in rows]
    if year is not None:
        items = [r for r in items if int(r["year"]) == year]
    return {"ticker": company_key, "history": items}


@app.get("/api/v1/companies/{ticker}/tearsheet")
def get_company_tearsheet(ticker: str):
    pdf_path = ROOT / "reports" / "tearsheets" / f"{ticker.upper()}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Tearsheet not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{ticker.upper()}.pdf")


@app.get("/api/v1/screener")
def screener(
    min_roe: float | None = None,
    max_de: float | None = None,
    min_fcf: float | None = None,
    sector: str | None = None,
    min_rev_cagr_5yr: float | None = None,
    min_pat_cagr_5yr: float | None = None,
    max_pe: float | None = None,
):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT company_id, name, ticker, broad_sector, roe_percentage AS roe, debt_to_equity AS de, free_cash_flow AS fcf, revenue_cagr_5yr, pat_cagr_5yr, pe_ratio AS pe FROM companies"
        ).fetchall()
    results = []
    for row in rows:
        item = dict(row)
        if min_roe is not None and (item.get("roe") or 0) < min_roe:
            continue
        if max_de is not None and (item.get("de") or 0) > max_de:
            continue
        if min_fcf is not None and (item.get("fcf") or 0) < min_fcf:
            continue
        if sector and str(item.get("broad_sector") or "").lower() != sector.lower():
            continue
        if min_rev_cagr_5yr is not None and (item.get("revenue_cagr_5yr") or 0) < min_rev_cagr_5yr:
            continue
        if min_pat_cagr_5yr is not None and (item.get("pat_cagr_5yr") or 0) < min_pat_cagr_5yr:
            continue
        if max_pe is not None and (item.get("pe") or 0) > max_pe:
            continue
        results.append(item)
    return results


@app.get("/api/v1/sectors")
def sectors():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT broad_sector AS sector, COUNT(*) AS company_count, AVG(CASE WHEN roe_percentage IS NOT NULL THEN roe_percentage ELSE NULL END) AS median_roe, AVG(CASE WHEN pe_ratio IS NOT NULL THEN pe_ratio ELSE NULL END) AS median_pe, AVG(CASE WHEN debt_to_equity IS NOT NULL THEN debt_to_equity ELSE NULL END) AS median_de FROM companies GROUP BY broad_sector ORDER BY sector"
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/v1/sectors/{sector}/companies")
def sector_companies(sector: str):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM companies WHERE UPPER(broad_sector) = UPPER(?) ORDER BY name",
            (sector,),
        ).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Sector not found")
    return [dict(row) for row in rows]


@app.get("/api/v1/portfolio/stats")
def portfolio_stats():
    return {"ok": True, "statistics": []}


@app.get("/api/v1/companies/{ticker}/documents")
def company_documents(ticker: str):
    company_key = ticker.strip().upper()
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT d.* FROM documents d JOIN companies c ON c.company_id = d.company_id WHERE UPPER(c.company_id) = UPPER(?) OR UPPER(c.ticker) = UPPER(?)",
            (company_key, company_key),
        ).fetchall()
    return [{"ticker": company_key, "documents": [dict(row) for row in rows]}]


@app.get("/api/v1/peers/{group_name}")
def peer_group(group_name: str):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM companies WHERE UPPER(broad_sector) = UPPER(?) ORDER BY name",
            (group_name,),
        ).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Peer group not found")
    return [dict(row) for row in rows]


@app.get("/api/v1/market-cap/{ticker}")
def market_cap_history(ticker: str):
    return {"ticker": ticker.upper(), "history": []}


@app.get("/api/v1/companies/{ticker}/peers/compare")
def peer_compare(ticker: str):
    return {"ticker": ticker.upper(), "axes": [], "company": {}, "peer_group_average": {}, "benchmark": {}}
