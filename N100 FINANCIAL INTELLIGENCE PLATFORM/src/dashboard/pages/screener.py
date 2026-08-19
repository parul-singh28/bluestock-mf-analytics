import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import get_companies, get_ratios

def render():
    st.title("Screener")

    selected_year = st.session_state.get("selected_year", 2024)

    defaults = {
        "roe_min": 0.0,
        "de_max": 2.0,
        "fcf_min": 0.0,
        "revenue_cagr_min": 0.0,
        "pat_cagr_min": 0.0,
        "opm_min": 0.0,
        "pe_max": 40.0,
        "pb_max": 5.0,
        "dividend_yield_min": 0.0,
        "icr_min": 0.0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    def slider(key, label, min_value, max_value, step):
        val = st.session_state.get(key, defaults[key])
        new_val = st.sidebar.slider(label, min_value=min_value, max_value=max_value, value=val, step=step)
        st.session_state[key] = new_val
        return new_val

    st.sidebar.subheader("Filters")
    roe_min = slider("roe_min", "ROE min", 0.0, 0.4, 0.01)
    de_max = slider("de_max", "D/E max", 0.0, 3.0, 0.01)
    fcf_min = slider("fcf_min", "FCF min", 0.0, 5000.0, 50.0)
    revenue_cagr_min = slider("revenue_cagr_min", "Revenue CAGR min", 0.0, 0.3, 0.01)
    pat_cagr_min = slider("pat_cagr_min", "PAT CAGR min", 0.0, 0.3, 0.01)
    opm_min = slider("opm_min", "OPM min", 0.0, 0.3, 0.01)
    pe_max = slider("pe_max", "P/E max", 5.0, 60.0, 1.0)
    pb_max = slider("pb_max", "P/B max", 0.5, 8.0, 0.1)
    dividend_yield_min = slider("dividend_yield_min", "Dividend Yield min", 0.0, 0.1, 0.001)
    icr_min = slider("icr_min", "ICR min", 0.0, 10.0, 0.1)

    preset_map = {
        "Quality": {"roe_min": 0.12, "de_max": 1.0, "fcf_min": 250, "revenue_cagr_min": 0.08, "pat_cagr_min": 0.08, "opm_min": 0.12, "pe_max": 25, "pb_max": 3.0, "dividend_yield_min": 0.01, "icr_min": 4.0},
        "Value": {"roe_min": 0.08, "de_max": 0.8, "fcf_min": 100, "revenue_cagr_min": 0.05, "pat_cagr_min": 0.05, "opm_min": 0.08, "pe_max": 15, "pb_max": 2.0, "dividend_yield_min": 0.01, "icr_min": 3.0},
        "Growth": {"roe_min": 0.1, "de_max": 1.2, "fcf_min": 200, "revenue_cagr_min": 0.12, "pat_cagr_min": 0.12, "opm_min": 0.1, "pe_max": 30, "pb_max": 4.0, "dividend_yield_min": 0.0, "icr_min": 3.5},
        "Dividend": {"roe_min": 0.08, "de_max": 0.9, "fcf_min": 150, "revenue_cagr_min": 0.04, "pat_cagr_min": 0.04, "opm_min": 0.08, "pe_max": 20, "pb_max": 2.5, "dividend_yield_min": 0.02, "icr_min": 4.0},
        "Debt-Free": {"roe_min": 0.09, "de_max": 0.3, "fcf_min": 120, "revenue_cagr_min": 0.05, "pat_cagr_min": 0.05, "opm_min": 0.09, "pe_max": 22, "pb_max": 2.8, "dividend_yield_min": 0.0, "icr_min": 3.0},
        "Turnaround": {"roe_min": 0.06, "de_max": 1.5, "fcf_min": 80, "revenue_cagr_min": 0.03, "pat_cagr_min": 0.03, "opm_min": 0.06, "pe_max": 35, "pb_max": 5.0, "dividend_yield_min": 0.0, "icr_min": 2.0},
    }

    cols = st.sidebar.columns(3)
    for idx, (name, values) in enumerate(preset_map.items()):
        if cols[idx % 3].button(name):
            for key, value in values.items():
                st.session_state[key] = value

    companies_df = get_companies()
    rows = []

    for _, company in companies_df.iterrows():
        metrics_df = get_ratios(ticker=company["ticker"], year=selected_year)
        if metrics_df.empty:
            continue
        metrics = metrics_df.iloc[0]

        if (
            metrics["roe"] >= roe_min and
            metrics["debt_to_equity"] <= de_max and
            metrics["fcf"] >= fcf_min and
            company["revenue_cagr_5yr"] is not None and company["revenue_cagr_5yr"] >= revenue_cagr_min and
            company["pat_cagr_5yr"] is not None and company["pat_cagr_5yr"] >= pat_cagr_min and
            metrics["operating_margin"] >= opm_min and
            metrics["pe_ratio"] <= pe_max and
            metrics["pb_ratio"] <= pb_max and
            metrics["dividend_yield"] >= dividend_yield_min and
            metrics["icr"] >= icr_min
        ):
            rows.append({
                "company_id": company["company_id"],
                "name": company["name"],
                "sector": company["broad_sector"],
                "composite_score": company["composite_score"],
                "roe": metrics["roe"],
                "debt_to_equity": metrics["debt_to_equity"],
                "fcf": metrics["fcf"],
                "revenue_cagr_5yr": company["revenue_cagr_5yr"],
                "pat_cagr_5yr": company["pat_cagr_5yr"],
                "operating_margin": metrics["operating_margin"],
                "pe_ratio": metrics["pe_ratio"],
                "pb_ratio": metrics["pb_ratio"],
                "dividend_yield": metrics["dividend_yield"],
                "icr": metrics["icr"],
            })

    st.caption(f"{len(rows)} companies match your filters")
    df = pd.DataFrame(rows)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, file_name="screener_results.csv", mime="text/csv")
    else:
        st.info("No companies match the selected filters")

render()        