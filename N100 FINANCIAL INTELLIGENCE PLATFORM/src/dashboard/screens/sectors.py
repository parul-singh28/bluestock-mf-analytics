import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import get_companies, get_ratios, get_sectors

def render():
    st.title("Sector Analysis")

    companies_df = get_companies()
    selected_year = st.session_state.get("selected_year", 2024)

    sectors = get_sectors()["sector"].tolist()
    selected_sector = st.selectbox("Sector", sectors, key="sector_select")
    sector_companies = companies_df[companies_df["broad_sector"] == selected_sector]

    rows = []
    for _, company in sector_companies.iterrows():
        ratio = get_ratios(ticker=company["ticker"], year=selected_year)
        if ratio.empty:
            continue
        ratio = ratio.iloc[0]
        rows.append({
            "company": company["name"],
            "sub_sector": company["sub_sector"],
            "revenue": ratio["revenue"],
            "roe": ratio["roe"],
            "market_cap": ratio["market_cap_crore"],
        })

    bubble_df = pd.DataFrame(rows)
    fig = px.scatter(
        bubble_df,
        x="revenue",
        y="roe",
        size="market_cap",
        color="sub_sector",
        hover_name="company",
        title=f"{selected_sector} Bubble Chart",
    )
    st.plotly_chart(fig, use_container_width=True)

    median_roe = bubble_df["roe"].median() if not bubble_df.empty else 0
    median_revenue = bubble_df["revenue"].median() if not bubble_df.empty else 0

    bar_df = pd.DataFrame({
        "metric": ["Median ROE", "Median Revenue"],
        "value": [median_roe, median_revenue],
    })
    fig2 = px.bar(bar_df, x="metric", y="value", title="Sector Median KPI")
    st.plotly_chart(fig2, use_container_width=True)
