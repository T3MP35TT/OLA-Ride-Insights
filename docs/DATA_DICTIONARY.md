# Data dictionary

This profile describes the supplied workbook and its current pipeline output. The pipeline regenerates this file; review its contents after changing the source workbook.

Source: first worksheet of `data/OLA_DataSet.xlsx`. Currency and distance/TAT units are not defined in the supplied materials. Cancellation columns contain reason text, not yes/no flags.

| Source column | Type | Missing | Distinct | Meaning |
|---|---|---:|---:|---|
| `Date` | datetime64[ns] | 0 (0.00%) | 40,214 | Booking calendar date |
| `Time` | object | 0 (0.00%) | 1,440 | Booking time of day |
| `Booking_ID` | object | 0 (0.00%) | 103,024 | Booking identifier |
| `Booking_Status` | object | 0 (0.00%) | 4 | Observed outcome category |
| `Customer_ID` | object | 0 (0.00%) | 94,544 | Customer identifier |
| `Vehicle_Type` | object | 0 (0.00%) | 7 | Vehicle category |
| `Pickup_Location` | object | 0 (0.00%) | 50 | Pickup location/category |
| `Drop_Location` | object | 0 (0.00%) | 50 | Drop location/category |
| `V_TAT` | float64 | 39,057 (37.91%) | 40 | Source turnaround-time measure; exact definition/unit not supplied |
| `C_TAT` | float64 | 39,057 (37.91%) | 25 | Source turnaround-time measure; exact definition/unit not supplied |
| `Canceled_Rides_by_Customer` | object | 92,525 (89.81%) | 5 | Customer cancellation reason text (not a boolean flag) |
| `Canceled_Rides_by_Driver` | object | 84,590 (82.11%) | 4 | Driver cancellation reason text (not a boolean flag) |
| `Incomplete_Rides` | object | 39,057 (37.91%) | 2 | Yes/No incomplete-ride indicator |
| `Incomplete_Rides_Reason` | object | 99,098 (96.19%) | 3 | Incomplete ride reason |
| `Booking_Value` | int64 | 0 (0.00%) | 2,883 | Recorded booking amount; not necessarily realized revenue |
| `Payment_Method` | object | 39,057 (37.91%) | 4 | Recorded payment method |
| `Ride_Distance` | int64 | 0 (0.00%) | 50 | Ride distance; source unit unspecified |
| `Driver_Ratings` | float64 | 39,057 (37.91%) | 21 | Driver rating (observed non-null range shown below); observed range 3-5 |
| `Customer_Rating` | float64 | 39,057 (37.91%) | 21 | Customer rating (observed non-null range shown below); observed range 3-5 |
| `Vehicle Images` | object | 0 (0.00%) | 7 | Formula-backed display URL; excluded from analytical output |

## Derived processed fields

| Field | Definition |
|---|---|
| `Booking DateTime` | Parsed source date plus time |
| `Successful Booking Flag` | Status exactly `Success` after normalization |
| `Customer Cancellation Flag` | Status exactly `Canceled by Customer` |
| `Driver Cancellation Flag` | Status exactly `Canceled by Driver` |
| `Cancellation Flag` | Status begins with `Canceled`; Driver Not Found remains separate |
| `Incomplete Flag` | Source `Incomplete_Rides` equals Yes |
| `Ride Distance Quartile` | Tie-safe distance bands calculated on successful bookings only; unsuccessful and missing-distance records remain null |
| Date parts, weekday, booking hour, weekend and time-of-day | Derived from booking datetime |
