Sprint 1 — Data Foundation

This scaffold provides the ETL foundation for Sprint 1: loaders, normaliser, validator, schema, tests, and exploratory queries.

Quick start:

- Copy `.env.example` to `.env` and adjust values.
- Run `make setup` to create the virtualenv and install dependencies.
-- Run `make load` to execute the loader (reads `data/` CSV/XLSX files).
-- Run `make validate` to execute DQ rules and write `output/validation_failures.csv`.
-- Run `make test` to run unit tests (35+ tests included for normaliser).

Full data load:

- Place the 12 source files (7 core + 5 supplementary) under the `data/` directory. Filenames may be `companies.xlsx`, `profitandloss.xlsx`, `balancesheet.xlsx`, `cashflow.xlsx`, `stock_prices.csv`, etc. The loader will attempt to discover files by prefix.
- Run `make load-full` to perform the full ingestion, apply schema, write `nifty100.db`, `output/load_audit.csv`, and execute DQ rules producing `output/validation_failures.csv`.

Files created:
- `src/etl/normaliser.py`, `loader.py`, `validator.py`
- `db/schema.sql`
- `tests/etl/test_normalizer.py` (35 tests)
- `notebooks/exploratory_queries.sql`
- Empty `output/validation_failures.csv`, `output/load_audit.csv`

Notes:
- Provide the 12 source files under `data/` before running full load.
- The loader will apply `db/schema.sql` if the database does not exist.
