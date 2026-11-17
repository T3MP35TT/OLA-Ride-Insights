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
# 🚕 OLA Ride Insights — Ride-Booking Analytics & Decision Support Platform

OLA Ride Insights is an end-to-end ride-sharing analytics project that combines **Python, SQL, Power BI, Streamlit, pandas, and statistical analysis** to turn one month of real OLA booking data into operational, revenue, and customer-experience decisions for leadership.

🔗 **Repository:** https://github.com/T3MP35TT/OLA-Ride-Insights

## 📌 Project Overview

Every ride booking generates structured data across outcome, vehicle, payment, location, and feedback fields.

OLA Ride Insights transforms 103,024 of those bookings into an analytical product designed to answer questions such as:

- 🚦 What share of bookings actually complete successfully?
- 🚗 Is cancellation a driver problem, a customer problem, or a dispatch problem?
- 💰 How much booking value is lost to cancellations, and where does it go?
- 🏍️ Do vehicle types differ in distance, value, or reliability — or just look different?
- 📍 Which pickup locations carry the most unmet demand?
- ⏰ Does time of day or day of week actually move the success rate, or does it only look that way?
- ⭐ How do customer and driver ratings compare, and where do they diverge?
- 👥 How concentrated is revenue among a small set of repeat customers?

The project demonstrates the full analyst workflow: profiling → cleaning → feature engineering → statistical testing → BI delivery → an executive-level writeup that states what the data can and can't support.

## 🎯 Business & Analytical Objectives

- Quantify booking success, cancellation, and dispatch-failure rates
- Separate `Driver Not Found` from cancellations as a distinct serviceability outcome
- Test whether failure rate actually varies by vehicle, time, or weekday (rather than assuming it)
- Measure value per kilometre and completed booking value by vehicle and payment method
- Identify operational hot spots by pickup location
- Compare customer vs. driver ratings and flag low-sample noise
- Convert every finding into an interactive, filterable view for non-technical stakeholders
- Translate the analysis into one scoped, actionable recommendation for a CEO audience

## 📊 Dataset & Key Metrics

| Metric | Value |
|---|---:|
| 🚕 Bookings | 103,024 |
| 📅 Period | 1–31 July 2024 (Bengaluru) |
| ✅ Success rate | 62.1% |
| 🚫 Canceled by Driver | 17.9% |
| 🙅 Canceled by Customer | 10.2% |
| ❌ Driver Not Found | 9.8% |
| 🚗 Vehicle types | 7 |
| 👥 Unique customers | ~94,500 |
| 💰 Completed booking value | ₹35.08M (source units; not confirmed revenue) |
| ⭐ Ratings recorded | Successful bookings only — 39,057 bookings have none |

**Headline finding:** failure modes don't cluster by vehicle type, time of day, or day of week — chi-square tests on all three return Cramér's V under 0.02. The reliability problem is close to uniform across the operation, which reframes the question from *"which segment is broken"* to *"fix dispatch and pickup reliability everywhere."*

## 🧠 Analytical Framework

### 🚦 Booking Outcome Analytics
Success, cancellation, and Driver Not Found rates, each using the full booking base as the denominator so a status filter can't distort a rate.

### 🚗 Ride & Vehicle Analytics
Completed distance, average distance, and value-per-kilometre by vehicle — because raw booking counts across vehicles are nearly identical (14.5–14.9K each) and hide the real differences.

### 💰 Booking Value & Customer Analytics
Completed value by payment method, one-time vs. repeat customers, lost booking value by failure status, and concentration among top customers.

### 🚫 Cancellation Analytics
Customer vs. driver cancellation reasons, rates by vehicle and location, and a decomposition of unsuccessful bookings by status → reason → vehicle → location.

### ⭐ Ratings & Experience Analytics
Customer and driver rating distributions, paired comparisons by vehicle and time of day, with a minimum-sample filter so low-volume locations don't masquerade as ranked outliers.

## 🔎 SQL Analytics — Required & Advanced Queries

### 🟢 Required business questions

| Query | Analytical Focus |
|---|---|
| Q1 | All successful bookings |
| Q2 | Mean ride distance and sample count by vehicle |
| Q3 | Customer cancellation rate |
| Q4 | Top five customers by booking count |
| Q5 | Driver cancellations with specific reason terms |
| Q6 | Observed Prime Sedan driver-rating range |
| Q7 | All UPI bookings |
| Q8 | Average customer rating and feedback count by vehicle |
| Q9 | Completed booking value (flagged as a value proxy, not revenue) |
| Q10 | Incomplete rides, using the source indicator rather than booking status |

### 🟡 Advanced analytical queries

Ten further queries build on the required set: booking-mix summary (success/cancel/DNF in one pass), booking value and average distance by vehicle, completed value by payment method, top-five customers by value, daily and monthly ride volume, hourly booking distribution, customer vs. driver cancellation rate side by side, average ratings by vehicle, and a unified cancellation-reason breakdown across both sides.

Every SQL result is reconciled against the Python/pandas pipeline output — see `reports/sql_python_reconciliation.csv` and `reports/sql_query_validation.csv`.

## 🛡️ Data Quality & Defensive Analytics

- **One month only.** The four month-over-month DAX measures will read blank — there's no second month to compare against. Daily and weekly views are used instead.
- **`Driver Not Found` is never folded into cancellations**, in the pipeline, SQL, or BI layer — it's a distinct serviceability outcome.
- **Ratings are missing, not zero**, for every non-successful booking (39,057 rows) — preserved as missing rather than imputed.
- **Vehicle and weekday differences are statistically weak** (Cramér's V < 0.02 across the board) — the dashboard favors rates over rankings so uniform noise doesn't get read as a pattern.
- **Booking value is a proxy**, not confirmed accounting revenue; ride-distance and turnaround-time units are unspecified in the source.

Full reasoning: [`reports/EDA_FINAL_REPORT.md`](reports/EDA_FINAL_REPORT.md) and [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md).

## 🎨 Dashboard Experience

### 📊 Power BI (5 pages)
Executive Overview, Ride & Vehicle Analysis, Booking Value & Customer Analysis, Cancellation Analysis, Ratings & Customer Experience — a single star schema, synced date/vehicle/status slicers, and 49 DAX measures.

### ⚡ Streamlit (8 pages)
Executive Overview, Ride Analysis, Revenue, Cancellations, Ratings, **SQL Explorer** (a real, sandboxed, read-only query engine over the dataset — not canned output), **Data Management** (CRUD over an isolated copy), and an embedded **Power BI** view so both layers live in one app.

## 🛠️ CRUD & Database Operations

The Data Management page runs full create / read / update / delete operations against a managed copy of the dataset, isolated from the cleaned baseline used everywhere else, so a demo edit never contaminates the analysis.

## 🗄️ Data Architecture

```text
Bookings          — fact table, booking grain
Calendar          — date dimension, related 1:many to Bookings
Measures          — 49 DAX measures (hidden table): Success Rate, Completed
                    Booking Value, Cancellation Rates, Top-N rankings, etc.
```

## 🔄 Data Pipeline

```text
📄 OLA_DataSet.xlsx (raw workbook)
        ↓
🛡️ Profiling & data-quality checks
        ↓
🧹 Cleaning (missing ratings preserved, outliers flagged not removed)
        ↓
🧮 Feature engineering (datetime, outcome flags, distance quartile, time-of-day)
        ↓
📊 Exploratory analysis (univariate → bivariate → multivariate, with significance tests)
        ↓
       ┌──────────────┬──────────────────┐
       ▼              ▼                  ▼
  🗄️ SQLite/MySQL  📈 Power BI (.pbix)  ⚡ Streamlit app
       │
       ▼
  📝 Executive report (PDF)
```

## 💻 Technical Stack

| Technology | Purpose |
|---|---|
| 🐍 Python | Pipeline, feature engineering, EDA |
| 🐼 pandas / NumPy | Data cleaning and transformation |
| 📓 Jupyter | Annotated end-to-end analysis notebook |
| 🔎 SQL (MySQL 8 / SQLite) | Schema, loading, validation, business queries |
| 📊 Power BI + DAX | 5-page executive report, 49 measures |
| ⚡ Streamlit | 8-page interactive app |
| 📝 python-docx / python-pptx | Executive report and slide generation |
| 🌿 Git / GitHub | Version control |

## 📊 Data Analyst Skills Demonstrated

**SQL:** filtering, aggregation, `GROUP BY`, `CASE` logic, rate calculations, multi-query reconciliation against Python output.

**Python:** pandas-based cleaning and validation, feature engineering with regression tests, statistical significance testing (chi-square, Cramér's V, Spearman correlation).

**BI & visualization:** star-schema modeling, DAX measure design, cross-filtered dashboards, KPI cards, decomposition trees.

**Analytics judgment:** distinguishing a real pattern from a calendar or sampling artifact, stating evidence limits instead of overclaiming, scoping a recommendation to what the data actually supports.

## 📁 Project Structure

```text
OLA Ride Insights project/
│
├── app.py, pages/, utils/        Streamlit entry point, 8 pages, shared helpers
│
├── src/ola_ride_insights/        Profiling, cleaning, feature engineering, EDA pipeline
│
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_create_tables.sql
│   ├── 03_load_data.sql
│   ├── 04_indexes.sql
│   ├── 05_data_validation.sql
│   ├── 06_required_business_queries.sql
│   ├── 07_advanced_business_queries.sql
│   ├── 08_powerbi_views.sql
│   └── 09_validation_queries.sql
│
├── powerbi/
│   └── OLA RIDE INSIGHTS.pbix     5-page executive report
│
├── notebooks/
│   └── OLA_Ride_Insights_Analysis.ipynb
│
├── reports/
│   ├── OLA_Ride_Insights_Executive_Report.pdf
│   ├── EDA_FINAL_REPORT.md
│   ├── FINAL_QA_REPORT.md
│   └── PROJECT_INSIGHTS.md
│
├── docs/                          Installation, data, SQL, deployment, evaluation docs
├── tests/                         pytest coverage for pipeline feature logic
└── requirements.txt
```

## 🚀 Getting Started

```bash
git clone https://github.com/T3MP35TT/OLA-Ride-Insights.git
cd OLA-Ride-Insights

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python -m src.ola_ride_insights.pipeline   # builds data/processed/ola_cleaned.csv
streamlit run app.py
```

Place `OLA_DataSet.xlsx` in `data/` first. The pipeline never modifies the source workbook; the app uses the processed extract and falls back to the raw workbook if it's missing.

## 📚 Documentation

| Document | Purpose |
|---|---|
| [`docs/INSTALLATION_GUIDE.md`](docs/INSTALLATION_GUIDE.md) | Full setup |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | Using the Streamlit app |
| [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) | Field-by-field definitions |
| [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md) | Source, lineage, limitations |
| [`docs/SQL_DOCUMENTATION.md`](docs/SQL_DOCUMENTATION.md) | Schema and query design |
| [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) | Running outside local dev |
| [`docs/PROJECT_DOCUMENTATION.md`](docs/PROJECT_DOCUMENTATION.md) | Full project handbook |

## 💡 Key Design Principles

1. **Evidence before narrative.** The reliability finding came from running chi-square tests, not from eyeballing a chart.
2. **Separate distinct failure modes.** `Driver Not Found` never gets folded into "cancellation."
3. **Missing isn't zero.** Ratings on failed bookings are absent, not poor.
4. **One recommendation, clearly scoped.** The executive report names one decision, not a wish list.
5. **State the limits.** One month of data, an unconfirmed value field, and unspecified units are said outright, not buried.

## 📈 Why This Project Matters

The workflow — profile, clean, test assumptions instead of assuming them, build for both technical and non-technical audiences, and scope the recommendation to the evidence — applies directly beyond ride-sharing: to support-ticket analysis, retail transaction data, or any operations dataset where leadership needs a decision, not a dashboard tour.

## ⭐ Project Highlights

```text
🚕 103,024 Bookings  +  📅 1 Month, Bengaluru  +  🚗 7 Vehicle Types
🔎 20 SQL Queries    +  📊 5-Page Power BI Report (49 DAX measures)
⚡ 8-Page Streamlit App (live SQL explorer + CRUD)  +  📝 Executive Report
```

---

## 👤 Author

**Kartikey Singh**

**Business Analyst | Power BI | Python | SQL | Excel**

🔗 LinkedIn: [Kartikey_Singh](https://www.linkedin.com/in/btwitskartiksinghdatanalyst/)

💻 GitHub: [Kartikey_Singh](https://github.com/T3MP35TT)

💼 Portfolio: [Kartikey_Singh](https://sites.google.com/view/kartikeysingh09/home)

## 📄 License

No license file is included yet. Add a `LICENSE` (e.g. MIT or Apache-2.0) before treating this as open source.

⭐ If you find the project useful, consider giving the repository a star.
