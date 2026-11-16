import streamlit as st
import plotly.express as px
import pandas as pd
from utils.charts import show_chart, show_insight
from utils.sidebar import set_sidebar_context

def render(df,f):
    status=f["status"]
    if not status: st.warning("Booking status field is unavailable."); return
    view=df
    if f["vehicle"]:
        choices=sorted(df[f["vehicle"]].dropna().astype(str).unique()); selected=st.multiselect("Vehicle types",choices,default=choices,key="cancel_vehicles"); view=view[view[f["vehicle"]].astype(str).isin(selected)]
    if view.empty:
        set_sidebar_context("Cancellations","No bookings match the selected vehicle filter.",[("Filtered bookings","0"),("Cancellation rate","—")])
        st.warning("No bookings match these filters. Adjust the vehicle selection to continue.")
        return
    outcomes=view[status].astype("string").str.strip().str.casefold()
    total=len(view); customer=int(outcomes.eq("canceled by customer").sum()); driver=int(outcomes.eq("canceled by driver").sum()); not_found=int(outcomes.eq("driver not found").sum())
    k=st.columns(4); k[0].metric("Bookings",f"{total:,}"); k[1].metric("Customer cancellations",f"{customer:,}",f"{customer/total:.2%}" if total else None); k[2].metric("Driver cancellations",f"{driver:,}",f"{driver/total:.2%}" if total else None); k[3].metric("Driver not found",f"{not_found:,}",f"{not_found/total:.2%}" if total else None)
    set_sidebar_context("Cancellations",f"Rates are recalculated across the {total:,} filtered bookings.",[("Customer canceled",f"{customer:,}"),("Driver canceled",f"{driver:,}")])
    top_side="driver" if driver>=customer else "customer"
    top_count=max(driver,customer)
    show_insight(st,f"{top_side.title()} cancellations are the larger intervention area in this selection ({top_count:,} bookings, {top_count/total:.1%} of all filtered bookings). Driver-not-found remains separate at {not_found:,}.")
    st.caption("Each rate uses all bookings as denominator. Driver-not-found outcomes are not classified as cancellations.")
    left,right=st.columns(2)
    for side,key,title,container in [("canceled by customer","customer_reason","Customer cancellation reasons",left),("canceled by driver","driver_reason","Driver cancellation reasons",right)]:
        col=f[key]
        if col:
            with container:
                values=view.loc[outcomes.eq(side),col].fillna("Reason missing").value_counts().rename_axis("Reason").reset_index(name="Bookings")
                show_chart(st,px.bar(values,x="Bookings",y="Reason",orientation="h",title=title))
    if f["datetime"]:
        canceled=view.loc[outcomes.isin(["canceled by customer","canceled by driver"])].copy()
        canceled["Booking hour"]=canceled[f["datetime"]].dt.hour
        hourly=canceled.groupby(["Booking hour",status]).size().rename("Canceled bookings").reset_index()
        show_chart(st,px.line(hourly,x="Booking hour",y="Canceled bookings",color=status,markers=True,
                               color_discrete_map={"Canceled by Customer":"#E87947","Canceled by Driver":"#7652A1"},title="Cancellation trends by hour"))
    if f["vehicle"]:
        counts=pd.crosstab(view[f["vehicle"]],view[status],normalize="index").mul(100).reset_index().melt(id_vars=f["vehicle"],var_name="Booking outcome",value_name="Share (%)")
        show_chart(st,px.bar(counts,x=f["vehicle"],y="Share (%)",color="Booking outcome",barmode="stack",title="Outcome mix by vehicle type"))
    if f["incomplete"]:
        incomplete=view[f["incomplete"]].astype("string").str.casefold().eq("yes")
        st.subheader(f"Incomplete rides ({int(incomplete.sum()):,})")
        show_insight(st,f"{int(incomplete.sum()):,} records carry the source incomplete-ride flag ({incomplete.mean():.1%} of this selection). Review recorded reasons before treating them as cancellations.")
        if f["incomplete_reason"]:
            reasons=view.loc[incomplete,f["incomplete_reason"]].fillna("Reason missing").value_counts().rename_axis("Reason").reset_index(name="Bookings")
            show_chart(st,px.bar(reasons,x="Reason",y="Bookings",title="Incomplete ride reasons"))
