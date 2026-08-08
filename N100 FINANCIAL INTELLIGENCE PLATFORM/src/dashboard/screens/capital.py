import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import get_companies

def render():
    st.title("Capital Allocation Map")

    companies_df = get_companies()
    patterns = sorted(companies_df["capital_pattern"].unique().tolist())
    selected_pattern = st.selectbox("Capital allocation pattern", patterns, key="capital_pattern")

    subset = companies_df[companies_df["capital_pattern"] == selected_pattern]

    labels = [selected_pattern] + subset["name"].tolist()
    parents = [""] + [selected_pattern for _ in subset["name"]]
    values = [subset["latest_market_cap_crore"].sum()] + subset["latest_market_cap_crore"].tolist()

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label+value",
        branchvalues="total",
    ))
    fig.update_layout(title="Capital Allocation Treemap", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Companies in this pattern")
    st.dataframe(
        subset[["company_id", "name", "broad_sector", "capital_pattern"]],
        use_container_width=True,
    )
