"""Executive decision dashboard: conversion, supply, value and experience."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.charts import show_chart
from utils.sidebar import set_sidebar_context

PAGE = "Executive overview"
STATUS_COLORS = {
    "Success": "#849900",
    "Canceled by Customer": "#E89E25",
    "Canceled by Driver": "#D46A42",
    "Driver Not Found": "#7652A1",
}


def _insight_card(label, headline, detail, accent="#849900"):
    st.markdown(
        f"<div style='height:100%;padding:1rem 1.1rem;border-radius:15px;"
        f"border:1px solid #e8eacb;border-left:4px solid {accent};"
        "background:linear-gradient(135deg,rgba(248,250,226,.88),rgba(255,255,255,.94));"
        "box-shadow:0 5px 18px rgba(45,55,0,.045)'>"
        f"<div style='font-size:.68rem;font-weight:800;letter-spacing:.12em;color:#73775d'>{label.upper()}</div>"
        f"<div style='font-size:1.03rem;font-weight:750;color:#202217;margin:.35rem 0'>{headline}</div>"
        f"<div style='font-size:.87rem;line-height:1.5;color:#62664c'>{detail}</div></div>",
        unsafe_allow_html=True,
    )


def render(df, f):
    status, value, vehicle = f.get("status"), f.get("value"), f.get("vehicle")
    dt = f.get("datetime")
    st.markdown("### Board snapshot")
    st.caption("A decision-focused view of booking conversion, supply loss, completed booking value and customer experience.")

    filters = st.columns(3)
    view = df.copy()
    selected_vehicles = selected_statuses = None
    if vehicle:
        options = sorted(df[vehicle].dropna().astype(str).unique())
        selected_vehicles = filters[0].multiselect("Vehicle types", options, default=options, key="overview_vehicles")
        view = view[view[vehicle].astype(str).isin(selected_vehicles)]
    if status:
        options = sorted(df[status].dropna().astype(str).unique())
        selected_statuses = filters[1].multiselect("Booking outcomes", options, default=options, key="overview_statuses")
        view = view[view[status].astype(str).isin(selected_statuses)]
    date_range = None
    if dt and dt in view:
        dates = pd.to_datetime(df[dt], errors="coerce").dropna()
        if not dates.empty:
            date_range = filters[2].date_input(
                "Analysis date range", value=(dates.min().date(), dates.max().date()),
                min_value=dates.min().date(), max_value=dates.max().date(), key="overview_dates",
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                view = view[pd.to_datetime(view[dt], errors="coerce").dt.date.between(*date_range)]

    if view.empty:
        set_sidebar_context(PAGE, "No bookings match the selected executive dashboard filters.", [("Filtered bookings", "0"), ("Decision status", "No data")])
        st.warning("No bookings match these filters. Adjust the selections to continue.")
        return

    outcomes = view[status].astype("string").str.strip().str.casefold() if status else pd.Series("unknown", index=view.index)
    total = len(view)
    successful = outcomes.eq("success")
    success_count = int(successful.sum())
    customer_count = int(outcomes.eq("canceled by customer").sum())
    driver_count = int(outcomes.eq("canceled by driver").sum())
    not_found_count = int(outcomes.eq("driver not found").sum())
    failed = total - success_count
    completed_value = pd.to_numeric(view.loc[successful, value], errors="coerce").sum() if value else None
    success_rate = success_count / total if total else 0
    failure_rate = failed / total if total else 0
    customer_rate = customer_count / total if total else 0
    driver_rate = driver_count / total if total else 0
    not_found_rate = not_found_count / total if total else 0

    metrics = st.columns(5)
    metrics[0].metric("Bookings in scope", f"{total:,}")
    metrics[1].metric("Successful rides", f"{success_count:,}", f"{success_rate:.1%} conversion")
    metrics[2].metric("Unfulfilled demand", f"{failed:,}", f"{failure_rate:.1%} of bookings", delta_color="inverse")
    metrics[3].metric("Driver not found", f"{not_found_count:,}", f"{not_found_rate:.1%} of bookings", delta_color="inverse")
    metrics[4].metric("Completed booking value", f"{completed_value:,.0f}" if completed_value is not None else "—", "Successful bookings · source units")

    set_sidebar_context(
        PAGE,
        f"Current filters cover {total:,} bookings. Value is summed only for successful rides and is not audited recognized revenue.",
        [("Success rate", f"{success_rate:.1%}"), ("Driver not found", f"{not_found_count:,}"), ("Completed value", f"{completed_value:,.0f}" if completed_value is not None else "—")],
    )

    st.markdown("### Executive readout")
    a, b, c = st.columns(3, gap="medium")
    if driver_rate >= customer_rate:
        gap_pp = (driver_rate - customer_rate) * 100
        _insight_card("Supply & fulfillment", f"Driver-side cancellations exceed customer cancellations by {gap_pp:.1f} pp.", f"Driver cancellations: {driver_count:,} ({driver_rate:.1%}); driver not found: {not_found_count:,} ({not_found_rate:.1%}). Review driver availability, acceptance and pickup coverage by hour.", "#D46A42")
    else:
        gap_pp = (customer_rate - driver_rate) * 100
        _insight_card("Customer demand", f"Customer cancellations exceed driver cancellations by {gap_pp:.1f} pp.", f"Customer cancellations: {customer_count:,} ({customer_rate:.1%}). Break down pickup delays and customer reasons before changing supply incentives.", "#E89E25")
    _insight_card("Conversion opportunity", f"{failed:,} bookings did not become successful rides.", f"The observed success rate is {success_rate:.1%}. Treat cancellations and driver-not-found outcomes as separate operational levers.", "#7652A1")
    _insight_card("Financial lens", f"{completed_value:,.0f} booking-value units on successful rides." if completed_value is not None else "Booking value is unavailable.", "Use this as completed booking value, not recognized revenue. The source does not define currency units or accounting treatment.", "#849900")
    st.caption("Decision guidance is descriptive: this workbook covers July 2024 only, so it cannot establish month-over-month change, causality or intervention impact.")

    st.markdown("### Demand, outcomes & operating levers")
    if status:
        counts = view[status].fillna("Missing").value_counts().rename_axis("Booking outcome").reset_index(name="Bookings")
        counts = counts.sort_values("Bookings")
        show_chart(
            st,
            px.bar(counts, x="Bookings", y="Booking outcome", orientation="h", color="Booking outcome",
                   color_discrete_map=STATUS_COLORS, title="Where bookings end", hover_data={"Bookings": ":,"}),
            insight=f"Successful rides convert {success_rate:.1%} of bookings; {not_found_count:,} more were lost to driver-not-found outcomes.",
        )

    if dt:
        date_frame = view.copy()
        date_frame[dt] = pd.to_datetime(date_frame[dt], errors="coerce")
        date_frame["_date"] = date_frame[dt].dt.floor("D")
        date_frame = date_frame.dropna(subset=["_date"])
        if not date_frame.empty:
            daily = date_frame.groupby("_date").agg(Bookings=("_date", "size")).reset_index()
            if status:
                success_daily = date_frame.assign(_success=outcomes.loc[date_frame.index].eq("success").astype(int)).groupby("_date")["_success"].mean().mul(100)
                daily["Success rate (%)"] = daily["_date"].map(success_daily)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=daily["_date"], y=daily["Bookings"], name="Bookings", marker_color="#D7DF23", opacity=.78, yaxis="y"))
            if "Success rate (%)" in daily:
                fig.add_trace(go.Scatter(x=daily["_date"], y=daily["Success rate (%)"], name="Success rate", mode="lines+markers", line={"color":"#25271D","width":3}, marker={"size":7}, yaxis="y2"))
            fig.update_layout(title="Daily demand and booking conversion", xaxis_title="Booking date", yaxis={"title":"Bookings"}, yaxis2={"title":"Success rate (%)","overlaying":"y","side":"right","range":[0,100]}, legend={"orientation":"h","y":1.12})
            peak = daily.loc[daily["Bookings"].idxmax()]
            show_chart(st, fig, insight=f"Peak day in the selected period: {peak['_date'].date():%d %b} with {int(peak['Bookings']):,} bookings. Compare daily conversion before reallocating supply.")

        if status:
            hourly = date_frame.assign(_hour=date_frame[dt].dt.hour, _outcome=outcomes.loc[date_frame.index].fillna("Missing"))
            hourly_counts = hourly.groupby(["_hour", "_outcome"]).size().rename("Bookings").reset_index()
            show_chart(
                st,
                px.bar(hourly_counts, x="_hour", y="Bookings", color="_outcome", barmode="stack", title="Demand and lost bookings by hour",
                       color_discrete_map=STATUS_COLORS, labels={"_hour":"Hour of day","_outcome":"Booking outcome"}),
                insight="Use the busiest hours with the highest driver-not-found or driver-cancellation share to target dispatch coverage.",
            )

    if vehicle and status:
        vehicle_rows = view.assign(_success=successful.astype(int)).groupby(vehicle).agg(Bookings=(status,"size"), Successful=("_success","sum")).reset_index()
        vehicle_rows["Success rate (%)"] = vehicle_rows["Successful"].div(vehicle_rows["Bookings"]).mul(100)
        fig = px.scatter(vehicle_rows, x="Bookings", y="Success rate (%)", size="Successful", color=vehicle,
                         hover_name=vehicle, hover_data={"Successful":":,","Bookings":":,","Success rate (%)":":.1f"},
                         color_discrete_sequence=["#849900","#25271D","#E89E25","#7652A1","#D46A42","#6E9AC4","#AAB1A1"],
                         title="Vehicle demand versus conversion")
        fig.update_traces(marker={"line":{"width":1,"color":"white"},"opacity":.86})
        fig.update_xaxes(title="Bookings")
        fig.update_yaxes(title="Successful booking rate (%)", range=[0,100])
        strongest = vehicle_rows.sort_values("Success rate (%)", ascending=False).iloc[0]
        show_chart(st, fig, insight=f"{strongest[vehicle]} leads the selected vehicles on conversion at {strongest['Success rate (%)']:.1f}%; check volume and mix before scaling capacity.")

    if value and f.get("payment"):
        payment = f["payment"]
        value_by_payment = view.loc[successful].groupby(payment)[value].sum().sort_values(ascending=False).rename("Completed booking value").reset_index()
        show_chart(st, px.bar(value_by_payment, x="Completed booking value", y=payment, orientation="h", color="Completed booking value",
                               color_continuous_scale=["#D7DF23","#849900","#425600"], title="Completed booking value by payment method"),
                   insight="Mix reflects successful rides only. Payment value is a booking metric, not audited cash collection or recognized revenue.")

    pickup = f.get("pickup")
    if pickup and status:
        supply_gaps = view.loc[outcomes.eq("driver not found"), pickup].fillna("Location missing").value_counts().head(12).rename_axis("Pickup location").reset_index(name="Driver not found")
        if not supply_gaps.empty:
            lead = supply_gaps.iloc[0]
            show_chart(st, px.bar(supply_gaps.sort_values("Driver not found"), x="Driver not found", y="Pickup location", orientation="h",
                                   color="Driver not found", color_continuous_scale=["#D7DF23","#E89E25","#7652A1"], title="Pickup zones with highest unmatched demand"),
                       insight=f"{lead['Pickup location']} has the most driver-not-found bookings ({int(lead['Driver not found']):,}); assess time-of-day concentration before changing zone incentives.")

    if value:
        amounts=pd.to_numeric(view[value],errors="coerce").dropna()
        if len(amounts)>3:
            q1,q3=amounts.quantile([.25,.75])
            upper=q3+1.5*(q3-q1)
            high_value=view.loc[pd.to_numeric(view[value],errors="coerce")>upper]
            st.markdown("### Anomaly review")
            flagged,threshold=st.columns(2)
            flagged.metric("High-value review flags",f"{len(high_value):,}",f"{len(high_value)/len(amounts):.1%} of records")
            threshold.metric("IQR review threshold",f"{upper:,.0f}","Q3 + 1.5 × IQR · source units")
            st.caption("These statistical outlier flags support review only. They are not evidence of fraud, pricing abuse or incorrect records.")
            # The booking values have a long tail, so a full-range histogram
            # hides the shape of the main distribution. Show the flagged
            # records directly, grouped by outcome, for a readable review view.
            if status:
                flagged_by_outcome = high_value.assign(
                    _outcome=high_value[status].fillna("Missing").astype(str)
                ).groupby("_outcome").size().rename("Flagged bookings").reset_index()
                outcome_order = (
                    flagged_by_outcome.sort_values("Flagged bookings", ascending=True)["_outcome"].tolist()
                )
                review_plot = px.bar(
                    flagged_by_outcome,
                    x="Flagged bookings",
                    y="_outcome",
                    orientation="h",
                    text="Flagged bookings",
                    category_orders={"_outcome": outcome_order},
                    color="_outcome",
                    color_discrete_map=STATUS_COLORS,
                    title="High-value review flags by booking outcome",
                    labels={"_outcome": "Booking outcome"},
                )
                review_plot.update_traces(texttemplate="%{x:,}", textposition="outside", cliponaxis=False)
                review_plot.update_layout(showlegend=False, xaxis_title="Bookings above review threshold")
            else:
                review_plot = px.bar(
                    pd.DataFrame({"Review group": ["Above IQR threshold"], "Flagged bookings": [len(high_value)]}),
                    x="Flagged bookings", y="Review group", orientation="h", text="Flagged bookings",
                    title="High-value records above the review threshold",
                )
                review_plot.update_traces(texttemplate="%{x:,}", textposition="outside", cliponaxis=False)
            show_chart(st,review_plot,insight=f"{len(high_value):,} selected records exceed the IQR review threshold of {upper:,.0f}. Check source records and trip context before taking action.")

    st.markdown("### Board interpretation")
    with st.container(border=True):
        st.markdown("**Recommended operating focus**")
        st.write(f"1. Diagnose the {not_found_rate:.1%} driver-not-found share by pickup zone and hour; pilot targeted driver positioning where volume is concentrated.")
        st.write(f"2. Separate driver cancellations ({driver_rate:.1%}) from customer cancellations ({customer_rate:.1%}) and address their distinct leading reasons in the Cancellations page.")
        st.write("3. Track success rate, driver-not-found rate and completed booking value together after any intervention. A single month is a baseline, not evidence of sustained improvement.")
        st.caption("Ratings, distance and payment behavior are available in their dedicated pages for deeper diagnosis. The supplied dataset does not include cost, margin, driver hours, surge, or a comparable prior period.")
