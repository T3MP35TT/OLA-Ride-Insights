# Source material review

Reviewed the files present in the project root. The user supplied a larger master prompt as an attachment; it defines a twelve-phase autonomous capstone and calls out optional EDA, GitHub, Streamlit, MySQL/Power BI and presentation training resources that are not present in the workspace.

| File | Type | Extracted contents | Use |
|---|---|---|---|
| `OLA RIDE.docx` | Official requirements | Problem statement; mobility analytics; peak demand, customer behavior, pricing, anomaly use cases; workflow; ten SQL questions; ten dashboard questions; five dashboard groupings (Overall, Vehicle Type, Revenue, Cancellation, Ratings). | Primary definition for analytics and deliverables. |
| `data/OLA_DataSet.xlsx` | Data workbook, 11.8 MB | Workbook has multiple sheets; first worksheet is a large row-level booking dataset and contains a formula-backed vehicle image lookup field. Workbook is preserved unchanged. | Pipeline reads the first worksheet as the row-level source table. It profiles fields before transformations and excludes the image lookup from analysis. |
| `Ola-Slides.pptx` | Power BI reference, 5 slides | Repeated five-tab navigation; vehicle categories Prime Sedan, Prime SUV, Prime Plus, Mini, Auto, Bike, E-Bike; vehicle page KPIs Total Booking Value, Success Booking Value, Average Distance Travelled, Total Distance Travelled. | Dashboard layout and vehicle grouping reference; use the design guide. |
| EDA guide, deep-dive guide, capstone guidelines, GitHub, Streamlit, MySQL/Power BI and Power BI account materials | Not available | Not found in workspace. | No claims made that these were reviewed. Use standard documented practices and mark absence as a limitation. |
| `Pasted text.txt` | User-provided master brief | Twelve phases, output structure and strict non-fabrication requirements. | Governs this implementation. |

## Requirements captured

The official DOCX requires the ten SQL questions and dashboard questions: ride volume over time; status breakdown; top five vehicle types by distance; average customer ratings by vehicle; cancellation reasons; value by payment method; top five customers by total booking value; ride distance distribution per day; driver rating distribution; customer versus driver ratings. The supplied PPTX confirms page groupings and vehicle types. The master prompt adds robust auditability, a fallback Streamlit app, SQL validation, DAX and deployment/evaluation documents.

## Decisions and limits

The source workbook, not the generic brief's conceptual field names, is the source of truth. Category and status filters in SQL are intentionally case-insensitive, but the exact labels must be checked against the profiled output. Completion and recognized revenue are not interchangeable; reports use “completed booking value” until financial recognition rules are confirmed. The workbook is the raw source and remains unchanged. No unavailable source document has been inferred or fabricated.
