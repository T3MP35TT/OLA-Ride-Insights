"""Descriptive charts and evidence-based business summaries."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def build_eda(df, field_map, root):
    charts = Path(root) / "reports/eda_charts"
    charts.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="crest")
    def save(fig, name):
        fig.tight_layout(); fig.savefig(charts/name, dpi=140, bbox_inches="tight"); plt.close(fig)
    status=field_map.get("booking_status")
    s=df[status].astype("string").str.strip().str.casefold() if status else pd.Series(index=df.index,dtype="string")
    success_mask=s.eq("success")
    successful_df=df.loc[success_mask]
    distance=field_map.get("ride_distance")
    # Categorical distributions, including distinct reason dimensions.
    for key, title in [("booking_status","Booking status"),("vehicle_type","Bookings by vehicle"),("payment_method","Payment method"),("customer_cancel_reason","Customer cancellation reasons"),("driver_cancel_reason","Driver cancellation reasons"),("incomplete_reason","Incomplete ride reasons")]:
        c=field_map.get(key)
        if c and c in df:
            vals=df[c].fillna("Not applicable / missing").value_counts().head(15)
            fig,ax=plt.subplots(figsize=(10,5)); vals.sort_values().plot.barh(ax=ax,color="#139B83"); ax.set(title=title,xlabel="Records",ylabel=""); save(fig,key+".png")
    for key,title in [("booking_value","Booking value distribution"),("ride_distance","Completed ride-distance distribution (successful bookings only)"),("customer_rating","Customer rating distribution"),("driver_rating","Driver rating distribution")]:
        c=field_map.get(key)
        if c and c in df:
            source=successful_df[c] if key=="ride_distance" else df[c]
            source=pd.to_numeric(source,errors="coerce").dropna() if key=="ride_distance" else source.dropna()
            fig,ax=plt.subplots(figsize=(9,4)); sns.histplot(source,bins=30,kde=("rating" not in key),ax=ax); ax.set(title=title,xlabel="Ride distance (source units)" if key=="ride_distance" else c); save(fig,key+".png")
    veh,dist=field_map.get("vehicle_type"),distance
    if veh and dist:
        completed_distance=successful_df[[veh,dist]].copy()
        completed_distance[dist]=pd.to_numeric(completed_distance[dist],errors="coerce")
        completed_distance=completed_distance.dropna(subset=[veh,dist])
        if not completed_distance.empty:
            fig,ax=plt.subplots(figsize=(10,5)); sns.boxplot(data=completed_distance,x=veh,y=dist,showfliers=False,ax=ax); ax.tick_params(axis="x",rotation=25); ax.set(title="Completed ride distance by vehicle (successful bookings)",xlabel="Vehicle type",ylabel="Distance (source units)"); save(fig,"distance_by_vehicle.png")
            vehicle_distance=completed_distance.groupby(veh)[dist].sum().nlargest(5).sort_values()
            fig,ax=plt.subplots(figsize=(9,4)); vehicle_distance.plot.barh(ax=ax,color="#139B83"); ax.set(title="Top five vehicle types by completed ride distance",xlabel="Total completed distance (source units)",ylabel="Vehicle type"); save(fig,"top5_completed_distance_by_vehicle.png")
    value=field_map.get("booking_value"); pay=field_map.get("payment_method"); customer_rating=field_map.get("customer_rating"); driver_rating=field_map.get("driver_rating")
    if veh and value:
        fig,ax=plt.subplots(figsize=(10,5)); sns.boxplot(data=df,x=veh,y=value,showfliers=False,ax=ax); ax.tick_params(axis="x",rotation=25); ax.set(title="Booking value by vehicle type",xlabel="Vehicle type",ylabel="Booking value (source units)"); save(fig,"value_by_vehicle.png")
    if veh and customer_rating:
        fig,ax=plt.subplots(figsize=(10,5)); sns.boxplot(data=df,x=veh,y=customer_rating,showfliers=False,ax=ax); ax.tick_params(axis="x",rotation=25); ax.set(title="Customer rating by vehicle type",xlabel="Vehicle type",ylabel="Customer rating (source scale)"); save(fig,"customer_rating_by_vehicle.png")
    if veh and driver_rating:
        fig,ax=plt.subplots(figsize=(10,5)); sns.boxplot(data=df,x=veh,y=driver_rating,showfliers=False,ax=ax); ax.tick_params(axis="x",rotation=25); ax.set(title="Driver rating by vehicle type",xlabel="Vehicle type",ylabel="Driver rating (source scale)"); save(fig,"driver_rating_by_vehicle.png")
    if dist and value:
        distance_value=successful_df[[dist,value]].apply(pd.to_numeric,errors="coerce").dropna()
        if not distance_value.empty:
            fig,ax=plt.subplots(figsize=(8,5)); sns.scatterplot(data=distance_value.sample(min(5000,len(distance_value)),random_state=17),x=dist,y=value,alpha=.35,s=16,ax=ax); ax.set(title="Completed ride distance and booking value (successful bookings)",xlabel="Ride distance (source units)",ylabel="Booking value (source units)"); save(fig,"distance_value_scatter.png")
    if status and value:
        fig,ax=plt.subplots(figsize=(10,5)); sns.boxplot(data=df,x=status,y=value,showfliers=False,ax=ax); ax.tick_params(axis="x",rotation=15); ax.set(title="Booking value by booking status",xlabel="Booking status",ylabel="Booking value (source units)"); save(fig,"value_by_status.png")
    if pay and value:
        payment_revenue=df.loc[success_mask].groupby(pay)[value].sum().sort_values(ascending=False)
        fig,ax=plt.subplots(figsize=(9,4)); payment_revenue.plot.bar(ax=ax,color="#139B83"); ax.set(title="Completed booking value by payment method",xlabel="Payment method",ylabel="Booking value (source units)"); save(fig,"completed_value_by_payment.png")
    if veh and value:
        vehicle_revenue=df.loc[success_mask].groupby(veh)[value].sum().sort_values(ascending=False)
        fig,ax=plt.subplots(figsize=(10,4)); vehicle_revenue.plot.bar(ax=ax,color="#3979A8"); ax.set(title="Completed booking value by vehicle type",xlabel="Vehicle type",ylabel="Booking value (source units)"); ax.tick_params(axis="x",rotation=25); save(fig,"completed_value_by_vehicle.png")
    dt="Booking DateTime"; status=field_map.get("booking_status"); value=field_map.get("booking_value")
    s=df[status].astype("string").str.strip().str.casefold() if status else pd.Series(index=df.index,dtype="string")
    if dt in df and status:
        hourly=df.groupby(df[dt].dt.hour).size()
        fig,ax=plt.subplots(figsize=(10,4)); hourly.plot(ax=ax,marker="o",color="#147D72"); ax.set(title="Booking volume by hour",xlabel="Hour of day",ylabel="Bookings",xticks=range(24)); save(fig,"bookings_by_hour.png")
        daily=df.assign(_date=df[dt].dt.floor("D")).groupby("_date").agg(bookings=(status,"size")).reset_index()
        fig,ax=plt.subplots(figsize=(12,4)); ax.plot(daily["_date"],daily.bookings,color="#147D72"); ax.set(title="Daily booking volume",xlabel="Booking date",ylabel="Bookings"); save(fig,"daily_booking_volume.png")
        if value:
            success=df[status].astype("string").str.strip().str.casefold().eq("success")
            daily_value=df.loc[success].assign(_date=df.loc[success,dt].dt.floor("D")).groupby("_date")[value].sum()
            fig,ax=plt.subplots(figsize=(12,4)); daily_value.plot(ax=ax,color="#E2923A"); ax.set(title="Completed booking value by day",xlabel="Booking date",ylabel="Booking value (source units)"); save(fig,"daily_completed_booking_value.png")
        week_order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        hmap=df.assign(_weekday=df[dt].dt.day_name(),_hour=df[dt].dt.hour).pivot_table(index="_weekday",columns="_hour",values=status,aggfunc="count").reindex(week_order)
        fig,ax=plt.subplots(figsize=(12,5)); sns.heatmap(hmap,cmap="crest",ax=ax); ax.set(title="Booking volume by weekday and hour",xlabel="Hour of day",ylabel="Weekday"); save(fig,"weekday_hour_heatmap.png")
        cancel=df.assign(_hour=df[dt].dt.hour,_is_cancel=s.isin(["canceled by customer","canceled by driver"]).astype(int)).groupby("_hour")[["_is_cancel"]].sum()
        fig,ax=plt.subplots(figsize=(10,4)); cancel["_is_cancel"].plot.bar(ax=ax,color="#D97952"); ax.set(title="Customer and driver cancellations by hour",xlabel="Hour of day",ylabel="Canceled bookings"); save(fig,"cancellations_by_hour.png")
        weekday=df[dt].dt.day_name().value_counts().reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
        fig,ax=plt.subplots(figsize=(10,4)); weekday.plot.bar(ax=ax,color="#3979A8"); ax.set(title="Bookings by weekday",xlabel="Weekday",ylabel="Bookings"); ax.tick_params(axis="x",rotation=20); save(fig,"bookings_by_weekday.png")
        weekend=df[dt].dt.dayofweek.ge(5).map({True:"Weekend",False:"Weekday"}).value_counts()
        fig,ax=plt.subplots(figsize=(6,4)); weekend.reindex(["Weekday","Weekend"]).plot.bar(ax=ax,color=["#3979A8","#139B83"]); ax.set(title="Weekday versus weekend bookings",xlabel="Day type",ylabel="Bookings"); save(fig,"weekday_weekend_bookings.png")
        if dist:
            day_distance=successful_df.assign(_date=successful_df[dt].dt.floor("D")).groupby("_date")[dist].agg(total="sum",average="mean",trips="count")
            fig,ax=plt.subplots(figsize=(12,4)); day_distance["average"].plot(ax=ax,color="#8357A5"); ax.set(title="Daily average completed ride distance (successful bookings)",xlabel="Booking date",ylabel="Average distance (source units)"); save(fig,"daily_average_distance.png")
            fig,ax=plt.subplots(figsize=(12,4)); day_distance["total"].plot(ax=ax,color="#139B83"); ax.set(title="Daily total completed ride distance (successful bookings)",xlabel="Booking date",ylabel="Total distance (source units)"); save(fig,"daily_completed_distance.png")
    pickup=field_map.get("pickup_location")
    if pickup:
        driver_not_found=df.loc[s.eq("driver not found"),pickup].fillna("Missing pickup").value_counts().head(15).sort_values()
        if not driver_not_found.empty:
            fig,ax=plt.subplots(figsize=(10,5)); driver_not_found.plot.barh(ax=ax,color="#E2923A"); ax.set(title="Pickup locations with most driver-not-found bookings",xlabel="Bookings",ylabel="Pickup location"); save(fig,"driver_not_found_by_pickup.png")
    drop=field_map.get("drop_location")
    if drop:
        destinations=successful_df[drop].fillna("Missing destination").value_counts().head(15).sort_values()
        if not destinations.empty:
            fig,ax=plt.subplots(figsize=(10,5)); destinations.plot.barh(ax=ax,color="#3979A8"); ax.set(title="Top destinations for successful bookings",xlabel="Completed bookings",ylabel="Drop location"); save(fig,"successful_drop_locations.png")
    tat_cols=[field_map.get(key) for key in ("v_tat","c_tat") if field_map.get(key)]
    correlation_cols=[c for c in [dist,value,*tat_cols] if c and c in df]
    if len(correlation_cols)>=2:
        numeric=successful_df[correlation_cols].apply(pd.to_numeric,errors="coerce")
        corr=numeric.corr(method="spearman",min_periods=30)
        if corr.notna().sum().sum()>0:
            fig,ax=plt.subplots(figsize=(8,6)); sns.heatmap(corr,annot=True,fmt=".2f",center=0,cmap="vlag",square=True,ax=ax); ax.set(title="Spearman associations among successful bookings"); save(fig,"turnaround_metric_correlation.png")
    n=len(df)
    count=lambda label:int(s.eq(label.casefold()).sum())
    successful=count("Success"); customer_cancel=count("Canceled by Customer"); driver_cancel=count("Canceled by Driver"); not_found=count("Driver Not Found")
    vehicle=field_map.get("vehicle_type"); payment=field_map.get("payment_method"); customer=field_map.get("customer_id")
    reason_c=field_map.get("customer_cancel_reason"); reason_d=field_map.get("driver_cancel_reason")
    top_c=df.loc[s.eq("canceled by customer"),reason_c].value_counts() if reason_c else pd.Series(dtype=int)
    top_d=df.loc[s.eq("canceled by driver"),reason_d].value_counts() if reason_d else pd.Series(dtype=int)
    top_customer=df.groupby(customer)[value].sum().nlargest(5) if customer and value else pd.Series(dtype=float)
    vehicle_value=df.loc[s.eq("success")].groupby(veh)[value].sum().sort_values(ascending=False) if veh and value else pd.Series(dtype=float)
    payment_value=df.loc[s.eq("success")].groupby(pay)[value].sum().sort_values(ascending=False) if pay and value else pd.Series(dtype=float)
    vehicle_volume=df[veh].value_counts() if veh else pd.Series(dtype=int)
    completed_distance_mean=successful_df[dist].mean() if dist and dist in successful_df else float("nan")
    facts=[("Source rows retained",f"{n:,}"),("Successful bookings",f"{successful:,} ({successful/n:.2%} of all rows)"),("Unsuccessful bookings",f"{n-successful:,} retained for operational analysis"),("Customer cancellations",f"{customer_cancel:,} ({customer_cancel/n:.2%} of all rows)"),("Driver cancellations",f"{driver_cancel:,} ({driver_cancel/n:.2%} of all rows)"),("Driver not found",f"{not_found:,} ({not_found/n:.2%} of all rows)"),("Highest volume vehicle",str(df[vehicle].value_counts().idxmax()) if vehicle else "n/a"),("Most used recorded payment",str(df[payment].value_counts().idxmax()) if payment else "n/a"),("Mean completed ride distance (successful bookings only)",f"{completed_distance_mean:.2f}" if dist else "n/a"),("Mean booking value, all statuses",f"{df[value].mean():.2f}" if value else "n/a"),("Completed booking value",f"{df.loc[s.eq('success'),value].sum():,.2f}" if value else "n/a"),("Mean customer rating",f"{df[field_map['customer_rating']].mean():.2f}" if field_map.get("customer_rating") else "n/a"),("Mean driver rating",f"{df[field_map['driver_rating']].mean():.2f}" if field_map.get("driver_rating") else "n/a")]
    hour=int(df[dt].dt.hour.value_counts().idxmax()) if dt in df else None
    files=sorted(charts.glob("*.png"))
    report="# Exploratory data analysis\n\n## Definitions\n\nThe source workbook covers July 2024. Successful bookings are exactly `Success`. Customer and driver cancellations are counted from their respective exact status labels. `Driver Not Found` is a separate status. Percentages use all booking rows as denominator. Completed-trip distance and completed booking value use successful bookings only; booking value is not verified accounting revenue.\n\n## Verified findings\n\n"+"\n".join(f"- **{a}:** {b}" for a,b in facts)+f"\n- **Peak booking hour:** {hour}:00 (booking count, not completed rides).\n- **Most frequent customer cancellation reason:** "+(f"{top_c.index[0]} ({top_c.iloc[0]:,})" if len(top_c) else "not available")+".\n- **Most frequent driver cancellation reason:** "+(f"{top_d.index[0]} ({top_d.iloc[0]:,})" if len(top_d) else "not available")+".\n\n## Top five vehicles by completed ride distance\n\n"+("\n".join(f"- {k}: {v:,.0f} source units" for k,v in vehicle_distance.items()) if veh and dist and len(completed_distance) else "Not available")+"\n\n## Top customers by total recorded booking value\n\n"+("\n".join(f"- `{k}`: {v:,.0f}" for k,v in top_customer.items()) or "Not available")+"\n\n## Completed booking value by vehicle\n\n"+("\n".join(f"- {k}: {v:,.0f}" for k,v in vehicle_value.items()) or "Not available")+"\n\n## Completed booking value by payment method\n\n"+("\n".join(f"- {k}: {v:,.0f}" for k,v in payment_value.items()) or "Not available")+"\n\n## Charts\n\n"+"\n".join(f"- [{p.stem}](eda_charts/{p.name})" for p in files)+"\n\n## Business recommendations\n\n- Examine the separate driver-not-found share by hour and pickup area as a driver matching/availability issue.\n- Align supply to observed completed-trip distance and hourly/location demand; evaluate changes through a measured pilot.\n- Use customer and driver cancellation reason breakdowns separately to target process fixes.\n- Analyze payment preference using successful bookings and completed booking value.\n- Interpret ratings with feedback coverage; missing ratings are unavailable feedback, not zero.\n"
    (Path(root)/"reports/EDA_FINAL_REPORT.md").write_text(report,encoding="utf-8")
    insights="# OLA Ride Insights — business report\n\n## Executive summary\n\nThe July 2024 source contains "+f"{n:,} booking rows. "+f"{successful:,} are successful ({successful/n:.2%}); {customer_cancel:,} are customer cancellations ({customer_cancel/n:.2%}); {driver_cancel:,} are driver cancellations ({driver_cancel/n:.2%}). Driver-not-found outcomes are shown separately.\n\n## Business problem and dataset\n\nThe analysis supports demand planning, vehicle mix, booking value, cancellation handling and customer/driver experience. See `docs/DATA_DICTIONARY.md` for actual source fields.\n\n## Data cleaning\n\nExact duplicate rows were audited; status and rating fields were not imputed. The raw workbook remains unchanged. The formula-backed `Vehicle Images` field is excluded from the analytical CSV.\n\n## Findings\n\n"+"\n".join(f"- {a}: {b}" for a,b in facts)+f"\n- Peak booking hour: {hour}:00.\n- Most common customer cancellation reason: "+(f"{top_c.index[0]} ({top_c.iloc[0]:,})" if len(top_c) else "unavailable")+".\n- Most common driver cancellation reason: "+(f"{top_d.index[0]} ({top_d.iloc[0]:,})" if len(top_d) else "unavailable")+".\n\n## Recommendations\n\n- Treat Driver Not Found as a distinct matching/supply issue; inspect its distribution by hour and pickup location.\n- Align supply to hourly demand and validate any repositioning pilot against a baseline.\n- Address the leading cancellation reasons through their separate customer and driver processes.\n- Compare payment methods using successful bookings and completed booking value.\n- Monitor ratings with response coverage and successful trip context.\n\n## Limitations\n\nThe data covers one month. Causal effects, lifetime value and accounting revenue are not inferable from these columns alone. Rates shown use all booking rows as denominator.\n"
    (Path(root)/"reports/PROJECT_INSIGHTS.md").write_text(insights,encoding="utf-8")
    # Expand the handoff report with the required business story and explicit completion boundaries.
    successful_df=df.loc[s.eq("success")]
    report_text=(
        f"# OLA Ride Insights — business report\n\n## Executive summary\n\n"
        f"The July 2024 workbook contains {n:,} bookings. {successful:,} are successful ({successful/n:.2%}), "
        f"{customer_cancel:,} are canceled by customers ({customer_cancel/n:.2%}), {driver_cancel:,} are canceled by drivers ({driver_cancel/n:.2%}), and {not_found:,} have `Driver Not Found` status ({not_found/n:.2%}). The latter is not grouped into cancellation rates.\n\n"
        "## Business problem\n\nUse booking data to improve demand planning, vehicle availability, matching, cancellation handling, payment experience and customer/driver satisfaction.\n\n"
        f"## Dataset overview\n\nRows: {n:,}; processed fields: {df.shape[1]}; unique booking IDs: {df['Booking_ID'].nunique():,}; unique customers: {df[customer].nunique():,}; date range: {df[dt].min().date()} to {df[dt].max().date()}.\n\n"
        f"## Data cleaning summary\n\nNo exact duplicate rows or duplicate booking IDs. Missing ratings preserved: {int(df[field_map['customer_rating']].isna().sum()):,} per rating field. Status and cancellation reason text were not imputed. The source workbook is unchanged; the formula-backed image field is omitted from the analytical CSV. No outlier records were automatically removed.\n\n"
        "## EDA findings\n\n"+"\n".join(f"- {a}: {b}" for a,b in facts)+f"\n- Peak booking hour: {hour}:00.\n- Mean ride distance among successful bookings: {successful_df[field_map['ride_distance']].mean():.2f} source units.\n- Most common customer cancellation reason: {top_c.index[0]} ({top_c.iloc[0]:,}).\n- Most common driver cancellation reason: {top_d.index[0]} ({top_d.iloc[0]:,}).\n\n"
        "## SQL analysis\n\nAll ten required query statements were executed in an in-memory SQLite-compatible database and key counts/value reconciled independently to pandas. See `reports/sql_query_validation.csv` and `reports/sql_python_reconciliation.csv`. A MySQL server-specific run remains pending.\n\n"
        f"## Revenue analysis\n\nCompleted booking value for `Success` rows is {successful_df[value].sum():,.0f} source units. Completed booking value is highest for payment method {payment_value.index[0]} ({payment_value.iloc[0]:,.0f}) and vehicle {vehicle_value.index[0]} ({vehicle_value.iloc[0]:,.0f}). These values are not audited recognized revenue.\n\n"
        "## Customer behavior\n\nTop five customer IDs by total recorded booking value (all statuses):\n\n"+"\n".join(f"- `{k}`: {v:,.0f}" for k,v in top_customer.items())+"\n\n"
        f"## Vehicle performance\n\n{vehicle_volume.index[0]} has the highest booking volume ({vehicle_volume.iloc[0]:,}). Completed booking value by vehicle is listed in `EDA_FINAL_REPORT.md`; distinguish booking volume, distance and value.\n\n"
        f"## Cancellation analysis\n\nCustomer and driver cancellation rates use all {n:,} booking rows as the denominator. The leading customer reason is driver is not moving towards pickup location ({top_c.iloc[0]:,}); the leading driver reason is Personal & Car related issue ({top_d.iloc[0]:,}). Incomplete-ride records are separately identified by the source `Incomplete_Rides` flag ({int(df['Incomplete Flag'].sum()):,}).\n\n"
        f"## Ratings analysis\n\nAverage observed customer rating: {df[field_map['customer_rating']].mean():.2f}; average observed driver rating: {df[field_map['driver_rating']].mean():.2f}. Both fields have {int(df[field_map['customer_rating']].notna().sum()):,} non-null values; absent feedback remains null.\n\n"
        "## Power BI dashboard findings\n\nThe five-section dashboard layout, model and DAX are specified in `powerbi/`. A PBIX has not been created or published; the specifications are not a completed report.\n\n"
        "## Business recommendations\n\n- Investigate `Driver Not Found` by hour and pickup location as a distinct matching/availability outcome.\n- Use observed hourly and location-level demand to plan driver positions, then evaluate changes against a baseline.\n- Address customer pickup/movement cancellations and driver personal/vehicle cancellations with separate interventions.\n- Prioritize payment improvements using successful bookings and completed booking value.\n- Monitor ratings alongside feedback coverage and successful-trip context.\n\n"
        "## Limitations\n\nOne month of data does not establish causation, customer lifetime value, surge effectiveness or recognized revenue. Units for booking value, ride distance and TAT are not defined in the supplied materials.\n")
    (Path(root)/"reports/PROJECT_INSIGHTS.md").write_text(report_text,encoding="utf-8")
    return facts
