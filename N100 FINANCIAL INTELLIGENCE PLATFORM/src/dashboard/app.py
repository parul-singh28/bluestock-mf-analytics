from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard.screens import capital, home, peers, profile, reports, screener, sectors, trends

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "Home": home.render,
    "Company Profile": profile.render,
    "Screener": screener.render,
    "Peer Comparison": peers.render,
    "Trend Analysis": trends.render,
    "Sector Analysis": sectors.render,
    "Capital Allocation": capital.render,
    "Annual Reports": reports.render,
}

st.sidebar.title("Nifty 100 Analytics")
st.session_state["selected_year"] = st.sidebar.selectbox(
    "Financial year",
    list(range(2019, 2025)),
    index=5,
    key="global_year_selector",
)
page_name = st.sidebar.radio("Screen", list(PAGES.keys()), key="dashboard_screen")

PAGES[page_name]()
