# Data provenance and interpretation

## Source and lineage

The canonical source is `data/OLA_DataSet.xlsx`. The pipeline reads its first worksheet as the row-level booking table. It does not edit the workbook.

```text
data/OLA_DataSet.xlsx (first worksheet)
  → src/ola_ride_insights/pipeline.py
  → data/processed/ola_cleaned.csv
  → Streamlit analytics, in-memory SQL, reports, and Power BI inputs/specifications
  → optional data/managed/ola_managed.csv for app CRUD changes
```

The app reads the managed copy when it exists; otherwise it reads the cleaned baseline. Managed edits are logged to `reports/data_management_audit.csv`. SQL Explorer creates a temporary in-memory SQLite database for the current app DataFrame; SQL results do not alter project data.

## Pipeline policy

- Reads the first worksheet and maps recognized source headers through normalized aliases.
- Trims repeated text whitespace and parses available numeric fields.
- Combines date and time when both are available.
- Removes exact duplicate rows only; repeated booking IDs are retained for investigation.
- Preserves missing values and observed ratings; it does not impute statuses or ratings.
- Derives date/time parts and status flags when their source fields are available.
- Keeps `Driver Not Found` distinct from cancellations and derives incomplete rides from the source incomplete flag.
- Excludes the formula-backed vehicle image field from the analytical output.

The pipeline also creates profile, data quality, cleaning audit, and EDA artifacts. See [final QA](../reports/FINAL_QA_REPORT.md) for the recorded run and its results.

## Interpretation controls

- `Success` is the successful outcome. Customer and driver cancellations are counted separately; `Driver Not Found` is not a cancellation.
- Cancellation columns contain reasons, not Boolean flags. Use booking status for cancellation counts.
- “Completed booking value” includes successful rows only. The source does not establish currency units, collection, margin, or accounting recognition; do not call it audited revenue.
- Ride distance and turnaround-time units are not supplied.
- Missing ratings mean feedback is unavailable, not a zero score.
- The supplied workbook covers July 2024. It cannot support year-over-year or month-over-month trends, causal claims, or measured intervention effects.

The Data Management page reports live source file availability, file size, modified date, row coverage, and a cached SHA-256 fingerprint.
