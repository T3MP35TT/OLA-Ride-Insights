# Installation and local run

## Requirements

- Python 3.10 or later
- A writable project checkout
- The source workbook, `OLA_DataSet.xlsx`, at `data/OLA_DataSet.xlsx` or the repository root

Dependencies are listed in [`requirements.txt`](../requirements.txt). A MySQL server is not required to run the pipeline or Streamlit app.

## Create an environment

Run these commands from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use the environment interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Build the processed data

```powershell
python -m src.ola_ride_insights.pipeline
```

The pipeline reads the first worksheet and writes `data/processed/ola_cleaned.csv`, a generated data dictionary, and profile, quality, and audit artifacts. It leaves the workbook unchanged. See [data provenance](DATA_PROVENANCE.md) for its cleaning rules.

## Launch the app

```powershell
streamlit run app.py
```

By default, Streamlit prints a local URL in the terminal. The app reads the processed CSV; if it is absent, the app can fall back to the workbook. Data Management may create a separate `data/managed/ola_managed.csv` working copy.

## Common issues

| Symptom | Resolution |
|---|---|
| Workbook not found | Place `OLA_DataSet.xlsx` in `data/` or the repository root. |
| Excel engine error | Reinstall requirements; `openpyxl` is used to read the workbook. |
| Import error | Confirm the virtual environment is active and install `requirements.txt`. |
| Power BI view is empty | Check the configured report URL and its access policy; see [deployment](DEPLOYMENT_GUIDE.md). |

For SQL setup, MySQL is optional and separately documented in [SQL documentation](SQL_DOCUMENTATION.md).
