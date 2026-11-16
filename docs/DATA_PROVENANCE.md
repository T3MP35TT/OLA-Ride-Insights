# OLA Ride Insights data provenance

## Source and lineage

The canonical source is `data/OLA_DataSet.xlsx`; the pipeline reads its first worksheet as the row-level booking table. The source is not edited by the pipeline or by app CRUD operations.

```text
data/OLA_DataSet.xlsx (first worksheet)
  -> src/ola_ride_insights/pipeline.py
  -> data/processed/ola_cleaned.csv
  -> Streamlit analytics, SQLite in-memory SQL, reports, and Power BI specifications
  -> optional data/managed/ola_managed.csv for app CRUD changes
```

The app reads the managed copy when it exists; otherwise it reads the cleaned baseline. Managed-copy changes are kept separate and logged in `reports/data_management_audit.csv`. SQL Explorer materializes the current app DataFrame in a temporary in-memory SQLite database. SQL edits do not change project files, and only a submitted read-only query is executed.

## Pipeline policy

- Reads the first worksheet and maps source fields through normalized aliases.
- Trims repeated text whitespace, parses numeric measures, and combines date and time when available.
- Removes only exact duplicate rows; duplicate booking IDs are retained for investigation.
- Preserves missing values and observed ratings; no ratings or booking statuses are imputed.
- Derives booking datetime parts and outcome flags. `Driver Not Found` remains separate from cancellations; incomplete rides use the source `Incomplete_Rides` flag.
- Excludes the formula-backed vehicle image field from the analytical output. The original workbook remains unchanged.

## Business interpretation controls

- `Success` is the successful booking outcome. Customer and driver cancellations are reported separately. `Driver Not Found` is not counted as a cancellation.
- Completed booking value includes `Success` rows only, but the source does not establish currency units, payment collection, margin, or accounting recognition. It must not be described as audited revenue.
- Ride distance and turnaround-time units are not defined by the source.
- The supplied records cover July 2024 only. They do not support year-over-year, month-over-month, causal, or intervention-effect claims.
- Missing customer and driver ratings represent unavailable feedback and are not zero ratings.

The Streamlit **Data provenance** page shows live file availability, size, modified date, record coverage, and a cached SHA-256 fingerprint for the source workbook.
