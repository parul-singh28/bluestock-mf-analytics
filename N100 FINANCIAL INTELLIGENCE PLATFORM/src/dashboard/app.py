import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.valuation import build_valuation_outputs

build_valuation_outputs()

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Nifty 100 Analytics")
years = [2024, 2023, 2022, 2021, 2020, 2019]
st.session_state.selected_year = st.sidebar.selectbox(
    "Select Financial Year",
    years,
    index=0,
    key="selected_year",
)

st.title("Nifty 100 Analytics")
st.info("Open the pages from the left sidebar: Home, Profile, Screener, Peers, Trends, Sectors, Capital, Reports.")