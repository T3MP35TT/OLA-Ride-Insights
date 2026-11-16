"""Always-visible navigation with page-aware context and quick metrics."""
from pathlib import Path
import base64
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
NAVIGATION=(
    ("EXECUTIVE",("Executive overview",)),
    ("OPERATIONS",("Ride analysis","Cancellations","Ratings")),
    ("REVENUE",("Revenue",)),
    ("DATA TOOLS",("SQL explorer","Data management")),
    ("INTEGRATIONS",("Power BI",)),
)

def _page_info(page,df,f):
    status=f.get("status"); outcome=df[status].astype("string").str.strip().str.casefold() if status else None
    total=len(df); success=outcome.eq("success") if outcome is not None else None
    if page=="Executive overview":
        return "CEO view of booking conversion, supply loss and completed booking value.",[("Bookings",f"{total:,}"),("Success rate",f"{success.sum()/total:.1%}" if total else "—")]
    if page=="Ride analysis":
        v,d=f.get("vehicle"),f.get("distance")
        top=df[v].value_counts().index[0] if v and len(df) else "—"
        avg=df.loc[success,d].mean() if d and success is not None and success.any() else None
        return "Compare vehicle demand and completed ride distance.",[("Top vehicle",str(top)),("Avg. completed distance",f"{avg:.1f}" if avg is not None else "—")]
    if page=="Revenue":
        value,pay=f.get("value"),f.get("payment")
        amount=df.loc[success,value].sum() if value and success is not None else None
        top=df.loc[success,pay].value_counts().index[0] if pay and success is not None and success.any() else "—"
        return "Booking-value view, filtered to successful records for completed value.",[("Completed value",f"{amount:,.0f}" if amount is not None else "—"),("Popular payment",str(top))]
    if page=="Cancellations":
        customer=int(outcome.eq("canceled by customer").sum()) if outcome is not None else 0
        driver=int(outcome.eq("canceled by driver").sum()) if outcome is not None else 0
        return "Cancellation reasons and incomplete trips are separated by source outcome.",[("Customer",f"{customer:,}"),("Driver",f"{driver:,}")]
    if page=="Ratings":
        c,d=f.get("customer_rating"),f.get("driver_rating")
        return "Ratings use observed feedback only; missing feedback stays missing.",[("Customer avg.",f"{df[c].mean():.2f}" if c else "—"),("Driver avg.",f"{df[d].mean():.2f}" if d else "—")]
    if page=="SQL explorer":
        return "Run a reviewed business question or a custom read-only SELECT against the local bookings table.",[("Query","Not run"),("SQL access","Read only")]
    if page=="Data management":
        return "Manage records in the isolated working copy; source and cleaned baseline stay protected.",[("Working copy","Baseline"),("Baseline rows",f"{total:,}")]
    if page=="Power BI":
        import os
        connected=bool(os.getenv("POWERBI_EMBED_URL",""))
        return "Open the authorized organization report when an embed URL is configured.",[("Connection","Ready" if connected else "Not configured")]
    return "OLA mobility analytics",[]

def set_sidebar_context(page,description,metrics):
    """Update page context after its filters/actions have been processed."""
    st.session_state["sidebar_page_context"]={"page":page,"description":description,"metrics":metrics}

def _select_page(page):
    st.session_state["active_page"]=page

def render_sidebar(df,fields=None) -> str:
    # Keep the navigation usable by callers on either the old one-argument
    # interface or the current page-aware interface.
    if fields is None:
        from utils.data import resolve_fields
        fields=resolve_fields(df)
    st.session_state.setdefault("active_page","Executive overview")
    valid_pages={page for _, pages in NAVIGATION for page in pages}
    if st.session_state.get("active_page") not in valid_pages:
        st.session_state["active_page"]="Executive overview"
    with st.sidebar:
        logo=ROOT/"images/Ola-Cabs-Logo.png"
        if logo.exists():
            encoded=base64.b64encode(logo.read_bytes()).decode("ascii")
            st.markdown(f"<div class='ola-sidebar-logo'><img src='data:image/png;base64,{encoded}' alt='OLA Cabs'></div>",unsafe_allow_html=True)
        st.markdown("<div class='ola-side-brand'>RIDE INSIGHTS<br><span>Mobility intelligence</span></div>",unsafe_allow_html=True)
        active=st.session_state.get("active_page","Executive overview")
        for section,pages in NAVIGATION:
            st.markdown(f"<div class='ola-nav-section'>{section}</div>",unsafe_allow_html=True)
            for page in pages:
                st.button(page,key=f"nav_{page.replace(' ','_')}",type="primary" if page==active else "secondary",width="stretch",on_click=_select_page,args=(page,))
    return st.session_state.get("active_page","Executive overview")

def render_sidebar_context(slot,df,fields,page):
    context=st.session_state.get("sidebar_page_context",{})
    if context.get("page")==page:
        description,metrics=context["description"],context["metrics"]
    else:
        description,metrics=_page_info(page,df,fields)
    with slot.container():
        st.markdown("<div class='ola-sidebar-divider'></div>",unsafe_allow_html=True)
        st.markdown("<div class='ola-context-title'>LIVE PAGE CONTEXT</div>",unsafe_allow_html=True)
        st.caption(description)
        for label,value in metrics:
            st.metric(label,value)
