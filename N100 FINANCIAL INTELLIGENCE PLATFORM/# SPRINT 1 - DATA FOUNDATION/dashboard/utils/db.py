import statistics
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

YEARS = list(range(2015, 2025))

SECTORS = [
    "IT", "Financials", "FMCG", "Energy", "Healthcare",
    "Industrials", "Consumer Durables", "Telecom", "Materials",
    "Utilities", "Auto"
]

SUB_SECTORS = {
    "IT": ["Software", "Cloud", "Semiconductors", "Cybersecurity"],
    "Financials": ["Banks", "Insurance", "NBFC", "Capital Markets"],
    "FMCG": ["Packaged Foods", "Personal Care", "Household"],
    "Energy": ["Oil & Gas", "Renewables", "Utilities"],
    "Healthcare": ["Pharma", "Diagnostics", "Biotech"],
    "Industrials": ["Engineering", "Manufacturing", "Logistics"],
    "Consumer Durables": ["Electronics", "Appliances", "Furniture"],
    "Telecom": ["Connectivity", "Infrastructure", "Digital"],
    "Materials": ["Chemicals", "Metals", "Mining"],
    "Utilities": ["Power", "Gas", "Water"],
    "Auto": ["Passenger Vehicles", "Commercial Vehicles", "Components"],
}

CAPITAL_PATTERNS = [
    "Buybacks", "Debt Repayment", "Dividend Growth",
    "Capex Expansion", "Acquisition", "Cash Buffer",
    "M&A", "Shareholder Returns"
]

def _build_dataset():
    rows = []

    for idx in range(92):
        sector = SECTORS[idx % len(SECTORS)]
        sub_sector = SUB_SECTORS[sector][idx % len(SUB_SECTORS[sector])]
        capital_pattern = CAPITAL_PATTERNS[idx % len(CAPITAL_PATTERNS)]

        company_id = f"CMP{idx + 1:03d}"
        ticker = f"ST{idx + 1:03d}"
        name = f"{sector} Co {idx + 1}"

        history = []
        for year in YEARS:
            revenue = round(5000 * (1 + 0.07 + 0.002 * (idx % 6)) ** (year - 2015) + idx * 100, 2)
            net_profit = round(revenue * (0.11 + 0.002 * (idx % 5) + 0.001 * (year - 2015)), 2)
            roe = round(0.10 + 0.003 * (idx % 5) + 0.004 * (year - 2015), 4)
            roce = round(roe + 0.01 + 0.001 * (idx % 4), 4)
            debt_to_equity = round(0.2 + 0.03 * (idx % 5) + 0.01 * (year - 2015), 4)
            fcf = round(revenue * 0.04 + 50 * (idx % 4) + 20 * (year - 2015), 2)
            operating_margin = round(0.10 + 0.004 * (idx % 4) + 0.001 * (year - 2015), 4)
            pe_ratio = round(10 + idx % 7 + 0.6 * (year - 2015), 2)
            pb_ratio = round(1.0 + 0.18 * (idx % 5) + 0.02 * (year - 2015), 2)
            ev_ebitda = round(7 + 0.4 * (idx % 5) + 0.2 * (year - 2015), 2)
            dividend_yield = round(0.01 + 0.003 * (idx % 6) + 0.0004 * (year - 2015), 4)
            icr = round(3.5 + 0.4 * (idx % 5) + 0.2 * (year - 2015), 2)
            market_cap_crore = round(10000 + idx * 180 + year * 100, 2)

            history.append({
                "year": year,
                "revenue": revenue,
                "net_profit": net_profit,
                "roe": roe,
                "roce": roce,
                "debt_to_equity": debt_to_equity,
                "fcf": fcf,
                "operating_margin": operating_margin,
                "pe_ratio": pe_ratio,
                "pb_ratio": pb_ratio,
                "ev_ebitda": ev_ebitda,
                "dividend_yield": dividend_yield,
                "icr": icr,
                "market_cap_crore": market_cap_crore,
            })

        latest = history[-1]
        revenue_cagr_5yr = round((latest["revenue"] / history[0]["revenue"]) ** (1 / 5) - 1, 4) if len(history) > 5 else None
        pat_cagr_5yr = round((latest["net_profit"] / history[0]["net_profit"]) ** (1 / 5) - 1, 4) if len(history) > 5 else None

        composite_score = round(
            latest["roe"] * 0.25 +
            latest["operating_margin"] * 0.2 +
            (latest["fcf"] / max(latest["market_cap_crore"], 1)) * 0.2 +
            revenue_cagr_5yr * 0.15 +
            latest["dividend_yield"] * 0.1 +
            (1 / max(latest["debt_to_equity"], 0.01)) * 0.1,
            2
        )

        rows.append({
            "company_id": company_id,
            "name": name,
            "ticker": ticker,
            "broad_sector": sector,
            "sector": sector,
            "sub_sector": sub_sector,
            "about": f"{name} is a diversified {sector} company focused on {sub_sector.lower()} operations.",
            "capital_pattern": capital_pattern,
            "latest_year": latest["year"],
            "latest_revenue": latest["revenue"],
            "latest_net_profit": latest["net_profit"],
            "latest_roe": latest["roe"],
            "latest_roce": latest["roce"],
            "latest_debt_to_equity": latest["debt_to_equity"],
            "latest_fcf": latest["fcf"],
            "latest_operating_margin": latest["operating_margin"],
            "latest_pe_ratio": latest["pe_ratio"],
            "latest_pb_ratio": latest["pb_ratio"],
            "latest_ev_ebitda": latest["ev_ebitda"],
            "latest_dividend_yield": latest["dividend_yield"],
            "latest_icr": latest["icr"],
            "latest_market_cap_crore": latest["market_cap_crore"],
            "history": history,
            "revenue_cagr_5yr": revenue_cagr_5yr,
            "pat_cagr_5yr": pat_cagr_5yr,
            "composite_score": composite_score,
            "report_years": [2024, 2023, 2022, 2021, 2020, 2019],
        })

    rows = sorted(rows, key=lambda x: x["composite_score"], reverse=True)
    return rows

@st.cache_data(ttl=600)
def get_companies():
    return pd.DataFrame(_build_dataset())

@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):
    companies_df = get_companies()

    if ticker:
        company = companies_df[companies_df["ticker"].str.upper() == ticker.upper()]
        if company.empty:
            return pd.DataFrame()
        company = company.iloc[0]
        target_year = year or company["latest_year"]
        row = next((h for h in company["history"] if h["year"] == target_year), None)
        if row is None:
            return pd.DataFrame()
        return pd.DataFrame([{
            "ticker": company["ticker"],
            "name": company["name"],
            "company_name": company["name"],
            "broad_sector": company["broad_sector"],
            "sector": company["sector"],
            "sub_sector": company["sub_sector"],
            "year": target_year,
            "revenue": row["revenue"],
            "net_profit": row["net_profit"],
            "roe": row["roe"],
            "roce": row["roce"],
            "debt_to_equity": row["debt_to_equity"],
            "fcf": row["fcf"],
            "operating_margin": row["operating_margin"],
            "pe_ratio": row["pe_ratio"],
            "pb_ratio": row["pb_ratio"],
            "ev_ebitda": row["ev_ebitda"],
            "dividend_yield": row["dividend_yield"],
            "icr": row["icr"],
            "market_cap_crore": row["market_cap_crore"],
            "revenue_cagr_5yr": company["revenue_cagr_5yr"],
            "pat_cagr_5yr": company["pat_cagr_5yr"],
            "composite_score": company["composite_score"],
        }])

    target_year = year or max(YEARS)
    rows = []
    for _, company in companies_df.iterrows():
        row = next((h for h in company["history"] if h["year"] == target_year), None)
        if row:
            rows.append({
                "ticker": company["ticker"],
                "name": company["name"],
                "company_name": company["name"],
                "broad_sector": company["broad_sector"],
                "sector": company["sector"],
                "sub_sector": company["sub_sector"],
                "year": target_year,
                "revenue": row["revenue"],
                "net_profit": row["net_profit"],
                "roe": row["roe"],
                "roce": row["roce"],
                "debt_to_equity": row["debt_to_equity"],
                "fcf": row["fcf"],
                "operating_margin": row["operating_margin"],
                "pe_ratio": row["pe_ratio"],
                "pb_ratio": row["pb_ratio"],
                "ev_ebitda": row["ev_ebitda"],
                "dividend_yield": row["dividend_yield"],
                "icr": row["icr"],
                "market_cap_crore": row["market_cap_crore"],
                "revenue_cagr_5yr": company["revenue_cagr_5yr"],
                "pat_cagr_5yr": company["pat_cagr_5yr"],
                "composite_score": company["composite_score"],
            })

    return pd.DataFrame(rows)

@st.cache_data(ttl=600)
def get_pl(ticker):
    companies_df = get_companies()
    company = companies_df[companies_df["ticker"].str.upper() == ticker.upper()]
    if company.empty:
        return {}
    company = company.iloc[0]
    return {
        "company_id": company["company_id"],
        "company_name": company["name"],
        "years": [h["year"] for h in company["history"]],
        "revenue": [h["revenue"] for h in company["history"]],
        "net_profit": [h["net_profit"] for h in company["history"]],
    }

@st.cache_data(ttl=600)
def get_bs(ticker):
    companies_df = get_companies()
    company = companies_df[companies_df["ticker"].str.upper() == ticker.upper()]
    if company.empty:
        return {}
    company = company.iloc[0]
    return {
        "company_id": company["company_id"],
        "company_name": company["name"],
        "assets": company["latest_revenue"] * 1.1,
        "liabilities": company["latest_revenue"] * 0.55,
        "equity": company["latest_revenue"] * 0.55,
        "cash": company["latest_fcf"] * 1.2,
    }

@st.cache_data(ttl=600)
def get_cf(ticker):
    companies_df = get_companies()
    company = companies_df[companies_df["ticker"].str.upper() == ticker.upper()]
    if company.empty:
        return {}
    company = company.iloc[0]
    return {
        "company_id": company["company_id"],
        "company_name": company["name"],
        "fcf": company["latest_fcf"],
        "operating_cf": company["latest_fcf"] + 120,
        "investing_cf": -company["latest_fcf"] * 0.2,
        "financing_cf": company["latest_fcf"] * 0.1,
    }

@st.cache_data(ttl=600)
def get_sectors():
    companies_df = get_companies()
    counts = companies_df["broad_sector"].value_counts().reset_index()
    counts.columns = ["sector", "company_count"]
    return counts

@st.cache_data(ttl=600)
def get_peers(group_name):
    companies_df = get_companies()
    return companies_df[companies_df["broad_sector"].str.lower() == group_name.lower()].copy()

@st.cache_data(ttl=600)
def get_valuation(ticker):
    companies_df = get_companies()
    company = companies_df[companies_df["ticker"].str.upper() == ticker.upper()]
    if company.empty:
        return {}
    company = company.iloc[0]
    history = company["history"]
    pe_history = [h["pe_ratio"] for h in history[-5:]]
    return {
        "company_id": company["company_id"],
        "company_name": company["name"],
        "sector": company["broad_sector"],
        "pe": company["latest_pe_ratio"],
        "pb": company["latest_pb_ratio"],
        "ev_ebitda": company["latest_ev_ebitda"],
        "fcf_yield_pct": round((company["latest_fcf"] / max(company["latest_market_cap_crore"], 1)) * 100, 2),
        "five_year_median_pe": round(statistics.median(pe_history), 2) if pe_history else None,
        "market_cap_crore": company["latest_market_cap_crore"],
    }