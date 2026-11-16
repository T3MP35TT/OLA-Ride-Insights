"""Read-only SQL execution against the complete in-memory bookings dataset."""
from __future__ import annotations

import re
import sqlite3
import time

import pandas as pd

COLUMN_MAP = {
    "Date": "date", "Time": "time", "Booking_ID": "booking_id",
    "Booking_Status": "booking_status", "Customer_ID": "customer_id",
    "Vehicle_Type": "vehicle_type", "Pickup_Location": "pickup_location",
    "Drop_Location": "drop_location", "V_TAT": "v_tat", "C_TAT": "c_tat",
    "Canceled_Rides_by_Customer": "canceled_rides_by_customer",
    "Canceled_Rides_by_Driver": "canceled_rides_by_driver",
    "Incomplete_Rides": "incomplete_rides",
    "Incomplete_Rides_Reason": "incomplete_rides_reason",
    "Booking_Value": "booking_value", "Payment_Method": "payment_method",
    "Ride_Distance": "ride_distance", "Driver_Ratings": "driver_ratings",
    "Customer_Rating": "customer_rating",
}

# All ordinary source-table selections fit. The ceiling protects custom queries
# such as self-joins while keeping the complete 103k-row source available.
MAX_ROWS = 250_000
DEFAULT_TIMEOUT_SECONDS = 8


def _validate_first_statement(sql: str) -> None:
    without_leading_comments = re.sub(
        r"\A\s*(?:(?:--[^\n]*(?:\n|\Z))|(?:/\*.*?\*/))*\s*",
        "", sql, count=1, flags=re.DOTALL,
    )
    match = re.match(r"([A-Za-z]+)", without_leading_comments)
    if not match or match.group(1).casefold() not in {"select", "with"}:
        raise ValueError("Only one read-only SELECT or WITH query is allowed.")


def execute_readonly_query(
    query: str,
    df: pd.DataFrame,
    *,
    max_rows: int = MAX_ROWS,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[pd.DataFrame, bool]:
    """Run a single read-only query on `bookings` and return rows plus truncation.

    The full input frame is loaded before execution. SQLite's authorizer blocks
    writes, schema changes, pragmas, attachments and reads from other tables.
    Ordinary source queries can return every matching source row; only unusually
    large custom-query outputs are capped, with truncation reported to the UI.
    """
    sql = str(query or "").strip()
    if not sql:
        raise ValueError("Enter a SQL query before running it.")
    _validate_first_statement(sql)
    if max_rows < 1 or timeout_seconds <= 0:
        raise ValueError("The query safety limits must be positive.")

    rename = {source: target for source, target in COLUMN_MAP.items() if source in df.columns}
    data = df.rename(columns=rename)
    if data.columns.duplicated().any():
        duplicates = data.columns[data.columns.duplicated()].tolist()
        raise ValueError(f"Source fields map to duplicate SQL column names: {duplicates}")

    connection = sqlite3.connect(":memory:")
    try:
        data.to_sql("bookings", connection, index=False, if_exists="replace")
        deadline = time.monotonic() + timeout_seconds
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
        if hasattr(sqlite3, "SQLITE_RECURSIVE"):
            allowed.add(sqlite3.SQLITE_RECURSIVE)

        def authorize(action, arg1, arg2, database, source):
            if action not in allowed:
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_READ and arg1 not in {"bookings", ""}:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        connection.set_authorizer(authorize)
        connection.set_progress_handler(lambda: int(time.monotonic() >= deadline), 10_000)
        cursor = connection.execute(sql)
        rows = cursor.fetchmany(max_rows + 1)
        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]
        columns = [item[0] for item in cursor.description or []]
        return pd.DataFrame.from_records(rows, columns=columns), truncated
    except sqlite3.OperationalError as exc:
        if "interrupted" in str(exc).casefold():
            raise ValueError(f"Query exceeded the {timeout_seconds:g}-second execution limit.") from exc
        raise ValueError(f"SQL query failed: {exc}") from exc
    except sqlite3.Error as exc:
        raise ValueError(f"SQL query failed: {exc}") from exc
    finally:
        connection.close()
