# OLA Ride Insights — project handbook

This handbook is the documentation home for the OLA Ride Insights project. It describes how the workbook becomes analysis-ready data, how to run the Streamlit application, where to find SQL and Power BI assets, and which interpretation limits apply to every result.

## Project at a glance

The project analyzes the supplied OLA booking workbook using a reproducible pandas pipeline, a Streamlit analytics application, SQL scripts, a Power BI report artifact, and supporting analysis and QA reports. The raw workbook is retained as the source of record. Cleaning outputs and app-managed edits are stored separately.

### Current artifact status

| Area | Available | Scope or status |
|---|---|---|
| Python pipeline | `src/ola_ride_insights/pipeline.py` | Profiles and cleans the first worksheet; writes processed data and audit/report artifacts. |
| Streamlit app | `app.py`, `pages/`, `utils/` | Eight navigable views; uses the processed data and supports workbook fallback. |
| SQL | `sql/` | MySQL 8 setup, loading, validation, required and advanced query scripts. Required queries were also reconciled in SQLite-compatible execution; no MySQL server run is recorded. |
| Power BI | `powerbi/OLA RIDE INSIGHTS.pbix` and `powerbi/` | A PBIX file and supporting specifications are present. Validate the report against the intended dataset and account before relying on publication or refresh behavior. |
| Analysis | `notebooks/`, `reports/` | Consolidated notebook, EDA charts, business findings, profiling and QA evidence. |

## Start here

Choose the guide that matches your task:

| I want to… | Read |
|---|---|
| Install dependencies, prepare data, and run locally | [Installation guide](INSTALLATION_GUIDE.md) |
| Use the dashboard and its data tools | [User guide](USER_GUIDE.md) |
| Understand source fields, cleaning, and lineage | [Data dictionary](DATA_DICTIONARY.md) and [Data provenance](DATA_PROVENANCE.md) |
| Run or adapt the SQL assets | [SQL documentation](SQL_DOCUMENTATION.md) |
| Deploy the app or connect Power BI | [Deployment guide](DEPLOYMENT_GUIDE.md) |
| Present and explain the project | [Live evaluation guide](LIVE_EVALUATION_GUIDE.md) |
| Review source materials and captured requirements | [Source material review](SOURCE_MATERIAL_ANALYSIS.md) |
| Prepare a GitHub repository | [GitHub guide](GITHUB_GUIDE.md) |

Analysis evidence and caveats live in [`reports/`](../reports/): start with the [executive report](../reports/OLA_Ride_Insights_Executive_Report.docx), [final QA](../reports/FINAL_QA_REPORT.md), [project insights](../reports/PROJECT_INSIGHTS.md), and [final EDA report](../reports/EDA_FINAL_REPORT.md). The [project plan](PROJECT_PLAN.md) is a historical execution log, not a live task tracker.

## Data flow

```text
data/OLA_DataSet.xlsx (first worksheet; source preserved)
        ↓
src/ola_ride_insights/pipeline.py
        ↓
data/processed/ola_cleaned.csv + reports and generated profile/dictionary
        ↓
Streamlit analytics / read-only in-memory SQL / analysis artifacts
        ↘
          optional data/managed/ola_managed.csv (app CRUD working copy)
```

The app uses the managed working copy when present, otherwise the cleaned baseline. The managed copy is separate from the pipeline output; changes are logged in `reports/data_management_audit.csv`. See [data provenance](DATA_PROVENANCE.md) for the transformation policy and interpretation controls.

## Reproducibility

From the repository root, install requirements and run the pipeline before launching the app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.ola_ride_insights.pipeline
streamlit run app.py
```

The pipeline writes the cleaned CSV under `data/processed/`, a generated data dictionary under `docs/`, and profiling/quality outputs under `reports/`. It does not modify the source workbook. Detailed setup and source placement are in the [installation guide](INSTALLATION_GUIDE.md).

## Interpretation rules

- `Success` is the successful booking outcome. Customer cancellation, driver cancellation, `Driver Not Found`, and source-flagged incomplete rides are distinct categories.
- Cancellation reason columns contain explanatory text, not booking-level Boolean flags. Use booking status for cancellation counts.
- Booking value is a source amount, not confirmed recognized revenue. Completed booking value refers only to successful rows and is not an audited financial measure.
- Distance and turnaround-time units are unspecified by the source. Do not attach assumed units.
- Missing ratings mean feedback is unavailable; they are not zero ratings.
- The supplied data covers July 2024. It cannot establish longer-term trends, causation, intervention impact, or customer lifetime value.
- Review the current reports after rerunning the pipeline; generated counts and findings can change if the input workbook changes.

## Documentation conventions

Paths are repository-root relative unless stated otherwise. File names and commands use the spelling and capitalization present in the project. Status statements describe artifacts in this checkout and should be updated when execution, deployment, or source data changes.
