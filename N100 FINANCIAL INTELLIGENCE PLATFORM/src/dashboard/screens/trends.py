import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import YEARS, get_companies, get_ratios

def render():
    st.title("Trend Analysis")

    companies_df = get_companies()
    company_name = st.selectbox("Company", companies_df["name"].tolist(), key="trend_company")
    selected_company = companies_df[companies_df["name"] == company_name].iloc[0]

    metric_map = {
        "Revenue": "revenue",
        "Net Profit": "net_profit",
        "ROE": "roe",
        "ROCE": "roce",
        "D/E": "debt_to_equity",
        "FCF": "fcf",
    }

    selected_metrics = st.multiselect("Metrics", list(metric_map.keys()), default=["Revenue", "Net Profit", "ROE"], max_selections=3)

    fig = go.Figure()
    for metric_name in selected_metrics:
        values = []
        for year in YEARS:
            ratio = get_ratios(ticker=selected_company["ticker"], year=year)
            if ratio.empty:
                values.append(None)
            else:
                values.append(ratio.iloc[0][metric_map[metric_name]])

        fig.add_trace(go.Scatter(x=YEARS, y=values, mode="lines+markers", name=metric_name))

        for idx, value in enumerate(values):
            if idx == 0 or value is None or values[idx - 1] in (None, 0):
                continue
            yoy = ((value - values[idx - 1]) / values[idx - 1]) * 100
            fig.add_annotation(x=YEARS[idx], y=value, text=f"{yoy:+.1f}%", showarrow=False, yshift=10)

    fig.update_layout(title=f"{selected_company['name']} Trend", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
