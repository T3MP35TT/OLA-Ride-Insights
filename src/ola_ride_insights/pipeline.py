"""Reproducible profiling, cleaning and reporting for the supplied OLA workbook."""
from __future__ import annotations
import json, re
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "OLA_DataSet.xlsx"
if not RAW.exists():
    RAW = ROOT / "data/OLA_DataSet.xlsx"
OUT = ROOT / "data/processed/ola_cleaned.csv"

ALIASES = {
    "date": ["date", "booking date"], "time": ["time", "booking time"],
    "booking_id": ["booking_id", "booking id"], "booking_status": ["booking_status", "booking status"],
    "customer_id": ["customer_id", "customer id"], "vehicle_type": ["vehicle_type", "vehicle type"],
    "booking_value": ["booking_value", "booking value"], "payment_method": ["payment_method", "payment method"],
    "ride_distance": ["ride_distance", "ride distance"], "driver_rating": ["driver_ratings", "driver_rating", "driver ratings", "driver rating"],
    "customer_rating": ["customer_rating", "customer_rating ", "customer rating"],
    "cancel_customer": ["canceled_rides_by_customer", "cancelled_rides_by_customer", "canceled rides by customer"],
    "cancel_driver": ["canceled_rides_by_driver", "cancelled_rides_by_driver", "canceled rides by driver"],
    "incomplete": ["incomplete_rides", "incomplete rides"], "incomplete_reason": ["incomplete_rides_reason", "incomplete rides reason"],
    "pickup_location": ["pickup_location", "pickup location"],
    "drop_location": ["drop_location", "drop location"],
    "v_tat": ["v_tat", "v tat", "vehicle_tat", "vehicle turnaround time"],
    "c_tat": ["c_tat", "c tat", "customer_tat", "customer turnaround time"],
    "customer_cancel_reason": ["canceled_rides_by_customer_reason", "cancelled_rides_by_customer_reason", "canceled rides by customer reason", "canceled_rides_by_customer", "cancelled_rides_by_customer"],
    "driver_cancel_reason": ["canceled_rides_by_driver_reason", "cancelled_rides_by_driver_reason", "canceled rides by driver reason", "canceled_rides_by_driver", "cancelled_rides_by_driver"],
}
def _norm(x): return re.sub(r"\s+", " ", str(x).strip().lower())
def mapping(columns):
    lookup = {_norm(c): c for c in columns}
    return {key: next((lookup[_norm(a)] for a in aliases if _norm(a) in lookup), None) for key, aliases in ALIASES.items()}

def completed_distance_quartiles(df, status_col, distance_col):
    """Classify successful, observed trip distances without splitting ties.

    Quantile cut points are calculated from successful bookings only. Duplicate
    cut points are collapsed, so tied distances stay in the same band. When all
    observed successful distances are identical, they receive one explicit
    all-tied label. Other rows and missing distances remain unclassified.
    """
    result = pd.Series(pd.NA, index=df.index, dtype="string")
    if not status_col or not distance_col or status_col not in df or distance_col not in df:
        return result

    status = df[status_col].astype("string").str.strip().str.casefold()
    distance = pd.to_numeric(df[distance_col], errors="coerce")
    eligible = status.eq("success") & distance.notna()
    values = distance.loc[eligible]
    if values.empty:
        return result
    if values.nunique(dropna=True) == 1:
        result.loc[eligible] = "Q1-Q4 (all distances tied)"
        return result

    quantile_positions = {}
    for position, value in enumerate(values.quantile([.25, .50, .75]).tolist(), start=1):
        quantile_positions.setdefault(float(value), []).append(position)
    cut_points = sorted(quantile_positions)
    edges = [-np.inf, *cut_points, np.inf]
    codes = pd.cut(values, bins=edges, labels=False, include_lowest=True, right=True)

    labels = []
    first_quartile = 1
    for cut_point in cut_points:
        last_quartile = max(quantile_positions[cut_point])
        if first_quartile == last_quartile:
            suffix = {1: "shortest", 2: "lower-middle", 3: "upper-middle", 4: "longest"}[first_quartile]
            labels.append(f"Q{first_quartile} {suffix}")
        else:
            labels.append(f"Q{first_quartile}-Q{last_quartile} (tied cutoffs)")
        first_quartile = last_quartile + 1
    if first_quartile == 4:
        labels.append("Q4 longest")
    elif first_quartile <= 4:
        labels.append(f"Q{first_quartile}-Q4 (tied cutoffs)")

    code_labels = {code: label for code, label in enumerate(labels)}
    result.loc[eligible] = codes.astype("int64").map(code_labels).astype("string")
    return result

def read_source(path=RAW):
    if not Path(path).exists(): raise FileNotFoundError(f"Source workbook not found: {path}")
    # Sheet 1 is the row-level source table; the remaining sheets are lookups/presentation assets.
    return pd.read_excel(path, sheet_name=0)
def profile(df):
    return {"shape": list(df.shape), "columns": list(map(str, df.columns)), "dtypes": {str(k):str(v) for k,v in df.dtypes.items()},
        "missing": {str(k): {"count":int(v),"percent":round(float(v)/max(len(df),1)*100,3)} for k,v in df.isna().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()), "unique": {str(c):int(df[c].nunique(dropna=True)) for c in df.columns},
        "categorical_values": {str(c): {str(k):int(v) for k,v in df[c].value_counts(dropna=False).head(50).items()} for c in df.select_dtypes(include=["object","category"]).columns},
        "numeric_summary": df.describe(include=[np.number]).replace({np.nan:None}).to_dict(),
        "samples": df.head(5).astype(object).where(pd.notna(df.head(5)),None).to_dict(orient="records"),
        "iqr_outliers": {str(c): int(((df[c] < df[c].quantile(.25)-1.5*(df[c].quantile(.75)-df[c].quantile(.25))) | (df[c] > df[c].quantile(.75)+1.5*(df[c].quantile(.75)-df[c].quantile(.25)))).sum()) for c in df.select_dtypes(include=[np.number]).columns}}
def clean(df):
    original = df.copy(); m = mapping(df.columns)
    result = df.copy()
    # Preserve source values; normalized categories replace only whitespace/case variants.
    for c in result.select_dtypes(include="object").columns:
        result[c] = result[c].map(lambda v: re.sub(r"\s+", " ", v.strip()) if isinstance(v,str) else v)
    for key in ("booking_value","ride_distance","customer_rating","driver_rating","v_tat","c_tat"):
        c=m[key]
        if c: result[c]=pd.to_numeric(result[c],errors="coerce")
    dc,tc=m["date"],m["time"]
    if dc:
        dates=pd.to_datetime(result[dc],errors="coerce",dayfirst=True)
        if tc:
            times=pd.to_timedelta(result[tc].astype(str),errors="coerce")
            result["Booking DateTime"] = dates.dt.normalize() + times
        else: result["Booking DateTime"]=dates
    # Workbook contains a derived icon lookup column; retain it in raw, exclude it as presentation-only.
    noisy=[c for c in result.columns if _norm(c) in {"vehicle image","vehicle images","vehicle icon","image","icon"}]
    result=result.drop(columns=noisy, errors="ignore")
    status=m["booking_status"]
    if status:
        s=result[status].astype("string").str.strip().str.lower()
        result["Successful Booking Flag"] = s.eq("success").fillna(False).astype("int8")
        result["Customer Cancellation Flag"] = s.eq("canceled by customer").fillna(False).astype("int8")
        result["Driver Cancellation Flag"] = s.eq("canceled by driver").fillna(False).astype("int8")
        result["Cancellation Flag"] = s.str.startswith("canceled",na=False).astype("int8")
        result["Incomplete Flag"] = result[m["incomplete"]].astype("string").str.strip().str.casefold().eq("yes").fillna(False).astype("int8") if m.get("incomplete") else s.eq("incomplete").fillna(False).astype("int8")
    if "Booking DateTime" in result:
        dt=result["Booking DateTime"]
        result["Booking Year"]=dt.dt.year; result["Booking Month"]=dt.dt.month
        result["Booking Day"]=dt.dt.day; result["Day of Week"]=dt.dt.day_name()
        result["Booking Hour"]=dt.dt.hour
        result["Weekday/Weekend"]=np.where(dt.dt.dayofweek>=5,"Weekend","Weekday")
        result["Time of Day"]=pd.cut(dt.dt.hour,[-1,5,11,16,20,24],labels=["Night","Morning","Afternoon","Evening","Late evening"])
    exact=int(original.duplicated().sum()); result=result.drop_duplicates()
    if status and m.get("ride_distance"):
        result["Ride Distance Quartile"] = completed_distance_quartiles(result, status, m["ride_distance"])
    audit=pd.DataFrame([{"action":"exact duplicate rows removed","count":exact,"policy":"confirmed exact duplicate only"},
       {"action":"rows with duplicate booking ID","count":int(result[m["booking_id"]].duplicated().sum()) if m["booking_id"] else 0,"policy":"retained for investigation; not assumed duplicates"},
       {"action":"presentation-only icon columns excluded","count":len(noisy),"policy":"source workbook remains unchanged"}])
    return result,m,audit
def write_dictionary(df, field_map):
    meaning={"Date":"Booking calendar date","Time":"Booking time of day","Booking_ID":"Booking identifier","Booking_Status":"Observed outcome category","Customer_ID":"Customer identifier","Vehicle_Type":"Vehicle category","Pickup_Location":"Pickup location/category","Drop_Location":"Drop location/category","V_TAT":"Source turnaround-time measure; exact definition/unit not supplied","C_TAT":"Source turnaround-time measure; exact definition/unit not supplied","Canceled_Rides_by_Customer":"Customer cancellation reason text (not a boolean flag)","Canceled_Rides_by_Driver":"Driver cancellation reason text (not a boolean flag)","Incomplete_Rides":"Yes/No incomplete-ride indicator","Incomplete_Rides_Reason":"Incomplete ride reason","Booking_Value":"Recorded booking amount; not necessarily realized revenue","Payment_Method":"Recorded payment method","Ride_Distance":"Ride distance; source unit unspecified","Driver_Ratings":"Driver rating (observed non-null range shown below)","Customer_Rating":"Customer rating (observed non-null range shown below)","Vehicle Images":"Formula-backed display URL; excluded from analytical output"}
    lines=["# Data dictionary","",f"Source: first worksheet of `{RAW.relative_to(ROOT).as_posix()}`. Currency and distance/TAT units are not defined in the supplied materials. Cancellation columns contain reason text, not yes/no flags.","","| Source column | Type | Missing | Distinct | Meaning |","|---|---|---:|---:|---|"]
    for c in df.columns:
        desc=meaning.get(str(c),"Source field; confirm definition with business owner")
        if str(c) in {field_map.get("driver_rating"),field_map.get("customer_rating")}:
            s=pd.to_numeric(df[c],errors="coerce").dropna(); desc+=f"; observed range {s.min():g}-{s.max():g}" if len(s) else "; no observed values"
        lines.append(f"| `{c}` | {df[c].dtype} | {df[c].isna().sum():,} ({df[c].isna().mean():.2%}) | {df[c].nunique(dropna=True):,} | {desc} |")
    lines += ["","## Derived processed fields","","| Field | Definition |","|---|---|","| `Booking DateTime` | Parsed source date plus time |","| `Successful Booking Flag` | Status exactly `Success` after normalization |","| `Customer Cancellation Flag` | Status exactly `Canceled by Customer` |","| `Driver Cancellation Flag` | Status exactly `Canceled by Driver` |","| `Cancellation Flag` | Status begins with `Canceled`; Driver Not Found remains separate |","| `Incomplete Flag` | Source `Incomplete_Rides` equals Yes |","| `Ride Distance Quartile` | Tie-safe distance bands calculated on successful bookings only; unsuccessful and missing-distance records remain null |","| Date parts, weekday, booking hour, weekend and time-of-day | Derived from booking datetime |"]
    (ROOT/"docs/DATA_DICTIONARY.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
def run():
    df=read_source(); prof=profile(df); clean_df,m,audit=clean(df)
    (ROOT/"data/processed").mkdir(parents=True,exist_ok=True); (ROOT/"reports/eda_charts").mkdir(parents=True,exist_ok=True)
    (ROOT/"reports").mkdir(exist_ok=True); (ROOT/"docs").mkdir(exist_ok=True)
    clean_df.to_csv(OUT,index=False); audit.to_csv(ROOT/"reports/cleaning_audit.csv",index=False)
    (ROOT/"reports/dataset_profile.json").write_text(json.dumps(prof,indent=2,default=str),encoding="utf-8")
    pd.DataFrame([{"column":str(c),"dtype":str(df[c].dtype),"non_null":int(df[c].notna().sum()),"missing":int(df[c].isna().sum()),"unique":int(df[c].nunique(dropna=True))} for c in df.columns]).to_csv(ROOT/"reports/data_quality_summary.csv",index=False)
    import html as html_lib
    rows="".join(f"<tr><td>{html_lib.escape(str(c))}</td><td>{html_lib.escape(str(df[c].dtype))}</td><td>{df[c].isna().sum()}</td><td>{df[c].nunique(dropna=True)}</td><td>{prof['iqr_outliers'].get(str(c),'â€”')}</td></tr>" for c in df.columns)
    html="<!doctype html><meta charset='utf-8'><title>OLA Dataset Profile</title><style>body{font:15px system-ui;max-width:1100px;margin:3em auto;color:#183044}table{border-collapse:collapse;width:100%}td,th{padding:.5em;border:1px solid #ccd;text-align:left}</style><h1>OLA Dataset Profile</h1><p>Source: "+html_lib.escape(RAW.name)+f". Rows: {len(df):,}; columns: {df.shape[1]}; exact duplicate rows: {prof['duplicate_rows']:,}.</p><h2>Fields</h2><table><thead><tr><th>Field</th><th>Type</th><th>Missing</th><th>Distinct</th><th>Potential IQR outliers</th></tr></thead><tbody>"+rows+"</tbody></table><p>Potential IQR outliers are review flags only; no outlier rows are automatically removed.</p>"
    (ROOT/"reports/dataset_profile.html").write_text(html,encoding="utf-8")
    (ROOT/"reports/data_cleaning_report.html").write_text(f"<!doctype html><meta charset='utf-8'><h1>Cleaning report</h1><p>Input rows: {len(df):,}; output rows: {len(clean_df):,}. Source preserved. Exact duplicate rows removed: {int(df.duplicated().sum())}. Missing statuses and ratings are not imputed; ratings are preserved when absent. Text whitespace is trimmed, numeric measures are converted, and date/time features are derived. The Vehicle Images formula field is excluded as presentation-only.</p><p>Potential numeric IQR outlier counts (review only): {html_lib.escape(json.dumps(prof['iqr_outliers']))}. No outlier records were deleted automatically. See data_quality_summary.csv and cleaning_audit.csv.</p>",encoding="utf-8")
    meaning={"Date":"Booking calendar date","Time":"Booking time of day","Booking_ID":"Booking identifier","Booking_Status":"Observed outcome category","Customer_ID":"Customer identifier","Vehicle_Type":"Booked vehicle category","Pickup_Location":"Pickup area/category","Drop_Location":"Destination area/category","V_TAT":"Source TAT measure; unit and exact definition not supplied","C_TAT":"Source TAT measure; unit and exact definition not supplied","Canceled_Rides_by_Customer":"Customer-side cancellation reason text; populated for applicable records, not a boolean flag","Canceled_Rides_by_Driver":"Driver-side cancellation reason text; populated for applicable records, not a boolean flag","Incomplete_Rides":"Yes/No incomplete ride indicator","Incomplete_Rides_Reason":"Recorded reason for an incomplete ride","Booking_Value":"Recorded booking amount; not necessarily realized revenue","Payment_Method":"Recorded payment type","Ride_Distance":"Ride distance; unit not specified in source","Driver_Ratings":"Driver rating (observed 3â€“5 in supplied file)","Customer_Rating":"Customer rating (observed 3â€“5 in supplied file)","Vehicle Images":"Formula-backed display image URL; excluded from processed analytical data"}
    dd="# Data dictionary\n\nUnits for `V_TAT`, `C_TAT`, ride distance and booking value are not defined in the source material; preserve source units until confirmed. Cancellation columns hold reason text rather than yes/no flags.\n\n| Source column | Type | Missing | Distinct | Meaning |\n|---|---|---:|---:|---|\n"+"\n".join(f"| `{c}` | {df[c].dtype} | {df[c].isna().sum()} ({df[c].isna().mean():.2%}) | {df[c].nunique(dropna=True)} | {meaning.get(str(c),'Source field; confirm with business owner')} |" for c in df.columns)+"\n\n## Derived processed fields\n\n| Field | Definition |\n|---|---|\n| `Booking DateTime` | Parsed `Date` plus `Time` |\n| `Successful Booking Flag` | `Booking_Status` exactly `Success` after case/space normalization |\n| `Customer Cancellation Flag` | `Booking_Status` exactly `Canceled by Customer` |\n| `Driver Cancellation Flag` | `Booking_Status` exactly `Canceled by Driver` |\n| `Cancellation Flag` | Booking status begins with `Canceled`; `Driver Not Found` remains separate |\n| `Incomplete Flag` | Source `Incomplete_Rides` equals Yes |\n| `Booking Year`, `Booking Month`, `Booking Day`, `Day of Week`, `Booking Hour`, `Weekday/Weekend`, `Time of Day` | Derived from parsed booking date/time |\n"
    (ROOT/"docs/DATA_DICTIONARY.md").write_text(dd,encoding="utf-8")
    write_dictionary(df,m)
    # Source-value validation flags; suspicious values are reported, never silently removed.
    cr=pd.to_numeric(df[m['customer_rating']],errors='coerce') if m.get('customer_rating') else None
    dr=pd.to_numeric(df[m['driver_rating']],errors='coerce') if m.get('driver_rating') else None
    quality={"negative_booking_value":int((pd.to_numeric(df[m['booking_value']],errors='coerce')<0).sum()) if m.get('booking_value') else None,"negative_ride_distance":int((pd.to_numeric(df[m['ride_distance']],errors='coerce')<0).sum()) if m.get('ride_distance') else None,"customer_ratings_outside_0_5":int((cr.notna() & ~cr.between(0,5)).sum()) if cr is not None else None,"driver_ratings_outside_0_5":int((dr.notna() & ~dr.between(0,5)).sum()) if dr is not None else None,"booking_id_duplicates":int(df[m['booking_id']].duplicated().sum()) if m.get('booking_id') else None,"missing_booking_status":int(df[m['booking_status']].isna().sum()) if m.get('booking_status') else None,"unparseable_booking_datetime":int(clean_df['Booking DateTime'].isna().sum()) if 'Booking DateTime' in clean_df else None}
    quality["missing_customer_ratings"]=int(df[m["customer_rating"]].isna().sum()) if m.get("customer_rating") else None
    quality["missing_driver_ratings"]=int(df[m["driver_rating"]].isna().sum()) if m.get("driver_rating") else None
    quality["missing_incomplete_reason"]=int(df[m["incomplete_reason"]].isna().sum()) if m.get("incomplete_reason") else None
    pd.Series(quality,name="count").to_csv(ROOT/"reports/data_quality_summary.csv",header=True)
    from src.ola_ride_insights.eda import build_eda
    build_eda(clean_df,m,ROOT)
    print(f"Loaded {len(df):,} rows x {df.shape[1]} columns; cleaned {len(clean_df):,}; output {OUT}")
if __name__=="__main__": run()

