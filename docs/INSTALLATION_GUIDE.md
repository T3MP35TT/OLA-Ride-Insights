# Installation

Requires Python 3.10+ and a writable local project copy. Keep `OLA_DataSet.xlsx` in the project root or at `data/OLA_DataSet.xlsx`; the pipeline checks both locations. From the root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.ola_ride_insights.pipeline
streamlit run app.py
```

Pipeline outputs are written under `data/processed`, `docs` and `reports`. Raw `OLA_DataSet.xlsx` is not modified. The app falls back to the workbook if the processed CSV does not exist. MySQL is optional and has not been connected in this environment.
