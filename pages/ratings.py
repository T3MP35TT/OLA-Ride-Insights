"""Interactive, side-by-side customer and driver feedback analysis."""
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.charts import show_chart, show_insight, show_table
from utils.sidebar import set_sidebar_context

RATER_COLORS={"Customer":"#789900","Driver":"#3178B5"}

def render(df,f):
    customer,driver=f["customer_rating"],f["driver_rating"]
    if not customer or not driver:
        st.warning("Both customer and driver rating fields are required for this comparison.")
        return

    st.markdown("#### Compare feedback")
    controls=st.columns([1.35,1.0,1.0])
    view=df
    if f["vehicle"]:
        vehicles=sorted(df[f["vehicle"]].dropna().astype(str).unique())
        selected=controls[0].multiselect("Vehicle types",vehicles,default=vehicles,key="ratings_vehicles")
        view=view[view[f["vehicle"]].astype(str).isin(selected)]
    paired_only=controls[2].toggle("Paired ratings only",value=False,key="ratings_paired_only",help="Use only trips that have both a customer and a driver rating.")
    observed=pd.concat([view[customer].dropna(),view[driver].dropna()])
    if observed.empty:
        st.info("No ratings are available for this selection.")
        return
    low,high=float(observed.min()),float(observed.max())
    step=.1
    selected_range=controls[1].slider("Rating range",min_value=low,max_value=high,value=(low,high),step=step,key="ratings_range")
    view=view.copy()
    view[customer]=view[customer].where(view[customer].between(*selected_range))
    view[driver]=view[driver].where(view[driver].between(*selected_range))
    if paired_only:
        view=view[view[customer].notna() & view[driver].notna()]
    if view.empty:
        st.warning("No ratings match these filters. Widen the rating range or select more vehicles.")
        return

    customer_values=view[customer].dropna()
    driver_values=view[driver].dropna()
    both=view[[customer,driver]].dropna()
    customer_mean=customer_values.mean()
    driver_mean=driver_values.mean()
    gap=customer_mean-driver_mean
    within_half=(both[customer].sub(both[driver]).abs().le(.5).mean()*100) if len(both) else 0

    k=st.columns(4)
    k[0].metric("Customer average",f"{customer_mean:.2f}",f"{len(customer_values):,} ratings")
    k[1].metric("Driver average",f"{driver_mean:.2f}",f"{len(driver_values):,} ratings")
    k[2].metric("Average gap",f"{gap:+.2f}","Customer − driver")
    k[3].metric("Within 0.5 points",f"{within_half:.1f}%",f"{len(both):,} paired trips")
    set_sidebar_context("Ratings",f"Showing {len(view):,} records; ratings filtered to {selected_range[0]:.1f}–{selected_range[1]:.1f}."+(" Paired feedback only." if paired_only else ""),[("Customer avg.",f"{customer_mean:.2f}"),("Driver avg.",f"{driver_mean:.2f}"),("Paired trips",f"{len(both):,}")])
    coverage=len(both)/len(view)*100 if len(view) else 0
    higher="customer" if gap>0 else "driver" if gap<0 else "neither rater"
    show_insight(st,f"Average ratings differ by {abs(gap):.2f} points in favor of {higher}; {coverage:.1f}% of filtered records have paired feedback. Interpret averages alongside this coverage.")

    summary=pd.DataFrame()
    left,right=st.columns([1.05,1.2],gap="large")
    with left:
        st.markdown("#### Rating distribution")
        # Use matched pairs when selected; otherwise keep all feedback in each series.
        rating_rows=[]
        for label,col in [("Customer",customer),("Driver",driver)]:
            values=view[col].dropna().round(1)
            counts=values.value_counts().sort_index()
            denom=int(counts.sum()) or 1
            rating_rows.extend({"Rater":label,"Rating":f"{rating:.1f}","Count":int(count),"Share of feedback (%)":count/denom*100} for rating,count in counts.items())
        dist=pd.DataFrame(rating_rows)
        order=[f"{x:.1f}" for x in sorted(pd.concat([customer_values,driver_values]).round(1).unique())]
        fig=px.bar(dist,x="Rating",y="Count",color="Rater",barmode="group",category_orders={"Rating":order},
                   color_discrete_map=RATER_COLORS,hover_data={"Share of feedback (%)":":.1f","Count":":,"},
                   title="How often each rating was given")
        fig.update_layout(legend_title_text="Feedback from")
        show_chart(st,fig)

    with right:
        st.markdown("#### Average rating by vehicle")
        vehicle=f["vehicle"]
        if vehicle:
            summary=view.groupby(vehicle).agg(
                Customer=(customer,"mean"),Driver=(driver,"mean"),
                Customer_feedback=(customer,"count"),Driver_feedback=(driver,"count"),
            ).reset_index()
            long=summary.melt(id_vars=vehicle,value_vars=["Customer","Driver"],var_name="Rater",value_name="Average rating")
            fig=px.bar(long,x="Average rating",y=vehicle,color="Rater",barmode="group",orientation="h",
                       text_auto=".2f",color_discrete_map=RATER_COLORS,
                       hover_data={"Average rating":":.3f"},title="Customer and driver averages by vehicle")
            fig.update_xaxes(range=[0,5],title="Average rating (full 0–5 axis)")
            fig.update_layout(legend_title_text="Feedback from",yaxis={"categoryorder":"total ascending"})
            show_chart(st,fig)
            summary["Customer–driver gap"]=summary["Customer"]-summary["Driver"]
            summary=summary.rename(columns={vehicle:"Vehicle type","Customer":"Customer avg.","Driver":"Driver avg.","Customer_feedback":"Customer ratings","Driver_feedback":"Driver ratings"})
            best=summary.loc[summary["Customer–driver gap"].abs().idxmax()]
            show_table(st,summary.sort_values("Vehicle type"),"Rating comparison by vehicle",insight=f"{best['Vehicle type']} has the largest absolute customer–driver gap ({best['Customer–driver gap']:+.2f} points). Feedback counts differ by vehicle, so compare coverage before ranking service quality.",hide_index=True)
        else:
            st.info("Vehicle type is not available in this dataset.")

    st.markdown("#### Where do customer and driver ratings agree?")
    if both.empty:
        st.info("No trips have both ratings for this selection.")
        return
    grid=pd.crosstab(both[customer].round(1),both[driver].round(1)).sort_index().sort_index(axis=1)
    heat=px.imshow(grid,text_auto=True,aspect="auto",color_continuous_scale=["#F4F6D8","#D7DF23","#789900","#245780"],
                   labels={"x":"Driver rating","y":"Customer rating","color":"Trips"},
                   title="Paired rating counts — hover for exact trip totals")
    heat.update_xaxes(title="Driver rating")
    heat.update_yaxes(title="Customer rating")
    show_chart(st,heat)
    exact=(both[customer].round(1).eq(both[driver].round(1)).mean()*100)
    correlation=both[customer].corr(both[driver])
    a,b,c=st.columns(3)
    a.metric("Exact agreement",f"{exact:.1f}%")
    b.metric("Rating correlation",f"{correlation:.3f}")
    c.metric("Trips compared",f"{len(both):,}")
    show_insight(st,f"Exact paired agreement is {exact:.1f}% and correlation is {correlation:.3f} across {len(both):,} trips; neither metric indicates which rater is correct.")
    if not summary.empty:
        st.download_button("Download vehicle rating comparison",summary.to_csv(index=False).encode("utf-8"),"ola_vehicle_rating_comparison.csv","text/csv")
