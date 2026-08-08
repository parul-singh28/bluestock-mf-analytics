N100 Financial Intelligence Platform

This project contains the Sprint 4 Streamlit dashboard, analytics utilities, valuation exports, and the earlier Sprint 1 data foundation.

Dashboard quick start:

- Install dependencies from `requirements.txt`.
- Run `streamlit run src/dashboard/app.py` from this directory.
- Open `http://localhost:8501`.

Sprint 4 dashboard screens:

- Home: summary KPI tiles, sector donut chart, and top quality-score companies with a global year selector.
- Company Profile: company/ticker search, profile card, six KPI tiles, 10-year revenue/profit bars, ROE/ROCE trend chart, and pros/cons badges.
- Screener: 10 live metric filters, six presets, result count, visible metric table, and CSV export.
- Peer Comparison: peer group selector, benchmark company selector, radar comparison, and peer KPI table.
- Trend Analysis: company selector, up to three overlaid metrics, 10-year chart, and YoY annotations.
- Sector Analysis: sector bubble chart using revenue, ROE, market cap, and sub-sector colour, plus sector median KPI bars.
- Capital Allocation Map: treemap grouped by eight capital allocation patterns with a drilldown company list.
- Annual Reports: company search and annual report year links with unavailable-report handling.

Valuation outputs:

- `src/analytics/valuation.py` builds `output/valuation_summary.xlsx`.
- `output/valuation_summary.xlsx` contains 92 rows with FCF yield, P/E comparison, and Caution/Discount/Fair labels.
- `output/valuation_flags.csv` contains only Caution and Discount companies.

Sprint 5 NLP, cash-flow, and report outputs:

- `src/nlp/parser.py` parses analysis text into `output/analysis_parsed.csv` and writes unmatched rows to `output/parse_failures.csv`.
- `src/nlp/pros_cons_generator.py` generates rule-based pros and cons in `output/pros_cons_generated.csv`.
- `src/analytics/cashflow_kpis.py` builds `output/cashflow_intelligence.xlsx`, `output/distress_alerts.csv`, `output/capital_allocation.csv`, and `output/pattern_changes.csv`.
- `src/reports/tearsheet.py` builds company tearsheets under `reports/tearsheets/`.
- `src/reports/sector_report.py` builds sector PDFs under `reports/sector/`.
- `reports/portfolio/portfolio_summary.pdf` contains the alphabetical portfolio summary.

Sprint 1 data foundation:

- Copy `.env.example` to `.env` and adjust values.
- Run `make setup` to create the virtualenv and install dependencies.
- Run `make load` to execute the loader.
- Run `make validate` to execute DQ rules and write `output/validation_failures.csv`.
- Run `make test` to run unit tests.

Full data load:

- Place the 12 source files under the `data/` directory. Filenames may be `companies.xlsx`, `profitandloss.xlsx`, `balancesheet.xlsx`, `cashflow.xlsx`, `stock_prices.csv`, and similar prefixes.
- Run `make load-full` to perform the full ingestion, apply `db/schema.sql`, write `nifty100.db`, `output/load_audit.csv`, and run validation.

Key files:

- `src/dashboard/app.py`
- `src/dashboard/pages/01_home.py` through `src/dashboard/pages/08_reports.py`
- `src/dashboard/utils/db.py`
- `src/analytics/valuation.py`
- `output/valuation_summary.xlsx`
- `output/valuation_flags.csv`
