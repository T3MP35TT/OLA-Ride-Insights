"""Read, create, update and delete booking records in a separate managed copy."""
from datetime import datetime, time, timedelta
from hashlib import sha256
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.charts import show_chart, show_insight, show_table
from utils.data import MANAGED, PROCESSED, load_data
from utils.sidebar import set_sidebar_context

ROOT=Path(__file__).resolve().parents[2]

@st.cache_data(show_spinner=False)
def _source_fingerprint(file_path):
    digest=sha256()
    with open(file_path,"rb") as source:
        for block in iter(lambda:source.read(1024*1024),b""): digest.update(block)
    return digest.hexdigest()

def _render_provenance(working):
    source=ROOT/"data/OLA_DataSet.xlsx"
    if not source.exists(): source=ROOT/"OLA_DataSet.xlsx"
    processed=PROCESSED
    managed=MANAGED
    audit=ROOT/"reports/data_management_audit.csv"
    st.markdown("#### Where this data comes from")
    st.caption("Trace the current records to the source workbook and see what changed during processing.")
    m=st.columns(4)
    m[0].metric("Current records",f"{len(working):,}")
    m[1].metric("Fields",f"{working.shape[1]}")
    m[2].metric("Source workbook","Available" if source.exists() else "Missing")
    m[3].metric("Record layer","Managed copy" if managed.exists() else "Cleaned baseline")
    with st.container(border=True):
        st.markdown("**Lineage**")
        st.code("data/OLA_DataSet.xlsx (first worksheet)\n        ↓  src/ola_ride_insights/pipeline.py\ndata/processed/ola_cleaned.csv\n        ↓  optional CRUD working copy\ndata/managed/ola_managed.csv\n        ↓  Streamlit analytics and read-only in-memory SQL",language="text")
        st.caption("The original workbook is not overwritten. The app uses the managed copy when it exists; otherwise it reads the cleaned baseline. SQL queries execute against a temporary database and do not write project records.")
    files=[]
    for label,path,role in [("Source workbook",source,"Original workbook; never modified by the app"),("Cleaned baseline",processed,"Reproducible pipeline output"),("Managed working copy",managed,"CRUD changes; separate from the baseline"),("Change audit",audit,"Create/update/delete/restore history")]:
        if path.exists():
            stat=path.stat()
            files.append({"Artifact":label,"Path":str(path.relative_to(ROOT)),"Status":"Available","Size":f"{stat.st_size/1024/1024:.2f} MB","Modified":datetime.fromtimestamp(stat.st_mtime).strftime("%d %b %Y %H:%M")})
        else:
            files.append({"Artifact":label,"Path":str(path.relative_to(ROOT)),"Status":"Not created yet","Size":"—","Modified":"—"})
    show_table(st,pd.DataFrame(files),"Data file inventory",insight="The source workbook and cleaned baseline stay separate from the optional CRUD working copy and its audit history.",hide_index=True)
    if source.exists():
        with st.expander("Source workbook fingerprint"):
            st.code(_source_fingerprint(str(source)))
            st.caption("SHA-256 identifies the workbook bytes in this workspace; it is not a digital signature or proof of external origin.")
    st.markdown("**Processing policy**")
    st.markdown("""
    - Reads the first worksheet; trims text whitespace and parses numeric and date/time fields.
    - Removes exact duplicate rows only; duplicate booking IDs remain for investigation.
    - Preserves missing ratings and other missing values; missing ratings are not zero.
    - Derives booking time parts and outcome flags. `Driver Not Found` stays distinct from cancellations; incomplete rides use the source incomplete flag.
    - Excludes the formula-backed vehicle image field from the analytical CSV. Create, update, delete and restore actions affect only the managed copy and are recorded in the audit file.
    """)
    st.markdown("**Interpretation limits**")
    st.info("The supplied records cover July 2024 only. Booking value units/accounting treatment and distance/turnaround-time units are unspecified. Completed booking value is not audited recognized revenue; missing ratings mean feedback was unavailable.")
    docs=ROOT/"docs/DATA_PROVENANCE.md"
    if docs.exists(): st.download_button("Download full project provenance notes",docs.read_bytes(),"OLA_DATA_PROVENANCE.md","text/markdown")

def _choices(df,column,defaults=()):
    found=list(df[column].dropna().astype(str).unique()) if column else []
    return sorted(set(found)|set(defaults))

def _persist(frame,notice,action,booking_id=""):
    MANAGED.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(MANAGED,index=False)
    load_data.clear()
    st.session_state["management_notice"]=notice
    st.session_state["management_last_action"]=notice
    st.session_state["managed_row_count"]=len(frame)
    audit_path=ROOT/"reports/data_management_audit.csv"
    audit_row=pd.DataFrame([{"timestamp":datetime.now().astimezone().isoformat(timespec="seconds"),"action":action,"booking_id":booking_id,"rows_after":len(frame)}])
    audit_row.to_csv(audit_path,mode="a",header=not audit_path.exists(),index=False)
    st.session_state["sidebar_page_context"]={"page":"Data management","description":"The managed working copy is saved separately; the cleaned baseline remains unchanged.","metrics":[("Managed rows",f"{len(frame):,}"),("Last action",notice)]}
    st.rerun()

def _set_derived(row,fields):
    status_col=fields.get("status")
    status=str(row.get(status_col,"" )).strip().casefold() if status_col else ""
    values={"Successful Booking Flag":int(status=="success"),"Customer Cancellation Flag":int(status=="canceled by customer"),"Driver Cancellation Flag":int(status=="canceled by driver"),"Cancellation Flag":int(status.startswith("canceled"))}
    incomplete_col=fields.get("incomplete")
    values["Incomplete Flag"]=int(str(row.get(incomplete_col,"No")).strip().casefold()=="yes") if incomplete_col else 0
    dt_col=fields.get("datetime"); dt=row.get(dt_col) if dt_col else None
    if dt is not None and not pd.isna(dt):
        dt=pd.Timestamp(dt)
        values.update({"Booking Year":dt.year,"Booking Month":dt.month,"Booking Day":dt.day,"Day of Week":dt.day_name(),"Booking Hour":dt.hour,"Weekday/Weekend":"Weekend" if dt.dayofweek>=5 else "Weekday"})
        hour=dt.hour
        values["Time of Day"]="Night" if hour<=5 else "Morning" if hour<=11 else "Afternoon" if hour<=16 else "Evening" if hour<=20 else "Late evening"
    row.update({key:value for key,value in values.items() if key in row})
    return row

def _new_record(df,f,values):
    row={col:pd.NA for col in df.columns}
    mapping={"booking_id":"booking_id","customer_id":"customer_id","status":"status","vehicle":"vehicle","pickup":"pickup","drop":"drop","value":"value","payment":"payment","distance":"distance","customer_rating":"customer_rating","driver_rating":"driver_rating","incomplete":"incomplete","incomplete_reason":"incomplete_reason","customer_reason":"customer_reason","driver_reason":"driver_reason"}
    for key,field in mapping.items():
        column=f.get(key)
        if column: row[column]=values.get(key,pd.NA)
    date_col,time_col=f.get("date"),f.get("time")
    date_value,time_value=values.get("date"),values.get("time")
    if date_col: row[date_col]=date_value.isoformat() if date_value else pd.NA
    if time_col: row[time_col]=time_value.strftime("%H:%M:%S") if time_value else pd.NA
    if f.get("datetime") and date_value and time_value:
        row[f["datetime"]]=pd.Timestamp(datetime.combine(date_value,time_value))
    return _set_derived(row,f)

def _get_value(row,column,default=None):
    if not column:return default
    value=row.get(column,default)
    try:
        return default if pd.isna(value) else value
    except (TypeError,ValueError):
        return value

def render(df,f):
    id_col=f["booking_id"]
    if not id_col:
        st.error("Booking ID is needed to manage records.")
        return
    working=df.copy()
    k=st.columns(4)
    k[0].metric("Managed records",f"{len(working):,}")
    k[1].metric("Unique booking IDs",f"{working[id_col].nunique():,}")
    k[2].metric("Working copy","Active" if MANAGED.exists() else "Baseline")
    k[3].metric("Baseline protected","Yes")
    show_insight(st,"Create, update and delete actions affect only the isolated managed copy; the cleaned baseline can be restored from the control below.")
    if notice:=st.session_state.pop("management_notice",None): st.success(notice)
    st.caption("Create, inspect, edit and delete records in a managed working copy. The cleaned baseline and source workbook are never overwritten.")

    view=working
    active_filters=[]
    summary_tab,create_tab,update_tab,delete_tab,provenance_tab=st.tabs(["Read records","Create","Update","Delete","Data provenance"])
    with summary_tab:
        filters=st.columns(3)
        status_col,vehicle_col=f.get("status"),f.get("vehicle")
        view=working
        if status_col:
            options=_choices(working,status_col)
            selected=filters[0].multiselect("Booking status",options,default=options,key="manage_status_filter")
            view=view[view[status_col].astype(str).isin(selected)]
            if len(selected)<len(options): active_filters.append(f"{len(selected)} of {len(options)} statuses")
        if vehicle_col:
            options=_choices(working,vehicle_col)
            selected=filters[1].multiselect("Vehicle type",options,default=options,key="manage_vehicle_filter")
            view=view[view[vehicle_col].astype(str).isin(selected)]
            if len(selected)<len(options): active_filters.append(f"{len(selected)} of {len(options)} vehicle types")
        search=filters[2].text_input("Find booking/customer",key="manage_search")
        if search:
            mask=view.astype(str).apply(lambda col:col.str.contains(search,case=False,na=False)).any(axis=1)
            view=view[mask]
            active_filters.append(f"search: {search[:24]}")
        st.caption(f"Showing {len(view):,} matching records (preview capped at 5,000).")
        show_table(st,view.head(5000),"Matching booking records",insight=f"{len(view):,} rows match the current filters and search; the on-screen preview is limited to the first 5,000 rows.",hide_index=True)
        st.download_button("Export filtered records",view.to_csv(index=False).encode("utf-8"),"ola_managed_records.csv","text/csv")
        if status_col:
            counts=view[status_col].fillna("Missing").value_counts().rename_axis("Booking status").reset_index(name="Records")
            show_chart(st,px.bar(counts,x="Booking status",y="Records",color="Booking status",title="Current record mix"))

    if not MANAGED.exists():
        st.info("The managed copy will be created on the first successful change. Until then, this page reads the cleaned baseline.")

    with create_tab:
        st.markdown("#### Add a booking")
        show_insight(st,"Booking ID and Customer ID must be unique or present as required; new records are written to the managed copy, never the cleaned baseline.")
        with st.form("create_booking_form",clear_on_submit=True):
            a,b,c=st.columns(3)
            booking_id=a.text_input("Booking ID *")
            customer_id=b.text_input("Customer ID *")
            status_values=_choices(working,f.get("status"),("Success","Canceled by Customer","Canceled by Driver","Driver Not Found"))
            status=c.selectbox("Booking status",status_values)
            vehicle_values=_choices(working,f.get("vehicle"),("Auto","Bike","Mini","Prime Sedan","Prime SUV","Prime Plus","eBike"))
            vehicle=a.selectbox("Vehicle type",vehicle_values)
            payment_values=_choices(working,f.get("payment"),("Cash","UPI","Credit Card","Debit Card"))
            payment=b.selectbox("Payment method",payment_values)
            booking_date=c.date_input("Booking date",value=datetime.now().date())
            booking_time=a.time_input("Booking time",value=datetime.now().time().replace(second=0,microsecond=0))
            booking_value=b.number_input("Booking value",min_value=0.0,value=0.0,step=50.0)
            ride_distance=c.number_input("Ride distance",min_value=0.0,value=0.0,step=1.0)
            pickup=a.text_input("Pickup location")
            drop=b.text_input("Drop location")
            customer_rating=c.number_input("Customer rating (optional)",min_value=0.0,max_value=5.0,value=0.0,step=.1)
            driver_rating=a.number_input("Driver rating (optional)",min_value=0.0,max_value=5.0,value=0.0,step=.1)
            incomplete=b.selectbox("Incomplete ride?",["No","Yes"])
            incomplete_reason=c.text_input("Incomplete reason")
            customer_reason=a.text_input("Customer cancellation reason")
            driver_reason=b.text_input("Driver cancellation reason")
            submitted=st.form_submit_button("Create booking",type="primary",width="stretch")
        if submitted:
            if not booking_id.strip() or not customer_id.strip(): st.error("Booking ID and Customer ID are required.")
            elif working[id_col].astype(str).eq(booking_id.strip()).any(): st.error("That Booking ID already exists.")
            else:
                values={"booking_id":booking_id.strip(),"customer_id":customer_id.strip(),"status":status,"vehicle":vehicle,"payment":payment,"date":booking_date,"time":booking_time,"value":booking_value,"distance":ride_distance,"pickup":pickup or pd.NA,"drop":drop or pd.NA,"customer_rating":customer_rating if customer_rating>0 else pd.NA,"driver_rating":driver_rating if driver_rating>0 else pd.NA,"incomplete":incomplete,"incomplete_reason":incomplete_reason or pd.NA,"customer_reason":customer_reason or pd.NA,"driver_reason":driver_reason or pd.NA}
                record=_new_record(working,f,values)
                updated=pd.concat([working,pd.DataFrame([record])],ignore_index=True)
                _persist(updated,"Booking created.","CREATE",booking_id.strip())

    with update_tab:
        st.markdown("#### Edit a booking")
        show_insight(st,"Load by Booking ID, review the current row, and save changes to the managed copy. Derived outcome and time fields are recalculated when saved.")
        if "edit_booking_payload" not in st.session_state: st.session_state["edit_booking_payload"]=None
        find_id=st.text_input("Booking ID to edit",key="edit_booking_search")
        if st.button("Load booking",key="load_booking_to_edit"):
            found=working.loc[working[id_col].astype(str).eq(find_id.strip())]
            if found.empty:
                st.session_state["edit_booking_payload"]=None
                st.error("Booking ID was not found.")
            else:
                st.session_state["edit_booking_payload"]=found.iloc[0].to_dict()
                for key in ["edit_status","edit_vehicle","edit_payment","edit_value","edit_distance","edit_customer_rating","edit_driver_rating","edit_pickup","edit_drop","edit_customer_reason","edit_driver_reason","edit_incomplete","edit_incomplete_reason","edit_customer_id","edit_date","edit_time"]:
                    st.session_state.pop(key,None)
                st.rerun()
        payload=st.session_state.get("edit_booking_payload")
        if payload:
            with st.form("update_booking_form"):
                st.caption(f"Editing booking `{payload[id_col]}`")
                a,b,c=st.columns(3)
                status_col=f.get("status"); vehicle_col=f.get("vehicle"); payment_col=f.get("payment")
                status_values=_choices(working,status_col)
                current_status=str(_get_value(payload,status_col,status_values[0]))
                edited_status=a.selectbox("Booking status",status_values,index=status_values.index(current_status) if current_status in status_values else 0,key="edit_status")
                vehicle_values=_choices(working,vehicle_col)
                current_vehicle=str(_get_value(payload,vehicle_col,vehicle_values[0]))
                edited_vehicle=b.selectbox("Vehicle type",vehicle_values,index=vehicle_values.index(current_vehicle) if current_vehicle in vehicle_values else 0,key="edit_vehicle")
                payment_values=_choices(working,payment_col)
                current_payment=str(_get_value(payload,payment_col,payment_values[0]))
                edited_payment=c.selectbox("Payment method",payment_values,index=payment_values.index(current_payment) if current_payment in payment_values else 0,key="edit_payment")
                edited_value=a.number_input("Booking value",min_value=0.0,value=float(_get_value(payload,f.get("value"),0) or 0),step=50.0,key="edit_value")
                edited_distance=b.number_input("Ride distance",min_value=0.0,value=float(_get_value(payload,f.get("distance"),0) or 0),step=1.0,key="edit_distance")
                edited_customer_rating=c.number_input("Customer rating (0 = missing)",min_value=0.0,max_value=5.0,value=float(_get_value(payload,f.get("customer_rating"),0) or 0),step=.1,key="edit_customer_rating")
                edited_driver_rating=a.number_input("Driver rating (0 = missing)",min_value=0.0,max_value=5.0,value=float(_get_value(payload,f.get("driver_rating"),0) or 0),step=.1,key="edit_driver_rating")
                edited_pickup=b.text_input("Pickup location",value=str(_get_value(payload,f.get("pickup"),"")),key="edit_pickup")
                edited_drop=c.text_input("Drop location",value=str(_get_value(payload,f.get("drop"),"")),key="edit_drop")
                edited_incomplete=a.selectbox("Incomplete ride?",["No","Yes"],index=1 if str(_get_value(payload,f.get("incomplete"),"No")).casefold()=="yes" else 0,key="edit_incomplete")
                edited_incomplete_reason=b.text_input("Incomplete reason",value=str(_get_value(payload,f.get("incomplete_reason"),"")),key="edit_incomplete_reason")
                edited_customer_reason=c.text_input("Customer cancellation reason",value=str(_get_value(payload,f.get("customer_reason"),"")),key="edit_customer_reason")
                edited_driver_reason=a.text_input("Driver cancellation reason",value=str(_get_value(payload,f.get("driver_reason"),"")),key="edit_driver_reason")
                edited_customer_id=b.text_input("Customer ID",value=str(_get_value(payload,f.get("customer_id"),"")),key="edit_customer_id")
                date_col,time_col=f.get("date"),f.get("time")
                original_date=pd.to_datetime(_get_value(payload,date_col,datetime.now().date())).date() if date_col else datetime.now().date()
                original_time=pd.to_datetime(str(_get_value(payload,time_col,"00:00:00")),errors="coerce") if time_col else None
                original_time=original_time.time() if original_time is not None and not pd.isna(original_time) else time(0,0)
                edited_date=c.date_input("Booking date",value=original_date,key="edit_date") if date_col else original_date
                edited_time=a.time_input("Booking time",value=original_time,key="edit_time") if time_col else original_time
                save=st.form_submit_button("Save changes",type="primary",width="stretch")
            if save:
                idx=working.index[working[id_col].astype(str).eq(str(payload[id_col]))]
                if len(idx) and edited_customer_id.strip():
                    row=working.loc[idx[0]].to_dict()
                    values={"status":edited_status,"vehicle":edited_vehicle,"payment":edited_payment,"value":edited_value,"distance":edited_distance,"customer_rating":edited_customer_rating if edited_customer_rating>0 else pd.NA,"driver_rating":edited_driver_rating if edited_driver_rating>0 else pd.NA,"pickup":edited_pickup or pd.NA,"drop":edited_drop or pd.NA,"incomplete":edited_incomplete,"incomplete_reason":edited_incomplete_reason or pd.NA,"customer_reason":edited_customer_reason or pd.NA,"driver_reason":edited_driver_reason or pd.NA}
                    for key,value in values.items():
                        if f.get(key): row[f[key]]=value
                    if f.get("customer_id"): row[f["customer_id"]]=edited_customer_id.strip()
                    if date_col: row[date_col]=edited_date.isoformat()
                    if time_col: row[time_col]=edited_time.strftime("%H:%M:%S")
                    if f.get("datetime"): row[f["datetime"]]=pd.Timestamp(datetime.combine(edited_date,edited_time))
                    updated=working.copy(); updated.loc[idx[0]]=pd.Series(_set_derived(row,f))
                    st.session_state["edit_booking_payload"]=None
                    _persist(updated,"Booking updated.","UPDATE",str(payload[id_col]))
                elif not edited_customer_id.strip(): st.error("Customer ID cannot be blank.")

    with delete_tab:
        st.markdown("#### Delete a booking")
        delete_id=st.text_input("Booking ID to delete",key="delete_booking_search")
        if st.button("Find booking",key="find_booking_to_delete"):
            found=working.loc[working[id_col].astype(str).eq(delete_id.strip())]
            st.session_state["delete_booking_found"]=found.iloc[0].to_dict() if not found.empty else None
            if found.empty: st.error("Booking ID was not found.")
        payload=st.session_state.get("delete_booking_found")
        if payload:
            show_table(st,pd.DataFrame([payload]),"Record selected for deletion",insight=f"Booking {payload[id_col]} will be removed from the managed copy only; the cleaned baseline remains unchanged.",hide_index=True)
            confirm=st.checkbox("I confirm deletion from the managed working copy.",key="confirm_delete_booking")
            if st.button("Delete booking",type="primary",disabled=not confirm,key="delete_booking_action"):
                updated=working.loc[working[id_col].astype(str).ne(str(payload[id_col]))].copy()
                st.session_state["delete_booking_found"]=None
                _persist(updated,"Booking deleted from the managed copy. The cleaned baseline is unchanged.","DELETE",str(payload[id_col]))

    with provenance_tab:
        show_insight(st,"This source-to-insight chain identifies which file feeds the current table and which transformations or interpretation limits apply.")
        _render_provenance(working)

    with st.expander("Restore the managed copy from the cleaned baseline"):
        st.write("This discards all changes in the managed working copy and reloads the cleaned baseline.")
        confirm_reset=st.checkbox("I understand this replaces the managed copy.",key="confirm_managed_reset")
        if st.button("Restore clean baseline",disabled=not confirm_reset,key="restore_managed_baseline"):
            base=pd.read_csv(PROCESSED)
            _persist(base,"Managed copy restored from the cleaned baseline.","RESTORE_BASELINE","")

    last_action=st.session_state.get("management_last_action")
    visible=len(view)
    success_count=int(view[f["status"]].astype("string").str.casefold().eq("success").sum()) if f.get("status") else 0
    unmatched_count=int(view[f["status"]].astype("string").str.casefold().eq("driver not found").sum()) if f.get("status") else 0
    scope=f"Current read view: {visible:,} matching records"+(f" ({'; '.join(active_filters)})" if active_filters else " (no filters applied)")
    action=f" Latest change: {last_action}." if last_action else " No create, update or delete action has been made this session."
    set_sidebar_context("Data management",scope+action+" The cleaned baseline remains protected.",[("Successes in view",f"{success_count:,}"),("Driver not found",f"{unmatched_count:,}"),("Latest change",last_action or "None this session")])
