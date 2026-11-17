<p align="center">
  <img src="images/Ola-Cabs-Logo.png" alt="OLA" width="140"/>
</p>

<h1 align="center">OLA Ride Insights</h1>

<p align="center">
  End-to-end ride-sharing analytics on 103,024 real OLA bookings — cleaning pipeline, SQL, Power BI, a Streamlit app, and a CEO-ready executive report.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/streamlit-1.32%2B-FF4B4B" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/pandas-2.0%2B-150458" alt="pandas"/>
  <img src="https://img.shields.io/badge/SQL-MySQL%208-4479A1" alt="MySQL 8"/>
  <img src="https://img.shields.io/badge/Power%20BI-report-F2C811" alt="Power BI"/>
  <img src="https://img.shields.io/badge/tests-pytest-0A9EDC" alt="pytest"/>
</p>

---

## Why this project

Most portfolio dashboards stop at "here's a chart." This one is built the way a senior analyst would actually hand off work to leadership: a **reproducible pipeline** with logged cleaning decisions, an **exploratory analysis** that tests its own assumptions (and says plainly when they don't hold), a **BI layer** for self-serve exploration, and an **executive report** that states its evidence basis and limitations as clearly as its findings.

The dataset is 103,024 OLA ride bookings from Bengaluru, covering **July 2024** — four mutually exclusive outcomes (Success, Canceled by Driver, Canceled by Customer, Driver Not Found), 7 vehicle types, and full ride, payment, and rating detail for completed trips.

| Metric | Value |
| --- | --- |
| Bookings analyzed | 103,024 |
| Success rate | 62.1% |
| Canceled by Driver | 17.9% |
| Canceled by Customer | 10.2% |
| Driver Not Found | 9.8% |
| Completed booking value | 35.08M (source units; not confirmed revenue) |

**Headline finding:** failure modes don't cluster by vehicle type, day of week, or time of day — chi-square tests on all three return Cramér's V under 0.02. The reliability problem is close to uniform across the operation, which reframes it from "which segment is broken" to "fix dispatch and pickup reliability everywhere." Full reasoning and caveats are in the [executive report](reports/OLA_Ride_Insights_Executive_Report.pdf) and [EDA report](reports/EDA_FINAL_REPORT.md).

## What's inside

| Layer | What it does | Where |
| --- | --- | --- |
| **Pipeline & EDA notebook** | Profiles the raw workbook, documents every cleaning decision, engineers time/outcome/distance features, runs univariate → bivariate → multivariate analysis with significance tests | [`notebooks/OLA_Ride_Insights_Analysis.ipynb`](notebooks/OLA_Ride_Insights_Analysis.ipynb), [`src/ola_ride_insights/`](src/ola_ride_insights) |
| **SQL layer** | Schema, load, indexing, validation, and the 10 required + advanced business questions, runnable on MySQL 8 or SQLite | [`sql/`](sql) |
| **Power BI report** | 5-page executive dashboard (Overview, Ride & Vehicle, Booking Value & Customer, Cancellations, Ratings) on a star schema with 49 DAX measures | [`powerbi/OLA RIDE INSIGHTS.pbix`](powerbi) |
| **Streamlit app** | 8-page interactive app: the BI views, plus a live SQL explorer and a sandboxed CRUD page over a managed copy of the data | [`app.py`](app.py), [`pages/`](pages) |
| **Executive report** | 8-page leadership readout: scope, evidence basis, findings, a single scoped recommendation, and stated limitations | [`reports/OLA_Ride_Insights_Executive_Report.pdf`](reports/OLA_Ride_Insights_Executive_Report.pdf) |

## Quick start

**Requirements:** Python 3.11+, the source workbook `OLA_DataSet.xlsx` in `data/`.

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.ola_ride_insights.pipeline   # builds data/processed/ola_cleaned.csv
streamlit run app.py
```

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.ola_ride_insights.pipeline
streamlit run app.py
```

The pipeline reads the source workbook, writes the cleaned extract to `data/processed/ola_cleaned.csv`, and never modifies the original file. The app runs on the processed extract and falls back to the raw workbook if it's missing. Full setup, including the SQL and Power BI steps, is in the [installation guide](docs/INSTALLATION_GUIDE.md).

## Project structure

```
.
├── app.py, pages/, utils/      Streamlit entry point, 8 pages, shared helpers
├── src/ola_ride_insights/      Profiling, cleaning, feature engineering, EDA pipeline
├── notebooks/                  Consolidated end-to-end analysis notebook
├── sql/                        Schema, load, indexing, validation, business-query scripts
├── powerbi/                    Power BI report (.pbix)
├── reports/                    Executive report, EDA/QA findings, data-quality outputs, charts
├── docs/                       Installation, user, data, SQL, deployment, evaluation docs
└── tests/                      pytest coverage for the pipeline's feature logic
```

## Data notes — read before presenting these numbers

- **Scope:** one month (July 2024) from one city. There is no month-over-month trend in this data, and nothing here should be read as a multi-month pattern.
- **`Driver Not Found` is kept separate from cancellations**, by design, throughout the pipeline, SQL, and BI layer — it's a distinct serviceability outcome, not a cancellation subtype.
- **Booking value is not confirmed recognized revenue**, and ride-distance and turnaround-time units are unspecified in the source. Treat value totals as a proxy, not a financial figure.
- Ratings are only observed for successful bookings (39,057 bookings have none) — missing ratings are preserved as missing, never imputed.

Details and full reasoning: [data provenance](docs/DATA_PROVENANCE.md) · [data dictionary](docs/DATA_DICTIONARY.md) · [project documentation](docs/PROJECT_DOCUMENTATION.md).

## Testing & verification

Pipeline feature logic is covered by `pytest` (`tests/test_pipeline_features.py`). The recorded QA pass covers a successful local pipeline run, a Streamlit smoke test, and reconciliation of all 10 required SQL business questions against SQLite-compatible execution. A live MySQL 8 run, external deployment, and org-specific Power BI validation are **not** part of the recorded evidence — see the [final QA report](reports/FINAL_QA_REPORT.md) before relying on those paths.

```bash
pytest tests/
```

## Documentation

| Doc | Covers |
| --- | --- |
| [Installation guide](docs/INSTALLATION_GUIDE.md) | Full setup, env vars, MySQL config |
| [User guide](docs/USER_GUIDE.md) | Using the Streamlit app |
| [Data dictionary](docs/DATA_DICTIONARY.md) | Field-by-field definitions |
| [Data provenance](docs/DATA_PROVENANCE.md) | Source, lineage, known limitations |
| [SQL documentation](docs/SQL_DOCUMENTATION.md) | Schema and query design |
| [Deployment guide](docs/DEPLOYMENT_GUIDE.md) | Running this outside local dev |
| [Project documentation](docs/PROJECT_DOCUMENTATION.md) | Full project handbook |

## Author

**Kartikey Singh** — Business Analyst. [GitHub repo](https://github.com/T3MP35TT/OLA-Ride-Insights)

## License

No license file is included yet. If you intend this repo to be reused by others, add a `LICENSE` (e.g. MIT or Apache-2.0) before publishing it as open source.
