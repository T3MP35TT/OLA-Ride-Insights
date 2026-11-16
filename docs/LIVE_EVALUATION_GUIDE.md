# Project walkthrough and evaluation guide

Use this walkthrough to explain the data, demonstrate the application, and distinguish verified results from proposed next steps. Run the pipeline and inspect the current reports before presenting numeric findings.

## Suggested walkthrough

1. **Frame the question.** Explain how booking outcomes, demand timing, vehicle mix, cancellations, payment, and ratings can inform operations.
2. **Establish data provenance.** Show the source workbook, [data dictionary](DATA_DICTIONARY.md), and [provenance notes](DATA_PROVENANCE.md). Explain that missing ratings mean unavailable feedback.
3. **Show reproducibility.** Run `python -m src.ola_ride_insights.pipeline` and point out the separate cleaned output and audit artifacts.
4. **Explain the analysis.** Walk through `notebooks/OLA_Ride_Insights_Analysis.ipynb` and the [business report](../reports/PROJECT_INSIGHTS.md). Distinguish all-status booking value from completed booking value.
5. **Discuss SQL.** Show a required question, its definition, and the Python reconciliation evidence. Clarify that validation used SQLite-compatible execution; a live MySQL run is a separate step.
6. **Demonstrate Streamlit.** Run `streamlit run app.py`; show filters, a focused analytics page, SQL Explorer, and the managed-copy behavior in Data Management.
7. **Cover Power BI.** Show the PBIX and accompanying specifications, then explain which data source and refresh state must be confirmed in the target environment.
8. **Close with evidence-based actions.** Present recommendations as hypotheses to investigate unless an intervention has been measured.

## Common questions

- **Why retain suspicious values?** The pipeline favors auditability; it removes exact duplicate rows only and does not automatically discard potential outliers.
- **Is booking value revenue?** No accounting recognition is established by the source. Report successful-row amounts as completed booking value.
- **How are cancellations counted?** Use booking status and state the denominator. Report customer and driver outcomes separately from `Driver Not Found`.
- **What do missing ratings mean?** The source has no recorded rating for those rows; they are not zero scores.
- **Why has MySQL not been demonstrated?** The recorded validation used SQLite-compatible execution. A configured MySQL server is needed to validate server-specific scripts and loading.
- **What limits the conclusions?** The data covers July 2024 only; currency, distance, and TAT units are unspecified. It cannot establish causality or longer-term trends.
