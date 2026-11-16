# Final QA report

## Executed and passed

- Loaded the first worksheet from `data/OLA_DataSet.xlsx`: 103,024 rows × 20 source columns.
- Ran the full cleaning/profile pipeline successfully; wrote `data/processed/ola_cleaned.csv` with 103,024 rows and 32 columns.
- Confirmed 0 exact duplicate rows, 0 duplicate booking IDs, 0 missing booking statuses, 0 negative booking values/distances, 0 ratings outside 0–5, and 0 unparseable booking datetimes.
- Confirmed 39,057 missing customer ratings and 39,057 missing driver ratings are retained; no ratings or booking statuses were imputed.
- Flagged 8,468 Booking_Value observations as potential IQR outliers for review; none were removed automatically.
- Generated dataset profile HTML/JSON, data dictionary, cleaning report, cleaning audit, quality summary and 26 EDA charts.
- Executed all ten required query statements through SQLite-compatible execution and reconciled each query result with independent pandas calculations. Key totals: 63,967 successful; 10,499 customer cancellations; 18,434 driver cancellations; 6,542 personal/car-related driver cancellation reasons; completed booking value 35,080,467; 3,926 source-flagged incomplete rides.
- Ran Streamlit app checks using `AppTest`: all eight navigation views rendered with zero exceptions; the Data Management download control rendered.
- After the OLA theme refactor, rechecked all eight views and exercised all ten SQL Explorer questions; all rendered without exceptions.
- Confirmed the revised sidebar exposes all eight pages as direct buttons (no section dropdown), highlights the active page, and renders page-specific context metrics.
- Confirmed overview, ride, revenue and cancellation/rating views accept interactive filters and retain responsive chart/table layouts.
- Ratings page uses one continuous dashboard layout (no tabs) with three distinct interactive visuals: grouped feedback counts, paired customer/driver averages by vehicle and a paired-rating count heatmap. AppTest confirms all three charts render without exceptions.
- Started Streamlit server and confirmed `/_stcore/health` returned HTTP 200 `ok`.
- Confirmed app page modules are grouped under `pages/` and reusable OLA theme/sidebar/data/query helpers are under `utils/`.
- Generated and reopened `presentation/OLA_RIDE_INSIGHTS_FINAL.pptx`: 18 slides.
- Compiled Python application, pipeline, EDA, query validation and presentation generator modules successfully.

## Current dashboard verification

- Rechecked all eight current navigation pages with Streamlit `AppTest`; all completed without exceptions. Current renders include 7 charts on Executive overview, 7 on Ride analysis, 5 on Cancellations, 3 on Ratings, and 7 on Revenue.
- Reconciled all ten required SQL statements against independent pandas calculations. The local SQL engine now returns all 63,967 successful bookings, all UPI matches and all source-flagged incomplete rides; no ordinary source query is cut off at 10,000 rows.
- Executed the default numbered SQL question from the SQL Explorer Run SQL Query button in `AppTest`; it returned 63,967 rows, a grouped chart and a 500-row preview without exceptions. The full result remains available through CSV export.
- Custom SQL is read-only, restricted to the `bookings` table, limited to 250,000 returned rows and an eight-second execution window. Summaries no longer infer a “top” category from ungrouped raw rows.
- Exercised all ten numbered questions through Streamlit `AppTest`; every question rendered its own question-matched chart/KPI set with no exceptions. Verified the customer-cancellation sidebar shows 10,499 cancellations, a 10.2% share and 103,024 bookings in scope.
- Preset-specific KPI and chart logic is used only when the submitted SQL matches its selected preset; edited or custom SQL gets result-driven summaries and chart controls.
- Replaced three partial notebooks with one consolidated, 34-cell senior analyst notebook. Executed all code cells end to end without errors; saved with cleared outputs to keep the notebook compact.
- Dashboard charts use the shared OLA chart card and include a descriptive key insight. Displayed tables use the shared table card and include a takeaway. Data Management includes source-to-insight provenance in-page.
- Ride analysis includes daily ride-distance and top-five vehicle total-distance views. Executive overview includes a statistical booking-value review threshold; it supports review and is not evidence of fraud.

## Not executed / remaining limits

- No MySQL server/client was installed or configured. Required query statements ran in SQLite-compatible mode, not against MySQL 8; `LOAD DATA LOCAL INFILE` is prepared but requires an authorized MySQL instance and a path adjustment.
- No Power BI Desktop/account was available. Model, DAX and layout specifications are prepared; a PBIX was not created or published.
- No Git executable was available. Repository initialization, commits and remote push were not performed.
- Streamlit Community Cloud deployment and Power BI embedding require user-owned external accounts and were not performed.
- The data covers July 2024 only. Booking value is not confirmed accounting revenue; currency/distance/TAT units are not specified.
- EDA/capstone/GitHub/Streamlit/MySQL/Power BI training references named in the brief were absent from the workspace; only the requirement DOCX and reference slide deck were reviewed.

## Business definition controls

`Success` is the only successful booking label. Customer and driver cancellation rates use all 103,024 booking rows as denominator. `Driver Not Found` is distinct and reported separately. Incomplete rides use the source `Incomplete_Rides = Yes` flag, not a fabricated status. Completed booking value includes only successful bookings and is not represented as audited revenue.
