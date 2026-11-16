import os
import streamlit as st
from utils.sidebar import set_sidebar_context
from utils.charts import show_insight

# Default report supplied for the OLA Ride Insights dashboard. An environment
# variable can still override it for deployments using a different report.
DEFAULT_POWERBI_EMBED_URL = (
    "https://app.powerbi.com/view?"
    "r=eyJrIjoiYWE2YWQ1MTUtZTUzZC00Y2M5LTg3ODgtZjRiODE5NzJiYzAzIiwidCI6"
    "IjY3NmIyNGNmLWM4OTItNDE1Ny1iMzM1LTRjYTM0NjBmNDMwOCJ9"
)

def render(df,f):
    url=os.getenv("POWERBI_EMBED_URL",DEFAULT_POWERBI_EMBED_URL).strip()
    set_sidebar_context("Power BI","Power BI report integration status.",[("Embed URL","Configured" if url else "Not configured"),("Dataset rows",f"{len(df):,}")])
    if url:
        show_insight(st,"The report frame is loaded from the configured organization URL. Confirm the report’s filters and refresh time in Power BI before using it for decisions.")
        st.components.v1.iframe(url,height=780,scrolling=True)
        st.markdown(f"[Open the report in Power BI]({url})")
    else:
        st.info("Power BI report is not configured yet.")
        show_insight(st,"No report is embedded in this session; use Executive overview and the analytics pages for the current local dataset.")
        st.markdown("1. Build and publish the report through your approved organizational workspace.\n2. Add the authorized embed URL as `POWERBI_EMBED_URL`.\n3. Restart Streamlit to load the report.")
        st.caption("Use organization-approved access for private reports. Do not place embed tokens or credentials in source code.")
