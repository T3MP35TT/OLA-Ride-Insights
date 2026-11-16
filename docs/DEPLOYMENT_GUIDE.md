# Deployment guide

Deployment depends on access to the source data, an approved hosting account, and the intended Power BI workspace. Validate those inputs before publishing.

## Local deployment

Follow the [installation guide](INSTALLATION_GUIDE.md). The Streamlit app uses a local CSV or workbook and does not require a database. The Power BI page reads `POWERBI_EMBED_URL` when set; otherwise the app uses its built-in default report URL. Do not add credentials or private tokens to source control.

## Streamlit Community Cloud

1. Ensure the app entry point, `src/`, `pages/`, `utils/`, and `requirements.txt` are in the repository.
2. Decide how the app will receive its input data. Commit the workbook or processed CSV only if redistribution is permitted; otherwise provide data through an approved private source.
3. Connect the repository and deploy `app.py`.
4. Add required non-secret settings through the host's supported configuration. Keep credentials out of Git and local secret files out of commits.
5. Verify the deployed app can read the dataset and that all eight views render.

## Power BI

`powerbi/OLA RIDE INSIGHTS.pbix` and supporting model, measure, and layout files are present. Open the PBIX in Power BI Desktop and confirm its data source, refresh state, measures, and visuals before publishing. Publish only through an authorized workspace. Configure `POWERBI_EMBED_URL` with a URL approved for the target audience; private reports require the appropriate sign-in and workspace permissions.

## SQL database

The SQL assets target MySQL 8. Configure a permitted server and CSV path before running the database and load scripts. The scripts have not been validated against a live MySQL server in the recorded QA. The Streamlit app itself does not depend on MySQL.

## Troubleshooting

- **Workbook read error:** check the file path and reinstall requirements, including `openpyxl`.
- **Missing Python module:** activate the project environment and install `requirements.txt`.
- **Power BI content unavailable:** verify URL, report publication, access permissions, and network policy.
- **MySQL load failure:** review server version, local-file loading settings, schema, and the path in the load script.
