import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import get_companies, get_ratios

def render():
    st.title("🏠 Home - Market Overview")

    selected_year = st.session_state.get("selected_year", 2024)

    companies_df = get_companies()
    ratios_df = get_ratios(year=selected_year)

    if ratios_df.empty:
        st.warning("No data available for the selected year.")
        return

    merged_df = companies_df.merge(ratios_df, on="ticker", how="inner", suffixes=("", "_ratio"))
    if "composite_score" not in merged_df and "composite_score_ratio" in merged_df:
        merged_df["composite_score"] = merged_df["composite_score_ratio"]

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Companies", len(merged_df))
    col2.metric("Average ROE", f"{merged_df['roe'].mean():.2%}" if "roe" in merged_df else "N/A")
    col3.metric("Median P/E", f"{merged_df['pe_ratio'].median():.2f}" if "pe_ratio" in merged_df else "N/A")
    col4.metric("Median D/E", f"{merged_df['debt_to_equity'].median():.2f}" if "debt_to_equity" in merged_df else "N/A")
    col5.metric("Median Revenue CAGR 5yr", f"{merged_df['revenue_cagr_5yr'].median():.2%}" if "revenue_cagr_5yr" in merged_df else "N/A")
    debt_free_count = int((merged_df["debt_to_equity"] < 0.3).sum()) if "debt_to_equity" in merged_df else 0
    col6.metric("Debt-Free Companies", debt_free_count)

    st.markdown("---")

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Sector Breakdown")
        sector_counts = companies_df["broad_sector"].value_counts().reset_index()
        sector_counts.columns = ["Broad Sector", "Count"]
        fig_donut = px.pie(
            sector_counts,
            names="Broad Sector",
            values="Count",
            hole=0.4,
            title="11 Sectors Distribution"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("Top 5 Quality Score Companies")
        top_5 = merged_df.sort_values(by="composite_score", ascending=False).head(5)
        st.dataframe(
            top_5[["ticker", "name", "broad_sector", "composite_score"]],
            hide_index=True,
            use_container_width=True,
        )

if __name__ == "__main__":
    render()

