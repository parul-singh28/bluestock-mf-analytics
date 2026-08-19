VENV=../.venv4
PYTHON=${VENV}/Scripts/python.exe

.PHONY: setup install test load validate clean

setup:
	python -m venv ${VENV}
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install -r requirements.txt

install: setup

test:
	${PYTHON} tools/run_tests_with_report.py

load:
	${PYTHON} -m src.etl.loader --db nifty100.db --data-dir data

load-full:
	${PYTHON} -m src.etl.loader --db nifty100.db --data-dir data

validate:
	${PYTHON} -m src.etl.validator --db nifty100.db

clean:
	rm -rf ${VENV} nifty100.db output/*

ratios:
	${PYTHON} tools/generate_deliverables.py

report:
	${PYTHON} tools/generate_deliverables.py

dashboard:
	${PYTHON} -m streamlit run src/dashboard/app.py --server.port 8501

api:
	${PYTHON} -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
