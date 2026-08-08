VENV=.venv
PYTHON=${VENV}/Scripts/python.exe

.PHONY: setup install test load validate clean

setup:
	python -m venv ${VENV}
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install -r requirements.txt

install: setup

test:
	${PYTHON} -m pytest -q

load:
	${PYTHON} -m src.etl.loader --db nifty100.db --data-dir data

load-full:
	${PYTHON} -m src.etl.loader --db nifty100.db --data-dir data

validate:
	${PYTHON} -m src.etl.validator --db nifty100.db

clean:
	rm -rf ${VENV} nifty100.db output/*

ratios:
	@echo "Placeholder: compute financial ratios (not yet implemented)"

report:
	@echo "Placeholder: generate report (not yet implemented)"

dashboard:
	@echo "Placeholder: start dashboard (not yet implemented)"

api:
	@echo "Placeholder: start API (not yet implemented)"
