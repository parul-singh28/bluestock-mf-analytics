import sys
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import get_companies


@st.cache_data(ttl=3600)
def _report_status(url):
    try:
        response = requests.head(url, timeout=2, allow_redirects=True)
        return response.status_code
    except Exception:
        return None

def render():
    st.title("Annual Reports")

    companies_df = get_companies()
    search = st.text_input("Search company", key="report_search")

    if search:
        matches = companies_df[
            companies_df["name"].str.lower().str.contains(search.lower()) |
            companies_df["ticker"].str.lower().str.contains(search.lower())
        ]
    else:
        matches = companies_df.head(20)

    if matches.empty:
        st.info("No company found")
        return

    selected = st.selectbox("Company", [f"{row['name']} ({row['ticker']})" for _, row in matches.iterrows()], key="report_company")
    company = matches[matches["name"] + " (" + matches["ticker"] + ")" == selected].iloc[0]

    for year in company["report_years"]:
        url = f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{company['ticker']}_{year}.pdf"
        status_code = _report_status(url)
        if status_code == 404:
            st.error(f"{year} Report unavailable")
        else:
            st.link_button(f"{year} Annual Report", url)
