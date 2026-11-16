import streamlit as st
import plotly.express as px
import pandas as pd
from utils.charts import show_chart, show_insight, show_table
from utils.sidebar import set_sidebar_context

def render(df,f):
    vehicle,distance,value=f["vehicle"],f["distance"],f["value"]
    status=f["status"]; view=df
    controls=st.columns(2)
    if vehicle:
        options=sorted(df[vehicle].dropna().astype(str).unique()); selected=controls[0].multiselect("Vehicle types",options,default=options,key="rides_vehicles")
        view=view[view[vehicle].astype(str).isin(selected)]
    if status:
        options=sorted(df[status].dropna().astype(str).unique()); selected=controls[1].multiselect("Booking outcomes",options,default=options,key="rides_statuses")
        view=view[view[status].astype(str).isin(selected)]
    if view.empty:
        set_sidebar_context("Ride analysis","No records match the selected vehicle and booking outcome filters.",[("Filtered rides","0"),("Vehicles",f"{len(selected) if vehicle else 0}")])
        st.warning("No rides match these filters. Adjust the selection to continue.")
        return
    set_sidebar_context("Ride analysis",f"Showing {len(view):,} records for the selected vehicles and outcomes.",[("Filtered rides",f"{len(view):,}"),("Vehicles",f"{view[vehicle].nunique() if vehicle else 0}")])
    if vehicle and distance:
        leading=view.groupby(vehicle)[distance].agg(["count","median"])
        top=leading["count"].idxmax()
        show_insight(st,f"{top} has the most rides in this selection ({leading.loc[top,'count']:,}); its median ride distance is {leading.loc[top,'median']:.1f} source units.")
    left,right=st.columns(2)
    if vehicle and distance:
        with left: show_chart(st,px.box(view,x=vehicle,y=distance,title="Ride distance by vehicle type",points=False))
        with right: show_chart(st,px.histogram(view,x=vehicle,title="Ride volume by vehicle",color=vehicle))
        summary=view.groupby(vehicle)[distance].agg(["count","mean","median"]).reset_index()
        st.subheader("Vehicle distance summary")
        lead=summary.loc[summary["count"].idxmax()]
        show_table(st,summary,"Vehicle distance summary",insight=f"{lead[vehicle]} has the most observations ({int(lead['count']):,}); compare medians as well as averages because ride distances may be skewed.",hide_index=True)
        a,b=st.columns(2,gap="large")
        with a:
            mean_distance=view.groupby(vehicle)[distance].mean().rename("Average distance").reset_index()
            show_chart(st,px.bar(mean_distance,x="Average distance",y=vehicle,orientation="h",color="Average distance",color_continuous_scale=["#D7DF23","#789900","#3178B5"],title="Average ride distance by vehicle"))
        if f["pickup"]:
            with b:
                pickup=view[f["pickup"]].value_counts().head(15).rename_axis("Pickup location").reset_index(name="Bookings")
                show_chart(st,px.bar(pickup,x="Bookings",y="Pickup location",orientation="h",color="Bookings",color_continuous_scale=["#F3C969","#E87947","#8E4B83"],title="Top pickup locations"))
        distance_leaders=view.groupby(vehicle)[distance].sum().nlargest(5).sort_values().rename("Total ride distance").reset_index()
        show_chart(st,px.bar(distance_leaders,x="Total ride distance",y=vehicle,orientation="h",color="Total ride distance",title="Top five vehicle types by total ride distance"),
                   insight=f"{distance_leaders.iloc[-1][vehicle]} contributes the most distance among the five leaders. Total distance combines volume and trip length; it is not a per-ride efficiency measure.")
        if f.get("datetime"):
            day_view=view[[f["datetime"],distance]].copy()
            day_view["Booking date"]=pd.to_datetime(day_view[f["datetime"]],errors="coerce").dt.floor("D")
            day_view=day_view.dropna(subset=["Booking date",distance])
            if not day_view.empty:
                daily_distance=day_view.groupby("Booking date")[distance].agg(["count","mean","sum"]).reset_index()
                show_chart(st,px.line(daily_distance,x="Booking date",y="mean",markers=True,title="Daily average ride distance"),
                           insight=f"Daily average distance ranges from {daily_distance['mean'].min():.1f} to {daily_distance['mean'].max():.1f} source units. Check trip counts alongside the average before interpreting day-to-day movement.")
    else: st.warning("Vehicle or ride-distance field is unavailable; inspect the data dictionary.")
    if vehicle and value:
        show_chart(st,px.box(view,x=vehicle,y=value,title="Booking value by vehicle type",points=False))
