# OLA Ride Insights — business report

## Executive summary

The July 2024 workbook contains 103,024 bookings. 63,967 are successful (62.09%), 10,499 are canceled by customers (10.19%), 18,434 are canceled by drivers (17.89%), and 10,124 have `Driver Not Found` status (9.83%). The latter is not grouped into cancellation rates.

## Business problem

Use booking data to improve demand planning, vehicle availability, matching, cancellation handling, payment experience and customer/driver satisfaction.

## Dataset overview

Rows: 103,024; processed fields: 33; unique booking IDs: 103,024; unique customers: 94,544; date range: 2024-07-01 to 2024-07-31.

## Data cleaning summary

No exact duplicate rows or duplicate booking IDs. Missing ratings preserved: 39,057 per rating field. Status and cancellation reason text were not imputed. The source workbook is unchanged; the formula-backed image field is omitted from the analytical CSV. No outlier records were automatically removed.

## EDA findings

- Source rows retained: 103,024
- Successful bookings: 63,967 (62.09% of all rows)
- Unsuccessful bookings: 39,057 retained for operational analysis
- Customer cancellations: 10,499 (10.19% of all rows)
- Driver cancellations: 18,434 (17.89% of all rows)
- Driver not found: 10,124 (9.83% of all rows)
- Highest volume vehicle: Prime Sedan
- Most used recorded payment: Cash
- Mean completed ride distance (successful bookings only): 22.85
- Mean booking value, all statuses: 548.75
- Completed booking value: 35,080,467.00
- Mean customer rating: 4.00
- Mean driver rating: 4.00
- Peak booking hour: 12:00.
- Mean ride distance among successful bookings: 22.85 source units.
- Most common customer cancellation reason: Driver is not moving towards pickup location (3,175).
- Most common driver cancellation reason: Personal & Car related issue (6,542).

## SQL analysis

All ten required query statements were executed in an in-memory SQLite-compatible database and key counts/value reconciled independently to pandas. See `reports/sql_query_validation.csv` and `reports/sql_python_reconciliation.csv`. A MySQL server-specific run remains pending.

## Revenue analysis

Completed booking value for `Success` rows is 35,080,467 source units. Completed booking value is highest for payment method Cash (19,260,316) and vehicle Prime Sedan (5,224,050). These values are not audited recognized revenue.

## Customer behavior

Top five customer IDs by total recorded booking value (all statuses):

- `CID785112`: 8,025
- `CID308763`: 6,281
- `CID734557`: 6,177
- `CID353074`: 6,110
- `CID836942`: 6,019

## Vehicle performance

Prime Sedan has the highest booking volume (14,877). Completed booking value by vehicle is listed in `EDA_FINAL_REPORT.md`; distinguish booking volume, distance and value.

## Cancellation analysis

Customer and driver cancellation rates use all 103,024 booking rows as the denominator. The leading customer reason is driver is not moving towards pickup location (3,175); the leading driver reason is Personal & Car related issue (6,542). Incomplete-ride records are separately identified by the source `Incomplete_Rides` flag (3,926).

## Ratings analysis

Average observed customer rating: 4.00; average observed driver rating: 4.00. Both fields have 63,967 non-null values; absent feedback remains null.

## Power BI dashboard findings

The five-section dashboard layout, model and DAX are specified in `powerbi/`. A PBIX has not been created or published; the specifications are not a completed report.

## Business recommendations

- Investigate `Driver Not Found` by hour and pickup location as a distinct matching/availability outcome.
- Use observed hourly and location-level demand to plan driver positions, then evaluate changes against a baseline.
- Address customer pickup/movement cancellations and driver personal/vehicle cancellations with separate interventions.
- Prioritize payment improvements using successful bookings and completed booking value.
- Monitor ratings alongside feedback coverage and successful-trip context.

## Limitations

One month of data does not establish causation, customer lifetime value, surge effectiveness or recognized revenue. Units for booking value, ride distance and TAT are not defined in the supplied materials.
