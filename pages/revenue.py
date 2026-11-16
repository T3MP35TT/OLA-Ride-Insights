import streamlit as st
import plotly.express as px
import pandas as pd
from utils.charts import show_chart, show_insight
from utils.sidebar import set_sidebar_context

def render(df,f):
    value,status,payment,customer=f["value"],f["status"],f["payment"],f["customer_id"]
    if not value:
        st.warning("Booking value is unavailable.")
        return
    view=df
    controls=st.columns(2)
    if payment:
        choices=sorted(df[payment].dropna().astype(str).unique())
        selected=controls[0].multiselect("Payment methods",choices,default=choices,key="revenue_payments")
        view=view[view[payment].astype(str).isin(selected)]
    if f["vehicle"]:
        choices=sorted(df[f["vehicle"]].dropna().astype(str).unique())
        selected=controls[1].multiselect("Vehicle types",choices,default=choices,key="revenue_vehicles")
        view=view[view[f["vehicle"]].astype(str).isin(selected)]
    if view.empty:
        set_sidebar_context("Revenue","No records match the selected payment and vehicle filters.",[("Completed value","0"),("Rows","0")])
        st.warning("No bookings match these filters. Adjust the selection to continue.")
        return
    successful=view[status].astype("string").str.strip().str.casefold().eq("success") if status else None
    completed=view.loc[successful,value].sum() if successful is not None else None
    set_sidebar_context("Revenue","Context uses current payment and vehicle filters; completed value includes Success rows only.",[("Filtered rows",f"{len(view):,}"),("Completed value",f"{completed:,.0f}" if completed is not None else "—")])
    k=st.columns(3)
    k[0].metric("All-status booking value",f"{view[value].sum():,.0f}")
    k[1].metric("Completed booking value",f"{completed:,.0f}" if completed is not None else "—")
    k[2].metric("Average booking value",f"{view[value].mean():,.2f}")
    st.info("Completed booking value includes only records with status `Success`. The source does not define accounting recognition or currency units.")
    if payment and successful is not None and successful.any():
        payment_totals=view.loc[successful].groupby(payment)[value].sum().sort_values(ascending=False)
        lead=payment_totals.index[0]
        share=payment_totals.iloc[0]/completed*100 if completed else 0
        show_insight(st,f"{lead} contributes the largest share of completed booking value ({share:.1f}%). This is recorded booking value, not confirmed collected revenue or margin.")
    else:
        show_insight(st,"Use completed booking value for the successful segment; this dataset does not identify recognized revenue, costs or margin.")
    left,right=st.columns(2)
    if payment:
        with left:
            totals=view.loc[successful].groupby(payment)[value].sum().sort_values(ascending=False).reset_index() if successful is not None else view.groupby(payment)[value].sum().reset_index()
            show_chart(st,px.bar(totals,x=payment,y=value,title="Completed booking value by payment method"))
    if customer:
        with right:
            top=view.groupby(customer)[value].sum().nlargest(5).rename("Booking value").reset_index()
            show_chart(st,px.bar(top,x="Booking value",y=customer,orientation="h",title="Top five customers by recorded booking value"),
                       insight="These are account-level booking-value signals for the selected data only. The source has no customer demographics, preferences or lifetime history for personalized marketing claims.")
    if f["datetime"] and successful is not None:
        daily=view.loc[successful].assign(_date=view.loc[successful,f["datetime"]].dt.floor("D")).groupby("_date")[value].sum().reset_index()
        show_chart(st,px.area(daily,x="_date",y=value,title="Completed booking value over time"))
    if f["vehicle"] and successful is not None:
        by_vehicle=view.loc[successful].groupby(f["vehicle"])[value].sum().sort_values().rename("Completed booking value").reset_index()
        a,b=st.columns(2,gap="large")
        with a:
            show_chart(st,px.bar(by_vehicle,x="Completed booking value",y=f["vehicle"],orientation="h",color="Completed booking value",color_continuous_scale=["#D7DF23","#789900","#3178B5"],title="Completed booking value by vehicle"))
        with b:
            show_chart(st,px.histogram(view,x=value,color=status if status else None,marginal="box",nbins=35,title="Booking value distribution"))
    if payment:
        count=view[payment].value_counts().rename_axis("Payment method").reset_index(name="Bookings")
        show_chart(st,px.pie(count,names="Payment method",values="Bookings",hole=.55,title="Payment method mix"))
    if f.get("distance"):
        successful_rows=view.loc[successful].copy() if successful is not None else view.copy()
        columns=[f["distance"],value]+([f["vehicle"]] if f.get("vehicle") else [])
        paired=successful_rows[columns].copy()
        paired[[f["distance"],value]]=paired[[f["distance"],value]].apply(pd.to_numeric,errors="coerce")
        paired=paired.dropna(subset=[f["distance"],value])
        paired=paired.loc[paired[f["distance"]]>0]
        if len(paired)>1:
            correlation=paired[f["distance"]].corr(paired[value])
            plotted=paired.sample(min(len(paired),5000),random_state=42) if len(paired)>5000 else paired
            show_chart(st,px.scatter(plotted,x=f["distance"],y=value,color=f["vehicle"] if f.get("vehicle") else None,opacity=.55,
                                     title="Completed booking value versus ride distance"),
                       insight=f"Booking value and distance have a correlation of {correlation:.2f} across {len(paired):,} successful trips. The source contains no surge flag or fare breakdown, so this pattern cannot measure surge effectiveness.")
