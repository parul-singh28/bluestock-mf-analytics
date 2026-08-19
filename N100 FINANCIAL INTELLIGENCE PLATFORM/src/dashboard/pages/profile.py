import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import get_companies, get_ratios

def render():
    st.title("Company Profile")

    companies_df = get_companies()
    selected_year = st.session_state.get("selected_year", 2024)

    search = st.text_input("Search by company name or ticker", key="profile_search")
    if search:
        matches = companies_df[
            companies_df["name"].str.lower().str.contains(search.lower()) |
            companies_df["ticker"].str.lower().str.contains(search.lower())
        ]
    else:
        matches = companies_df.head(20)

    if matches.empty:
        st.warning("Ticker not found — please try another")
        return

    options = [f"{row['name']} ({row['ticker']})" for _, row in matches.iterrows()]
    selected = st.selectbox("Select company", options, key="profile_company")
    company = matches[matches["name"] + " (" + matches["ticker"] + ")" == selected].iloc[0]

    metrics_df = get_ratios(ticker=company["ticker"], year=selected_year)
    if metrics_df.empty:
        st.info("No data available for this company in the selected year")
        return

    metrics = metrics_df.iloc[0]

    st.subheader(company["name"])
    st.caption(f"Sector: {company['broad_sector']} | Sub-sector: {company['sub_sector']} | NSE ticker: {company['ticker']}")
    st.write(company["about"])

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("ROE", f"{metrics['roe']:.2%}" if metrics.get("roe") is not None else "N/A")
    col2.metric("ROCE", f"{metrics['roce']:.2%}" if metrics.get("roce") is not None else "N/A")
    col3.metric("Net Profit Margin", f"{metrics['operating_margin']:.2%}" if metrics.get("operating_margin") is not None else "N/A")
    col4.metric("D/E", f"{metrics['debt_to_equity']:.2f}" if metrics.get("debt_to_equity") is not None else "N/A")
    col5.metric("Revenue CAGR 5yr", f"{company['revenue_cagr_5yr']:.2%}" if company.get("revenue_cagr_5yr") is not None else "N/A")
    col6.metric("FCF", f"{metrics['fcf']:,.0f}" if metrics.get("fcf") is not None else "N/A")

    history = company["history"]
    years = [h["year"] for h in history]
    revenue = [h["revenue"] for h in history]
    profit = [h["net_profit"] for h in history]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=revenue, name="Revenue"))
    fig.add_trace(go.Bar(x=years, y=profit, name="Net Profit"))
    fig.update_layout(barmode="group", title="Revenue & Net Profit (10Y)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    roe_vals = [h["roe"] for h in history]
    roce_vals = [h["roce"] for h in history]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=years, y=roe_vals, mode="lines+markers", name="ROE", yaxis="y"))
    fig2.add_trace(go.Scatter(x=years, y=roce_vals, mode="lines+markers", name="ROCE", yaxis="y2"))
    fig2.update_layout(
        title="ROE vs ROCE (10Y)",
        yaxis=dict(title="ROE"),
        yaxis2=dict(title="ROCE", overlaying="y", side="right"),
        template="plotly_white",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Pros & Cons")
    col_a, col_b = st.columns(2)
    with col_a:
        st.success("Strong profitability")
        st.success("Healthy free cash flow")
    with col_b:
        st.error("Higher leverage than peers")
        st.error("Lower dividend yield")
        
render()        