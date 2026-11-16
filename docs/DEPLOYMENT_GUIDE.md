# Deployment guide

## Local

Follow `INSTALLATION_GUIDE.md`. Set `POWERBI_EMBED_URL` only to an organization-approved embed URL; do not put tokens in source control. The Streamlit app runs with the processed CSV and does not require a database.

## Streamlit Community Cloud

Commit the app, `src/`, requirements and processed CSV if dataset redistribution is permitted; otherwise supply data through an approved private data source at runtime. Connect the GitHub repository, select `app.py`, deploy, then configure approved values in the app's Secrets settings. Include no passwords in Git. Add `.streamlit/secrets.toml` locally only for development and keep it ignored.

## Power BI

Build and validate the PBIX in Power BI Desktop using `powerbi/DASHBOARD_DESIGN_GUIDE.md` and `DAX_MEASURES.md`. Publish only through the organization's approved workspace. Configure an authorized embed URL as `POWERBI_EMBED_URL`; private reports require authenticated organizational access. No report URL, tenant or PBIX was supplied, so embedding/publishing is not complete.

## Troubleshooting

- Workbook read error: install `openpyxl`, confirm the workbook is in the repository root.
- Missing module: activate the project virtual environment and install `requirements.txt`.
- Blank Power BI page: verify approved embed permissions and the configured URL.
- MySQL unavailable: use the app's CSV fallback; the current app does not require MySQL credentials.
