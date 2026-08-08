"""Ratio engine: read DB, compute KPIs, populate financial_ratios table and outputs."""
import sqlite3
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "nifty100.db"
OUTPUT = ROOT / "output"

from src.analytics.ratios import (
    net_profit_margin_pct,
    operating_profit_margin_pct,
    return_on_equity_pct,
    return_on_capital_employed_pct,
    return_on_assets_pct,
    debt_to_equity,
    interest_coverage,
    net_debt,
    asset_turnover,
)
from src.analytics.cagr import cagr_from_series
from src.analytics.cashflow_kpis import (
    free_cash_flow,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
    write_capital_allocation_csv,
)


def ensure_columns(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(companies)")
    existing_cols = {row[1] for row in cur.fetchall()}
    for col, coltype in [
        ("broad_sector", "TEXT"),
        ("roce_percentage", "REAL"),
        ("roe_percentage", "REAL"),
    ]:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE companies ADD COLUMN {col} {coltype}")
    conn.commit()

    cur.execute("PRAGMA table_info(financial_ratios)")
    existing_cols = {row[1] for row in cur.fetchall()}
    new_cols = [
        ("net_profit_margin_pct", "REAL"),
        ("operating_profit_margin_pct", "REAL"),
        ("return_on_equity_pct", "REAL"),
        ("return_on_capital_employed_pct", "REAL"),
        ("return_on_assets_pct", "REAL"),
        ("debt_to_equity", "REAL"),
        ("interest_coverage", "REAL"),
        ("asset_turnover", "REAL"),
        ("free_cash_flow", "REAL"),
        ("capex_intensity_pct", "REAL"),
        ("fcf_conversion_rate_pct", "REAL"),
        ("composite_quality_score", "REAL"),
        ("revenue_cagr_5yr", "REAL"),
        ("pat_cagr_5yr", "REAL"),
        ("eps_cagr_5yr", "REAL"),
    ]
    for col, coltype in new_cols:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE financial_ratios ADD COLUMN {col} {coltype}")
    conn.commit()


def compute_and_populate(db_path: str = None):
    db_path = db_path or DB
    engine = create_engine(f"sqlite:///{db_path}")
    conn = sqlite3.connect(str(db_path))
    ensure_columns(conn)

    companies = pd.read_sql_query(
        "SELECT company_id, name, broad_sector, roce_percentage, roe_percentage FROM companies",
        engine,
    )

    capital_rows = []

    for _, comp in companies.iterrows():
        cid = comp["company_id"]
        broad_sector = comp.get("broad_sector")
        pl = pd.read_sql_query(
            f"SELECT year, sales, opm, net_profit, operating_profit, other_income, interest, earnings_per_share, dividend_payout_ratio_pct FROM profitandloss WHERE company_id='{cid}' ORDER BY year",
            engine,
        )
        bs = pd.read_sql_query(
            f"SELECT year, total_assets, total_liabilities FROM balancesheet WHERE company_id='{cid}' ORDER BY year",
            engine,
        )
        cf = pd.read_sql_query(
            f"SELECT year, net_cash, operating_activity, investing_activity, financing_activity FROM cashflow WHERE company_id='{cid}' ORDER BY year",
            engine,
        )

        if pl.empty and bs.empty:
            continue

        df = pl.merge(bs, on="year", how="outer")
        df = df.merge(cf, on="year", how="outer")
        df = df.sort_values("year").reset_index(drop=True)
        years = df["year"].tolist()

        revenue_values = df["sales"].tolist()
        pat_values = df["net_profit"].tolist()
        eps_values = df["earnings_per_share"].tolist()

        for idx, row in df.iterrows():
            year = int(row["year"]) if pd.notna(row["year"]) else None
            sales = row.get("sales")
            net_profit = row.get("net_profit")
            operating_profit = row.get("operating_profit")
            other_income = row.get("other_income")
            interest = row.get("interest")
            total_assets = row.get("total_assets")
            equity_capital = None
            reserves = None
            borrowings = None
            investments = None
            cfo = row.get("operating_activity")
            cfi = row.get("investing_activity")
            cff = row.get("financing_activity")

            npm = net_profit_margin_pct(net_profit, sales)
            opm_pct, opm_diff = operating_profit_margin_pct(operating_profit, sales, row.get("opm"))
            roe = return_on_equity_pct(net_profit, equity_capital, reserves)
            roce, bench_flag = return_on_capital_employed_pct(
                operating_profit,
                equity_capital,
                reserves,
                borrowings,
                broad_sector,
                comp.get("roce_percentage"),
            )
            roa = return_on_assets_pct(net_profit, total_assets)
            dte = debt_to_equity(borrowings, equity_capital, reserves)
            icr = interest_coverage(operating_profit, other_income, interest)
            nd = net_debt(borrowings, investments)
            at = asset_turnover(sales, total_assets)
            fcf = free_cash_flow(cfo, cfi)
            capex_pct = capex_intensity(cfi, sales)
            fcf_conv = fcf_conversion_rate(fcf, operating_profit)
            revenue_cagr_5yr, _ = cagr_from_series(revenue_values, years, 5)
            pat_cagr_5yr, _ = cagr_from_series(pat_values, years, 5)
            eps_cagr_5yr, _ = cagr_from_series(eps_values, years, 5)
            composite_quality_score = None

            capital_rows.append(
                {
                    "company_id": cid,
                    "year": year,
                    "cfo_sign": 1 if cfo and cfo > 0 else (-1 if cfo and cfo < 0 else 0),
                    "cfi_sign": 1 if cfi and cfi > 0 else (-1 if cfi and cfi < 0 else 0),
                    "cff_sign": 1 if cff and cff > 0 else (-1 if cff and cff < 0 else 0),
                }
            )

            df_out = pd.DataFrame(
                [
                    {
                        "company_id": cid,
                        "year": year,
                        "net_profit_margin_pct": npm,
                        "operating_profit_margin_pct": opm_pct,
                        "return_on_equity_pct": roe,
                        "return_on_capital_employed_pct": roce,
                        "return_on_assets_pct": roa,
                        "debt_to_equity": dte,
                        "interest_coverage": icr,
                        "asset_turnover": at,
                        "free_cash_flow": fcf,
                        "capex_intensity_pct": capex_pct,
                        "fcf_conversion_rate_pct": fcf_conv,
                        "revenue_cagr_5yr": revenue_cagr_5yr,
                        "pat_cagr_5yr": pat_cagr_5yr,
                        "eps_cagr_5yr": eps_cagr_5yr,
                        "composite_quality_score": composite_quality_score,
                    }
                ]
            )
            df_out.to_sql("financial_ratios", engine, if_exists="append", index=False)

    if capital_rows:
        write_capital_allocation_csv(capital_rows)

    conn.close()


if __name__ == "__main__":
    compute_and_populate()
