Sprint 1 — Data Foundation

This folder groups the Sprint-1 deliverables. Files live in the workspace root; links below point to their locations.

Deliverables and status:

- `nifty100.db`: [nifty100.db](nifty100.db) — created
- `output/load_audit.csv`: [output/load_audit.csv](output/load_audit.csv) — created
- `output/validation_failures.csv`: [output/validation_failures.csv](output/validation_failures.csv) — created
- `src/etl/loader.py`: [src/etl/loader.py](src/etl/loader.py)
- `src/etl/validator.py`: [src/etl/validator.py](src/etl/validator.py)
- `src/etl/normaliser.py`: [src/etl/normaliser.py](src/etl/normaliser.py)
- `db/schema.sql`: [db/schema.sql](db/schema.sql)
- `tests/etl/test_normalizer.py`: [tests/etl/test_normalizer.py](tests/etl/test_normalizer.py)
- `notebooks/exploratory_queries.sql`: [notebooks/exploratory_queries.sql](notebooks/exploratory_queries.sql)
- `Makefile`: [Makefile](Makefile) (includes `load`, `load-full`, `validate`, `test`, `setup`, plus placeholders)

Status summary:
- Full data load executed locally; FK check returned 0 issues.
- 16 DQ rules implemented and executed; see `output/validation_failures.csv` for results.
- Unit tests present (35+ for normaliser). Please run `make test` to execute them locally.

Next actions:
- Provide or confirm the 12 source files in `data/` to re-run if you want corrected loads.
- I can inspect and resolve any CRITICAL failures listed in `output/validation_failures.csv`.
