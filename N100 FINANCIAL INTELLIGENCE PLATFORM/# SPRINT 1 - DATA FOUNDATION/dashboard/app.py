import importlib.util
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

PAGES = [
    ("Home", "Pages/01_home.py"),
    ("Profile", "Pages/02_profile.py"),
    ("Screener", "Pages/03_screener.py"),
    ("Peers", "Pages/04_peers.py"),
    ("Trends", "Pages/05_trends.py"),
    ("Sectors", "Pages/06_sectors.py"),
    ("Capital", "Pages/07_capital.py"),
    ("Reports", "Pages/08_reports.py"),
]

def load_page(path):
    spec = importlib.util.spec_from_file_location("page_module", str(ROOT / path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load page: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

if "selected_year" not in st.session_state:
    st.session_state.selected_year = 2024

st.sidebar.title("Nifty 100 Analytics")
years = [2024, 2023, 2022, 2021, 2020, 2019]
st.session_state.selected_year = st.sidebar.selectbox(
    "Select Financial Year",
    options=years,
    index=years.index(st.session_state.selected_year),
)

selected_page = st.sidebar.radio("Navigate", [p[0] for p in PAGES], key="page_nav")
page_path = next(path for name, path in PAGES if name == selected_page)
module = load_page(page_path)
module.render()