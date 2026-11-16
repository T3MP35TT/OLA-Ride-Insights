# Streamlit user guide

Start the app with `streamlit run app.py` after following the [installation guide](INSTALLATION_GUIDE.md). The sidebar links to eight views: Executive overview, Ride analysis, Cancellations, Ratings, Revenue, SQL Explorer, Data Management, and Power BI.

## Analytics views

Use the page filters to select the relevant dates, booking outcomes, vehicle types, or other available categories. Charts and summary metrics describe the selected data. The supplied source covers July 2024, so the dashboard cannot support comparisons with other months unless additional data is added.

The Executive overview summarizes booking outcomes, completed booking value, time patterns, vehicle and payment mix, and location patterns. Ride analysis, Cancellations, Ratings, and Revenue provide more focused views. Keep the [interpretation rules](PROJECT_DOCUMENTATION.md#interpretation-rules) in mind when presenting results.

## Data Management

The data tools support browsing, filtering, searching, exporting, and CRUD operations. Changes are written to `data/managed/ola_managed.csv`, a separate working copy. The cleaned baseline remains the reproducible pipeline output. App changes are recorded in `reports/data_management_audit.csv`; use the restore control to recreate the managed copy from the baseline.

## SQL Explorer

Choose one of the ten reviewed business questions or edit the query. Editing alone does not run it; use **Run SQL Query**. Results include relevant summaries, a chart/table view, and CSV export. The local engine accepts one read-only `SELECT` or `WITH` query against `bookings`; it allows up to 250,000 returned rows and an eight-second execution window. See [SQL documentation](SQL_DOCUMENTATION.md) for column mappings and limits.

## Power BI

The Power BI view embeds the configured report URL. Access depends on the report's publication and permission settings. Confirm that the displayed report reflects the intended source and refresh before using it for decisions; see [deployment](DEPLOYMENT_GUIDE.md).
