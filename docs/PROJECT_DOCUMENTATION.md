# Project documentation

This repository contains a source-preserving OLA ride analytics workflow. The Python pipeline profiles the largest workbook sheet, cleans only confirmed exact duplicates and whitespace, adds date/status-derived features when their source fields exist, and emits a processed CSV and audit outputs. The Streamlit UI reads that CSV and provides an executive overview, ride, value, cancellation, rating and data management views. SQL and Power BI artifacts are supplied as reusable build assets.

Reproduce results using the commands in `INSTALLATION_GUIDE.md`. Definitions are source-dependent: inspect profile outputs before publishing results. Retain a distinction between total booking value and completed booking value. No business savings, demand shifts or performance improvements are asserted without executed analysis.
