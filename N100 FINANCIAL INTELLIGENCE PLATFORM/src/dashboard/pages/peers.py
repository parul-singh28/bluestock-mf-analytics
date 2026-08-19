import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import get_companies, get_ratios, get_sectors

def render():
    st.title("Peer Comparison")

    companies_df = get_companies()
    selected_year = st.session_state.get("selected_year", 2024)

    sectors = get_sectors()["sector"].tolist()
    selected_group = st.selectbox("Peer group", sectors, key="peer_group")
    group_companies = companies_df[companies_df["broad_sector"] == selected_group]

    if group_companies.empty:
        st.info("No companies found")
        return

    benchmark_name = st.selectbox("Benchmark company", group_companies["name"].tolist(), key="peer_company")
    benchmark_company = group_companies[group_companies["name"] == benchmark_name].iloc[0]

    metrics = ["ROE", "D/E", "FCF Yield", "Revenue CAGR", "PAT CAGR", "OPM", "P/E", "P/B"]
    benchmark_ratio = get_ratios(ticker=benchmark_company["ticker"], year=selected_year).iloc[0]
    benchmark_values = [
        benchmark_ratio["roe"],
        benchmark_ratio["debt_to_equity"],
        (benchmark_ratio["fcf"] / max(benchmark_ratio["market_cap_crore"], 1)) * 100,
        benchmark_company["revenue_cagr_5yr"],
        benchmark_company["pat_cagr_5yr"],
        benchmark_ratio["operating_margin"],
        benchmark_ratio["pe_ratio"],
        benchmark_ratio["pb_ratio"],
    ]

    group_values = []
    for _, company in group_companies.iterrows():
        ratio = get_ratios(ticker=company["ticker"], year=selected_year)
        if ratio.empty:
            continue
        ratio = ratio.iloc[0]
        group_values.append([
            ratio["roe"],
            ratio["debt_to_equity"],
            (ratio["fcf"] / max(ratio["market_cap_crore"], 1)) * 100,
            company["revenue_cagr_5yr"],
            company["pat_cagr_5yr"],
            ratio["operating_margin"],
            ratio["pe_ratio"],
            ratio["pb_ratio"],
        ])

    avg_values = [sum(row[i] for row in group_values) / len(group_values) for i in range(len(metrics))]

    def normalize(vals):
        max_val = max(vals) if max(vals) > 0 else 1
        return [v / max_val for v in vals]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=normalize(benchmark_values), theta=metrics, fill="toself", name="Benchmark"))
    fig.add_trace(go.Scatterpolar(r=normalize(avg_values), theta=metrics, fill="toself", name="Group Avg"))
    fig.update_layout(title="Benchmark vs Peer Group Average", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    rows = []
    for _, company in group_companies.iterrows():
        ratio = get_ratios(ticker=company["ticker"], year=selected_year)
        if ratio.empty:
            continue
        ratio = ratio.iloc[0]
        rows.append({
            "company": company["name"],
            "sector": company["broad_sector"],
            "ROE": ratio["roe"],
            "P/E": ratio["pe_ratio"],
            "P/B": ratio["pb_ratio"],
            "FCF Yield": (ratio["fcf"] / max(ratio["market_cap_crore"], 1)) * 100,
            "Composite Score": company["composite_score"],
        })

    df = pd.DataFrame(rows)
    df["benchmark"] = df["company"] == benchmark_company["name"]
    st.dataframe(df, use_container_width=True)

render()    