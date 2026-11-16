"""Run the ten required query semantics through SQLite and reconcile with pandas."""
from pathlib import Path
import sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/"data/processed/ola_cleaned.csv"
SQL=ROOT/"sql/06_required_business_queries.sql"
def main():
    frame=pd.read_csv(CSV)
    source_names={"Date":"date","Time":"time","Booking_ID":"booking_id","Booking_Status":"booking_status","Customer_ID":"customer_id","Vehicle_Type":"vehicle_type","V_TAT":"v_tat","C_TAT":"c_tat","Canceled_Rides_by_Customer":"canceled_rides_by_customer","Canceled_Rides_by_Driver":"canceled_rides_by_driver","Incomplete_Rides":"incomplete_rides","Incomplete_Rides_Reason":"incomplete_rides_reason","Booking_Value":"booking_value","Payment_Method":"payment_method","Ride_Distance":"ride_distance","Driver_Ratings":"driver_ratings","Customer_Rating":"customer_rating"}
    data=frame.rename(columns=source_names)
    con=sqlite3.connect(":memory:")
    data.to_sql("bookings",con,index=False)
    sql=SQL.read_text(encoding="utf-8")
    statements=[]
    for line in sql.splitlines():
        line=line.strip()
        if line.startswith("--") or line.upper().startswith("USE ") or not line: continue
        statements.append(line)
    text="\n".join(statements)
    queries=[q.strip() for q in text.split(";") if q.strip()]
    if len(queries)!=10: raise AssertionError(f"Expected 10 required queries, found {len(queries)}")
    results=[]; outputs=[]
    for idx,q in enumerate(queries,1):
        out=pd.read_sql_query(q,con)
        outputs.append(out)
        results.append({"query":idx,"rows_returned":len(out),"columns":"; ".join(out.columns)})
    success=data.booking_status.str.strip().str.casefold().eq("success")
    cust_cancel=data.booking_status.str.strip().str.casefold().eq("canceled by customer")
    driver_cancel=data.booking_status.str.strip().str.casefold().eq("canceled by driver")
    # Reconcile each query's result to an independent pandas calculation.
    assert len(outputs[0])==int(success.sum())
    pandas_dist=data.groupby("vehicle_type",dropna=False).ride_distance.mean().sort_index()
    sql_dist=outputs[1].set_index("vehicle_type").average_ride_distance.sort_index()
    assert pandas_dist.index.tolist()==sql_dist.index.tolist() and (pandas_dist.values.round(10)==sql_dist.values.round(10)).all()
    assert int(outputs[2].iloc[0,0])==int(cust_cancel.sum())
    expected_top=data.groupby("customer_id").size().rename("bookings").reset_index().sort_values(["bookings","customer_id"],ascending=[False,True]).head(5).set_index("customer_id").bookings
    actual_top=outputs[3].set_index("customer_id").bookings
    assert expected_top.index.tolist()==actual_top.index.tolist() and expected_top.tolist()==actual_top.tolist()
    expected_reason=int((driver_cancel & data.canceled_rides_by_driver.str.contains("personal",case=False,na=False) & data.canceled_rides_by_driver.str.contains("car",case=False,na=False)).sum())
    assert int(outputs[4].iloc[0,0])==expected_reason
    prime=data.vehicle_type.str.strip().str.casefold().eq("prime sedan")
    assert outputs[5].iloc[0,0]==data.loc[prime,"driver_ratings"].max() and outputs[5].iloc[0,1]==data.loc[prime,"driver_ratings"].min()
    assert set(outputs[6].booking_id)==set(data.loc[data.payment_method.str.strip().str.casefold().eq("upi"),"booking_id"])
    pandas_rating=data.groupby("vehicle_type").customer_rating.mean().sort_index(); sql_rating=outputs[7].set_index("vehicle_type").average_customer_rating.sort_index()
    assert pandas_rating.index.tolist()==sql_rating.index.tolist() and ((pandas_rating-sql_rating).abs()<1e-10).all()
    assert float(outputs[8].iloc[0,0])==float(data.loc[success,"booking_value"].sum())
    expected_incomplete=data.loc[data.incomplete_rides.str.strip().str.casefold().eq("yes"),"booking_id"]
    assert set(outputs[9].booking_id)==set(expected_incomplete)
    # Exact status and value reconciliation against loaded records.
    checks={
      "successful_bookings":int((data.booking_status.str.strip().str.casefold()=="success").sum()),
      "customer_cancellations":int((data.booking_status.str.strip().str.casefold()=="canceled by customer").sum()),
      "driver_cancellations":int((data.booking_status.str.strip().str.casefold()=="canceled by driver").sum()),
      "driver_personal_car_reason":int(((data.booking_status.str.strip().str.casefold()=="canceled by driver") & data.canceled_rides_by_driver.str.contains("personal",case=False,na=False)).sum()),
      "completed_booking_value":float(data.loc[data.booking_status.str.strip().str.casefold()=="success","booking_value"].sum()),
      "incomplete_flag_yes":int((data.incomplete_rides.str.strip().str.casefold()=="yes").sum()),
    }
    assert checks["successful_bookings"]==63967
    assert checks["customer_cancellations"]==10499
    assert checks["driver_cancellations"]==18434
    assert checks["driver_personal_car_reason"]==6542
    assert checks["completed_booking_value"]==35080467
    assert checks["incomplete_flag_yes"]==3926
    pd.DataFrame(results).to_csv(ROOT/"reports/sql_query_validation.csv",index=False)
    pd.Series(checks,name="value").to_csv(ROOT/"reports/sql_python_reconciliation.csv",header=True)
    print(f"Executed all {len(results)} required queries; reconciliation passed: {checks}")
if __name__=="__main__": main()
