"""Company endpoints."""
from fastapi import APIRouter, HTTPException
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "nifty100.db"

router = APIRouter(prefix="/companies", tags=["companies"])


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
def list_companies():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT company_id, name, broad_sector, ticker, roe_percentage, roce_percentage FROM companies ORDER BY name").fetchall()
    return [dict(r) for r in rows]


@router.get("/{ticker}")
def get_company(ticker: str):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM companies WHERE UPPER(ticker)=UPPER(?) LIMIT 1", (ticker,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return dict(row)
