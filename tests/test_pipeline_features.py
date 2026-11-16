"""Regression tests for source mappings and completed-distance features."""
import pandas as pd

from src.ola_ride_insights.pipeline import clean, completed_distance_quartiles, mapping


def _mini_source():
    return pd.DataFrame(
        {
            "Date": ["2024-07-01", "2024-07-01", "2024-07-01", "2024-07-01"],
            "Time": ["10:00:00", "10:05:00", "10:10:00", "10:15:00"],
            "Booking_ID": ["B1", "B2", "B3", "B4"],
            "Booking_Status": ["Success", "Canceled by Customer", "Canceled by Driver", "Driver Not Found"],
            "Customer_ID": ["C1", "C2", "C3", "C4"],
            "Vehicle_Type": ["Auto", "Bike", "Mini", "Auto"],
            "Pickup_Location": ["North", "South", "East", "West"],
            "Drop_Location": ["Central", "West", "North", "East"],
            "V_TAT": ["18", "invalid", None, 30],
            "C_TAT": [12, "bad", 16, None],
            "Canceled_Rides_by_Customer": [None, "Wrong Address", None, None],
            "Canceled_Rides_by_Driver": [None, None, "Personal issue", None],
            "Incomplete_Rides": ["No", "No", "Yes", "No"],
            "Incomplete_Rides_Reason": [None, None, "Vehicle issue", None],
            "Booking_Value": [100, 50, 60, 70],
            "Payment_Method": ["Cash", "UPI", "Cash", "UPI"],
            "Ride_Distance": [10, 0, 0, 0],
            "Driver_Ratings": [5, None, None, None],
            "Customer_Rating": [4, None, None, None],
        }
    )


def test_source_mapping_and_cleaning_preserve_location_and_tat_fields():
    raw = _mini_source()
    fields = mapping(raw.columns)

    assert fields["pickup_location"] == "Pickup_Location"
    assert fields["drop_location"] == "Drop_Location"
    assert fields["v_tat"] == "V_TAT"
    assert fields["c_tat"] == "C_TAT"

    cleaned, clean_fields, _ = clean(raw)
    assert len(cleaned) == len(raw)
    assert cleaned["Booking_Status"].tolist() == raw["Booking_Status"].tolist()
    assert cleaned["Pickup_Location"].tolist() == raw["Pickup_Location"].tolist()
    assert cleaned["Drop_Location"].tolist() == raw["Drop_Location"].tolist()
    assert pd.api.types.is_numeric_dtype(cleaned["V_TAT"])
    assert pd.api.types.is_numeric_dtype(cleaned["C_TAT"])
    assert cleaned["V_TAT"].tolist()[0] == 18
    assert pd.isna(cleaned["V_TAT"].iloc[1])
    assert pd.isna(cleaned["C_TAT"].iloc[1])
    assert clean_fields["pickup_location"] == "Pickup_Location"
    assert clean_fields["drop_location"] == "Drop_Location"
    assert cleaned["Ride Distance Quartile"].notna().sum() == 1
    assert cleaned["Ride Distance Quartile"].iloc[0] == "Q1-Q4 (all distances tied)"
    assert cleaned["Ride Distance Quartile"].iloc[1:].isna().all()


def test_quartiles_use_successful_trips_only_and_keep_distance_ties_together():
    frame = pd.DataFrame(
        {
            "status": ["Success"] * 8 + ["Canceled by Customer", "Driver Not Found"],
            "distance": [1, 1, 1, 2, 2, 3, 3, 4, 0, 0],
            "booking": [f"B{i}" for i in range(10)],
        }
    )
    bands = completed_distance_quartiles(frame, "status", "distance")

    assert bands.iloc[:8].notna().all()
    assert bands.iloc[8:].isna().all()
    assert bands.iloc[:3].nunique() == 1
    assert bands.iloc[3:5].nunique() == 1
    assert bands.iloc[5:7].nunique() == 1
    assert bands.iloc[:8].nunique() <= 4

    reordered = frame.sample(frac=1, random_state=42)
    reordered_bands = completed_distance_quartiles(reordered, "status", "distance")
    first_by_id = pd.Series(bands.to_numpy(), index=frame["booking"])
    second_by_id = pd.Series(reordered_bands.to_numpy(), index=reordered["booking"])
    pd.testing.assert_series_equal(first_by_id.sort_index(), second_by_id.sort_index(), check_names=False)


def test_quartiles_handle_insufficient_unique_distances_without_splitting_ties():
    frame = pd.DataFrame(
        {"status": ["Success"] * 6, "distance": [5, 5, 5, 7, 7, 7]}
    )
    bands = completed_distance_quartiles(frame, "status", "distance")
    assert bands.notna().all()
    assert bands.iloc[:3].nunique() == 1
    assert bands.iloc[3:].nunique() == 1
    assert bands.nunique() <= 2

    all_tied = pd.DataFrame({"status": ["Success"] * 4, "distance": [9] * 4})
    tied_bands = completed_distance_quartiles(all_tied, "status", "distance")
    assert tied_bands.nunique() == 1
    assert tied_bands.iloc[0] == "Q1-Q4 (all distances tied)"


def test_missing_fields_and_missing_success_distances_remain_unclassified():
    frame = pd.DataFrame(
        {"status": ["Success", "Success", "Canceled by Driver"], "distance": [3, None, 0]}
    )
    bands = completed_distance_quartiles(frame, "status", "distance")
    assert bands.notna().sum() == 1
    assert bands.iloc[1:].isna().all()
    assert completed_distance_quartiles(frame, "unknown", "distance").isna().all()
    assert completed_distance_quartiles(frame, "status", "unknown").isna().all()
