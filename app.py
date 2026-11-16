"""OLA Ride Insights Streamlit application entry point."""
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="OLA Ride Insights", page_icon="🚕", layout="wide", initial_sidebar_state="expanded")

from utils.data import load_data, resolve_fields
from utils.theme import apply_theme, render_brand_header
from utils.sidebar import render_sidebar, render_sidebar_context
from pages import (
    overview,
    rides,
    cancellations,
    ratings,
    revenue,
    sql_explorer,
    data_management,
    power_bi,
)

ROOT = Path(__file__).resolve().parent
apply_theme()
try:
    df = load_data()
except Exception as exc:
    st.error(f"Unable to load the ride dataset: {exc}")
    st.stop()

fields = resolve_fields(df)
page = render_sidebar(df, fields)
sidebar_context=st.sidebar.empty()
render_brand_header(page)

PAGE_RENDERERS = {
    "Executive overview": overview.render,
    "Ride analysis": rides.render,
    "Revenue": revenue.render,
    "Cancellations": cancellations.render,
    "Ratings": ratings.render,
    "SQL explorer": sql_explorer.render,
    "Data management": data_management.render,
    "Power BI": power_bi.render,
}
PAGE_RENDERERS[page](df, fields)
render_sidebar_context(sidebar_context,df,fields,page)
