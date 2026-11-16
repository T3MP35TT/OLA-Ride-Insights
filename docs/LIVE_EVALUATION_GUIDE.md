# Live evaluation guide

## Suggested walkthrough

1. Explain the business need: use booking, vehicle, payment, cancellation and rating data to plan supply and improve service.
2. Show the source workbook and dictionary. Emphasize that missing ratings mean no feedback and are not zero ratings.
3. Run `python -m src.ola_ride_insights.pipeline`; show exact duplicate auditing and the separate processed file.
4. Walk through `notebooks/OLA_Ride_Insights_Analysis.ipynb`: business framing, source QA, cleaning, feature engineering, UBM analysis (univariate, bivariate and multivariate), and recommendations. Distinguish all-status booking value from completed booking value.
5. Open SQL files and walk through one aggregation, one cancellation definition and the validation queries.
6. Explain the proposed Power BI model, measures and five dashboard sections. State that the PBIX is a manual remaining step.
7. Run `streamlit run app.py`; demonstrate navigation, data explorer, filtering/search and CSV download.
8. End with evidence-based recommendations after the pipeline has generated current results.

## Common questions

- **Why retain suspicious records?** Flagging preserves auditability; only confirmed exact duplicate rows are removed.
- **Is booking value revenue?** Not necessarily. Only completed booking value is reported as a proxy until finance rules are confirmed.
- **How are cancellation rates calculated?** State numerator and total booking denominator explicitly; distinguish customer and driver categories from general cancellations.
- **What if ratings are missing?** Keep nulls because they indicate unavailable feedback.
- **Why does the SQL need field review?** The exact workbook headers are authoritative; generated dictionary/profile should drive identifier corrections.
- **Why is Power BI not attached?** PBIX creation/publication requires Power BI Desktop and organizational account access not available here.

Do not state numeric results until the pipeline has run successfully and the generated reports have been inspected.
