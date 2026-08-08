"""Loader to ingest source files into the Nifty100 SQLite database.

Features:
- Applies `db/schema.sql` when creating a new DB
- Ingests a set of expected files from `data/` into mapped tables
- Normalises `year` and `ticker` using `normaliser.py`
- Records per-table row counts and rejections to `output/load_audit.csv`
- Runs DQ validator after load and saves `output/validation_failures.csv`
"""
import argparse
import sqlite3
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from sqlalchemy import create_engine

from src.etl.normaliser import normalize_year, normalize_ticker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "db" / "schema.sql"
DB_DEFAULT = ROOT / "nifty100.db"
OUTPUT = ROOT / "output"


FILE_TABLE_MAP: List[Tuple[str, str]] = [
    ("companies", "companies"),
    ("profitandloss", "profitandloss"),
    ("balancesheet", "balancesheet"),
    ("cashflow", "cashflow"),
    ("analysis", "analysis"),
    ("documents", "documents"),
    ("prosandcons", "prosandcons"),
    ("sectors", "sectors"),
    ("stock_prices", "stock_prices"),
    ("financial_ratios", "financial_ratios"),
    ("peer_groups", "peer_groups"),
]


def apply_schema(conn: sqlite3.Connection):
    if not SCHEMA.exists():
        print("No schema.sql found at db/schema.sql — skipping schema application.")
        return
    with open(SCHEMA, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()


def init_db(db_path: Path) -> sqlite3.Connection:
    new_db = not db_path.exists()
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    if new_db:
        apply_schema(conn)
    return conn


def discover_file(data_dir: Path, prefix: str) -> Path:
    # look for files like prefix.csv/xlsx/xls
    for ext in (".csv", ".xlsx", ".xls"):
        p = data_dir / (prefix + ext)
        if p.exists():
            return p
    # try any file that contains prefix
    for p in data_dir.iterdir():
        if prefix in p.name.lower():
            return p
    return None


def read_table_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    return pd.read_csv(path)


def transform_dataframe(tbl: str, df: pd.DataFrame) -> pd.DataFrame:
    # Apply simple normalisations
    df = df.copy()
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)
    if "ticker" in df.columns:
        df["ticker"] = df["ticker"].apply(normalize_ticker)
    return df


def write_audit(audit_rows: List[Tuple[str, int, int]]):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    audit_path = OUTPUT / "load_audit.csv"
    with open(audit_path, "w", encoding="utf-8") as f:
        f.write("table,rows,rejections\n")
        for table, rows, rej in audit_rows:
            f.write(f"{table},{rows},{rej}\n")
    print(f"Wrote load audit to {audit_path}")


def run_foreign_key_check(conn: sqlite3.Connection) -> List[Tuple]:
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_key_check;")
    return cur.fetchall()


def load_all(db: str = None, data_dir: str = None):
    db_path = Path(db or DB_DEFAULT)
    data_dir = Path(data_dir or (ROOT / "data"))
    conn = init_db(db_path)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

    audit = []
    for prefix, table in FILE_TABLE_MAP:
        file_path = discover_file(data_dir, prefix)
        if file_path is None:
            audit.append((table, 0, 0))
            continue
        try:
            df = read_table_file(file_path)
            df = transform_dataframe(table, df)
            before_count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table}", engine).iloc[0, 0]
            # attempt to write via pandas to_sql, catching exceptions per-row by using transactions
            try:
                df.to_sql(table, engine, if_exists="append", index=False)
                rejections = 0
            except Exception:
                # fallback: insert row by row to count rejections
                rejections = 0
                with engine.begin() as conn_trans:
                    for _, row in df.iterrows():
                        try:
                            row.to_frame().T.to_sql(table, conn_trans, if_exists="append", index=False)
                        except Exception:
                            rejections += 1
            after_count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table}", engine).iloc[0, 0]
            inserted = after_count - before_count
            audit.append((table, inserted, rejections))
            print(f"Loaded {inserted} rows into {table} (rejections={rejections})")
        except Exception as e:
            print(f"Failed to load {file_path} -> {table}: {e}")
            audit.append((table, 0, 0))

    # write audit
    write_audit(audit)

    # run FK check and write small report
    fk_issues = run_foreign_key_check(conn)
    if fk_issues:
        print("Foreign key check returned issues:", fk_issues[:5])
    else:
        print("Foreign key check: 0 issues")

    conn.close()

    # run validators to produce validation_failures.csv
    try:
        from src.etl import validator

        validator.run_all_rules(db_path)
    except Exception as e:
        print("Failed to run validator:", e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="Path to SQLite DB", default=str(DB_DEFAULT))
    parser.add_argument("--data-dir", help="Directory with source files", default=str(ROOT / "data"))
    args = parser.parse_args()
    load_all(args.db, args.data_dir)


if __name__ == "__main__":
    main()
