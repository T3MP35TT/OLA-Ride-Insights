# SQL assets and query behavior

## Script inventory

Scripts are numbered in the recommended setup order. Review file comments and adjust local paths and server settings before loading data.

| File | Purpose |
|---|---|
| `sql/01_create_database.sql` | Create the project database. |
| `sql/02_create_tables.sql` | Define the typed booking table. |
| `sql/03_load_data.sql` | Load a CSV; requires a valid local path and compatible MySQL settings. |
| `sql/04_indexes.sql` | Add indexes for common filters and grouping. |
| `sql/05_data_validation.sql` | Inspect row counts, categories, keys, and suspicious values. |
| `sql/06_required_business_queries.sql` | Answer the ten required business questions. |
| `sql/07_advanced_business_queries.sql` | Additional KPI, customer, time, payment, vehicle, and rating analyses. |
| `sql/08_powerbi_views.sql` | Create grouped views for reporting. |
| `sql/09_validation_queries.sql` | Produce aggregates for reconciliation. |

See [data dictionary](DATA_DICTIONARY.md) for source field definitions and [data provenance](DATA_PROVENANCE.md) for outcome definitions.

## Important field semantics

- Cancellation reason columns contain reason text. Count cancellations using `Booking_Status`; group the reason columns only for reason analysis.
- Incomplete rides are identified by `Incomplete_Rides = 'Yes'`, not by a fabricated booking status.
- `Driver Not Found` is separate from customer and driver cancellations.
- The amount field is not confirmed recognized revenue. Use “completed booking value” for successful rows.

## Streamlit SQL Explorer

The app loads the current app DataFrame into a temporary in-memory SQLite database as `bookings`. Column names are mapped to lowercase snake case (for example, `Booking_Status` becomes `booking_status`). One read-only `SELECT` or `WITH` statement is accepted; writes and access to other tables are blocked. Ordinary source queries can return all matching rows. Custom query results are capped at 250,000 rows and execution is limited to eight seconds. The app reports truncation when the cap is reached; the displayed table is a preview and CSV export contains the returned result.

This SQLite-backed feature is distinct from the MySQL scripts. The ten required query statements were executed in SQLite-compatible mode and reconciled against pandas calculations. A live MySQL 8 run and server-specific CSV load have not been recorded. See [final QA](../reports/FINAL_QA_REPORT.md) for verification details.
