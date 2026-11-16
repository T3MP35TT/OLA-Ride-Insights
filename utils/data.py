"""Dataset loading and actual source-field mapping."""
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/ola_cleaned.csv"
MANAGED = ROOT / "data/managed/ola_managed.csv"
SOURCE_CANDIDATES = (ROOT / "data/OLA_DataSet.xlsx", ROOT / "OLA_DataSet.xlsx")

@st.cache_data(show_spinner="Loading OLA ride data…")
def load_data() -> pd.DataFrame:
    """Load the cleaned CSV, with an Excel fallback for first-run use."""
    path=MANAGED if MANAGED.exists() else PROCESSED
    if path.exists():
        frame=pd.read_csv(path)
        if "Booking DateTime" in frame:
            frame["Booking DateTime"]=pd.to_datetime(frame["Booking DateTime"],errors="coerce")
        return frame
    source = next((p for p in SOURCE_CANDIDATES if p.exists()), None)
    if source is None:
        raise FileNotFoundError("Place OLA_DataSet.xlsx in data/ or the project root, then run the pipeline.")
    return pd.read_excel(source, sheet_name=0)

ALIASES = {
    "date": ("Date", "Booking Date"), "datetime": ("Booking DateTime",),
    "time": ("Time", "Booking Time"), "booking_id": ("Booking_ID", "Booking ID"),
    "status": ("Booking_Status", "Booking Status"), "customer_id": ("Customer_ID", "Customer ID"),
    "vehicle": ("Vehicle_Type", "Vehicle Type"), "pickup": ("Pickup_Location", "Pickup Location"),
    "drop": ("Drop_Location", "Drop Location"), "value": ("Booking_Value", "Booking Value"),
    "payment": ("Payment_Method", "Payment Method"), "distance": ("Ride_Distance", "Ride Distance"),
    "customer_rating": ("Customer_Rating", "Customer Rating"),
    "driver_rating": ("Driver_Ratings", "Driver_Rating", "Driver Rating"),
    "customer_reason": ("Canceled_Rides_by_Customer", "Canceled_Rides_by_Customer_Reason"),
    "driver_reason": ("Canceled_Rides_by_Driver", "Canceled_Rides_by_Driver_Reason"),
    "incomplete": ("Incomplete_Rides", "Incomplete Rides"),
    "incomplete_reason": ("Incomplete_Rides_Reason", "Incomplete Rides Reason"),
}

def resolve_fields(df: pd.DataFrame) -> dict[str, str | None]:
    lookup = {str(c).strip().casefold(): str(c) for c in df.columns}
    return {key: next((lookup[name.strip().casefold()] for name in values if name.strip().casefold() in lookup), None) for key, values in ALIASES.items()}
