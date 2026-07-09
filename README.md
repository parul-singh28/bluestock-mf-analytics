# Bluestock Mutual Fund Capstone

This repository contains a submission-ready mutual fund analytics capstone project covering ETL, SQLite storage, exploratory data analysis, performance analytics, and Power BI dashboard preparation.

## Project Scope
- Ingest and clean fund master, NAV, SIP, performance, and investor transaction data
- Load the data into SQLite using a structured schema
- Perform exploratory analysis and performance evaluation
- Prepare a dashboard-ready data model and Power BI report artifact
- Package the final outputs for submission

## Folder Structure
- data/raw: original source CSV files
- data/processed: cleaned and merged datasets
- data/db: SQLite database
- notebooks: analysis notebooks
- scripts: ETL and utility scripts
- sql: schema and queries
- dashboard: Power BI report artifact
- reports: final report and presentation outputs

## Deliverables Included
- ETL pipeline script: scripts/etl_pipeline.py
- SQLite database: data/db/bluestock_mf.db
- EDA notebook: notebooks/03_eda_analysis.ipynb
- Performance notebook: notebooks/04_performance_analytics.ipynb
- Power BI report artifact: dashboard/bluestock_mf.pbip
- Final report draft: reports/Final_Report.md
- Presentation placeholder: reports/Presentation.pptx

## Submission Notes
- The project follows the requested capstone structure.
- The database file is stored in data/db and ignored by Git for submission hygiene.
- The report and presentation files can be finalized further for a polished academic submission.
