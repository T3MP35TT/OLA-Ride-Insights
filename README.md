# OLA Ride Insights

End-to-end ride analytics using the supplied workbook, with a reproducible pandas pipeline, SQL assets, Power BI build specifications and a Streamlit data management and analytics app.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.ola_ride_insights.pipeline
streamlit run app.py
```

Source workbook: `data/OLA_DataSet.xlsx` (kept unchanged). Processed output: `data/processed/ola_cleaned.csv`. The app reads the processed CSV or falls back to the workbook in `data/` or the project root.

## Project map

- `src/ola_ride_insights/pipeline.py`: workbook profiling, cleaning and derived fields.
- `app.py`: Streamlit entry point and dynamic page router.
- `pages/`: all dashboard page modules in one folder (`overview.py`, `rides.py`, `cancellations.py`, `ratings.py`, `revenue.py`, `sql_explorer.py`, `data_management.py`, `power_bi.py`).
- `utils/`: OLA theme, dynamic sidebar, source field mapping, chart styling and predefined SQL query logic.
- `utils/sql_engine.py`: in-memory, read-only SQL execution against the `bookings` table.
- `utils/charts.py`: shared OLA chart/table cards with chart-specific key insights.
- `notebooks/OLA_Ride_Insights_Analysis.ipynb`: consolidated business framing, source QA, cleaning, feature engineering, univariate/bivariate/multivariate EDA and recommendations.
- `pages/data_management.py`: CRUD operations against an isolated managed copy; the cleaned baseline remains unchanged.
- `images/Ola-Cabs-Logo.png`: brand image used in the app header and sidebar.
- `sql/`: MySQL 8 schema, required and additional analytics queries.
- `powerbi/`: model, DAX and dashboard specifications. No PBIX was supplied or generated.
- `reports/`, `docs/`, `notebooks/`, `presentation/`: analysis and handoff material.

See [installation](docs/INSTALLATION_GUIDE.md), [deployment](docs/DEPLOYMENT_GUIDE.md), [source review](docs/SOURCE_MATERIAL_ANALYSIS.md), and [QA status](reports/FINAL_QA_REPORT.md).

Dashboard charts and tables include descriptive key insights. Data Management contains the source provenance details alongside its managed-copy controls. SQL Explorer returns complete source-sized results, previews up to 500 rows, and exports the full result as CSV.

## Verified source findings

The source has 103,024 rows from July 2024. Success is 63,967 rows (62.09%); customer cancellations are 10,499 (10.19%); driver cancellations are 18,434 (17.89%); Driver Not Found is 10,124 (9.83%) and is reported separately. Completed booking value for successful rows totals 35,080,467 source units. See `reports/PROJECT_INSIGHTS.md` for the definitions and limitations.

GitHub setup instructions are in `docs/GITHUB_GUIDE.md`; the directory has not been initialized as a Git repository because Git was not available in the environment.
