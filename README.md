# OLA Ride Insights

An end-to-end ride analytics project built around the supplied OLA booking workbook. It includes a reproducible pandas pipeline, Streamlit analytics app, SQL assets, a Power BI report artifact, and supporting analysis and QA outputs.

## Quick start

Place `OLA_DataSet.xlsx` in `data/` (or the project root), then run from PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.ola_ride_insights.pipeline
streamlit run app.py
```

The pipeline writes `data/processed/ola_cleaned.csv`; the source workbook remains unchanged. The app uses the processed data and can fall back to the workbook. Installation details are in [docs](docs/README.md).

## Project map

- `src/ola_ride_insights/`: profiling, cleaning, feature engineering, and EDA pipeline.
- `app.py`, `pages/`, `utils/`: Streamlit entry point, views, and shared helpers.
- `sql/`: MySQL 8 schema, loading, validation, and analytics scripts.
- `powerbi/`: PBIX report and supporting specifications.
- `notebooks/`: consolidated analysis notebook.
- `reports/`: executive report, findings, QA evidence, quality outputs, and charts.
- `docs/`: installation, user, data, SQL, deployment, and evaluation documentation.

## Data interpretation

The supplied dataset covers July 2024. `Driver Not Found` is reported separately from cancellations. Booking value is not confirmed recognized revenue; distance and turnaround-time units are unspecified. Read [data provenance](docs/DATA_PROVENANCE.md) and the [project handbook](docs/PROJECT_DOCUMENTATION.md) before presenting findings.

## Current verification

The recorded QA reports successful local pipeline and Streamlit checks and reconciliation of the ten required SQL questions using SQLite-compatible execution. A live MySQL 8 execution, external deployment, and organization-specific Power BI validation are not recorded. See [final QA](reports/FINAL_QA_REPORT.md).
