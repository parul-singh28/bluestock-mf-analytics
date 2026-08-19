from __future__ import annotations

import math
import sqlite3
from pathlib import Path

import pandas as pd
try:
    import streamlit as st
except ModuleNotFoundError:
    class _StreamlitFallback:
        @staticmethod
        def cache_data(*args, **kwargs):
            def decorator(func):
                return func

            return decorator

    st = _StreamlitFallback()

YEARS = list(range(2015, 2025))
ROOT = Path(__file__).resolve().parents[3]
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

CAPITAL_PATTERNS = [
    "Reinvestor",
    "Cash Compounder",
    "Dividend Distributor",
    "Debt Reducer",
    "Acquisition Led",
    "Capex Heavy",
    "Working Capital Builder",
    "Turnaround",
]

TICKERS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "ITC", "LT",
    "SBIN", "HINDUNILVR", "AXISBANK", "BAJFINANCE", "KOTAKBANK", "M&M", "SUNPHARMA",
    "MARUTI", "NTPC", "HCLTECH", "TITAN", "ULTRACEMCO", "TATAMOTORS", "POWERGRID",
    "ASIANPAINT", "BAJAJFINSV", "ONGC", "NESTLEIND", "COALINDIA", "WIPRO",
    "JSWSTEEL", "ADANIENT", "TATASTEEL", "TECHM", "GRASIM", "HINDALCO", "CIPLA",
    "DRREDDY", "BRITANNIA", "EICHERMOT", "DIVISLAB", "APOLLOHOSP", "HEROMOTOCO",
    "BPCL", "TATACONSUM", "BAJAJ-AUTO", "INDUSINDBK", "ADANIPORTS", "SHRIRAMFIN",
    "HDFCLIFE", "SBILIFE", "ICICIPRULI", "DLF", "PIDILITIND", "GODREJCP", "DABUR",
    "HAVELLS", "AMBUJACEM", "SIEMENS", "ABB", "VEDL", "BANKBARODA", "PNB",
    "CANBK", "UNIONBANK", "TVSMOTOR", "TRENT", "ZOMATO", "DMART", "NAUKRI",
    "IRCTC", "BEL", "HAL", "BHEL", "ADANIGREEN", "ADANIPOWER", "JIOFIN",
    "LTIM", "PERSISTENT", "OFSS", "MPHASIS", "LUPIN", "TORNTPHARM", "BIOCON",
    "MOTHERSON", "BOSCHLTD", "INDIGO", "GAIL", "IOC", "PETRONET", "COLPAL",
    "MARICO", "BERGEPAINT", "SHREECEM",
]


def _clean_name(ticker: str) -> str:
    return ticker.replace("-", " ").title().replace("Tcs", "TCS").replace("Itc", "ITC")


def _growth(first: float, last: float, periods: int = 5) -> float:
    if first <= 0 or periods <= 0:
        return 0.0
    return (last / first) ** (1 / periods) - 1


def _metric(seed: int, year: int, base: float, spread: float, scale: float = 1.0) -> float:
    cycle = math.sin((seed + 1) * 0.73 + (year - 2015) * 0.41)
    trend = (year - 2015) * 0.018
    return round((base + spread * cycle + trend) * scale, 4)


@st.cache_data(ttl=600)
def _companies_base() -> pd.DataFrame:
    rows = []
    for idx, ticker in enumerate(TICKERS, start=1):
        sector = SECTORS[(idx - 1) % len(SECTORS)]
        rows.append(
            {
                "company_id": f"C{idx:03d}",
                "name": _clean_name(ticker),
                "ticker": ticker,
                "broad_sector": sector,
                "sector": sector,
                "sub_sector": f"{sector} - Core",
                "about": f"{_clean_name(ticker)} is tracked in the Nifty 100 analytics universe.",
                "capital_pattern": CAPITAL_PATTERNS[(idx - 1) % len(CAPITAL_PATTERNS)],
                "report_years": [2024, 2023, 2022, 2021, 2020],
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=600)
def get_companies() -> pd.DataFrame:
    companies = _companies_base().copy()
    latest = get_ratios(year=2024)
    companies = companies.merge(
        latest[["ticker", "market_cap_crore", "composite_score"]].rename(
            columns={"market_cap_crore": "latest_market_cap_crore"}
        ),
        on="ticker",
        how="left",
    )
    history_map = {
        ticker: rows.drop(columns=["ticker"]).to_dict("records")
        for ticker, rows in get_ratios().groupby("ticker", sort=False)
    }
    companies["history"] = companies["ticker"].map(history_map)
    companies["revenue_cagr_5yr"] = companies["ticker"].map(
        lambda t: _growth(
            history_map[t][-6]["revenue"] if len(history_map[t]) >= 6 else history_map[t][0]["revenue"],
            history_map[t][-1]["revenue"],
        )
    )
    companies["pat_cagr_5yr"] = companies["ticker"].map(
        lambda t: _growth(
            max(history_map[t][-6]["net_profit"], 1),
            max(history_map[t][-1]["net_profit"], 1),
        )
    )
    return companies


@st.cache_data(ttl=600)
def get_ratios(ticker: str | None = None, year: int | None = None) -> pd.DataFrame:
    company_df = _companies_base()
    rows = []
    for idx, company in company_df.reset_index(drop=True).iterrows():
        seed = idx + 1
        for yr in YEARS:
            revenue = max(900, 2500 + seed * 185 + (yr - 2015) * (110 + seed % 9 * 18))
            opm = min(0.42, max(0.06, _metric(seed, yr, 0.17, 0.045)))
            net_profit = revenue * opm * (0.58 + (seed % 7) * 0.025)
            fcf = net_profit * (0.72 + (seed % 5) * 0.08)
            roe = min(0.38, max(0.055, _metric(seed, yr, 0.155, 0.055)))
            roce = min(0.42, max(0.06, roe + 0.035 + ((seed % 4) * 0.006)))
            pe = max(7.0, round(15 + (seed % 17) * 1.35 + (yr - 2020) * 0.28, 2))
            pb = max(0.7, round(1.2 + (seed % 13) * 0.28, 2))
            market_cap = round(revenue * pe / 7.5, 2)
            rows.append(
                {
                    "company_id": company["company_id"],
                    "ticker": company["ticker"],
                    "year": yr,
                    "revenue": round(revenue, 2),
                    "net_profit": round(net_profit, 2),
                    "roe": round(roe, 4),
                    "roce": round(roce, 4),
                    "debt_to_equity": round(max(0.02, (seed % 16) / 10), 2),
                    "operating_margin": round(opm, 4),
                    "pe_ratio": pe,
                    "pb_ratio": pb,
                    "ev_ebitda": round(pe * 0.62 + pb * 1.1, 2),
                    "dividend_yield": round((seed % 8) * 0.004, 4),
                    "icr": round(2.0 + (seed % 12) * 0.75, 2),
                    "fcf": round(fcf, 2),
                    "market_cap_crore": market_cap,
                    "composite_score": round((roe * 100) + (opm * 35) + min(fcf / 450, 20), 2),
                }
            )
    df = pd.DataFrame(rows)
    if ticker:
        df = df[df["ticker"].str.upper() == ticker.upper()]
    if year:
        df = df[df["year"] == int(year)]
    return df.reset_index(drop=True)


@st.cache_data(ttl=600)
def get_pl(ticker: str) -> pd.DataFrame:
    return get_ratios(ticker=ticker)[["ticker", "year", "revenue", "net_profit", "operating_margin"]]


@st.cache_data(ttl=600)
def get_bs(ticker: str) -> pd.DataFrame:
    df = get_ratios(ticker=ticker)[["ticker", "year", "market_cap_crore", "debt_to_equity"]].copy()
    df["total_assets"] = df["market_cap_crore"] * 0.72
    df["total_liabilities"] = df["total_assets"] * df["debt_to_equity"] / (1 + df["debt_to_equity"])
    return df


@st.cache_data(ttl=600)
def get_cf(ticker: str) -> pd.DataFrame:
    df = get_ratios(ticker=ticker)[["ticker", "year", "fcf"]].copy()
    df["net_cash"] = df["fcf"]
    return df


@st.cache_data(ttl=600)
def get_sectors() -> pd.DataFrame:
    counts = get_companies()["broad_sector"].value_counts().rename_axis("sector").reset_index(name="company_count")
    return counts.sort_values("sector").reset_index(drop=True)


@st.cache_data(ttl=600)
def get_peers(group_name: str) -> pd.DataFrame:
    return get_companies()[get_companies()["broad_sector"] == group_name].reset_index(drop=True)


@st.cache_data(ttl=600)
def get_valuation(ticker: str) -> dict:
    companies = get_companies()
    match = companies[companies["ticker"].str.upper() == ticker.upper()]
    if match.empty:
        return {}
    company = match.iloc[0]
    latest = get_ratios(ticker=ticker, year=2024).iloc[0]
    five_year = get_ratios(ticker=ticker)
    five_year = five_year[five_year["year"] >= 2020]
    market_cap = max(float(latest["market_cap_crore"]), 1.0)
    return {
        "company_id": company["company_id"],
        "company_name": company["name"],
        "sector": company["broad_sector"],
        "pe": float(latest["pe_ratio"]),
        "pb": float(latest["pb_ratio"]),
        "ev_ebitda": float(latest["ev_ebitda"]),
        "fcf_yield_pct": round(float(latest["fcf"]) / market_cap * 100, 2),
        "five_year_median_pe": round(float(five_year["pe_ratio"].median()), 2),
    }


def read_sql(query: str, params: tuple = ()) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)
