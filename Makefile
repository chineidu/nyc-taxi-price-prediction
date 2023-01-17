# Used to execute commands even if there is a file sharing the target's name.
.PHONY: help setup_venv test typecheck lint stylecheck checks code_quality
.PHONY: run_container

WORK_DIR:=opt
SRC_CODE:="src"
COVERAGE_THRESH:=85
MODEL_DEPLOY:=model_deployment
MODEL_MONITOR:=model_monitoring



help:
	@echo "Commands:"
	@echo "\tsetup_venv:       creates a virtual environment."
	@echo "\tclean:            cleans all unnecessary files."
	@echo "\ttrain:            runs the training pipeline."
	@echo "\ttest:             runs the tests."
	@echo "\tcode_quality:     executes tests, style, lint and type formatting."
	@echo "\tchecks:           creates virtual env, executes tests and code_quality (RECOMMENDEED)."
	@echo ""


setup_venv: # Create virtual env. You have to run this first!
	python3 -m venv .venv && . .venv/bin/activate
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt
	python3 -m pip install -e . && pre-commit install

train:  # This is used to run the flow runs that trains the model.
	. .venv/bin/activate && python3 -V
	python3 src/orchestrate.py

clean_pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean_test: # Remove prev test logs/artifacts
	rm -f .coverage
	rm -f .coverage.*
	find . -name '.pytest_cache' -exec rm -fr {} +

clean: clean_pyc clean_test
	find . -name '.my_cache' -exec rm -fr {} +
	rm -rf logs/

test: clean # src is the source code
	. .venv/bin/activate && pytest -svv --cov=${SRC_CODE} \
	tests --cov-report=term-missing \
	--cov-fail-under ${COVERAGE_THRESH}

typecheck:  # Run the typecheck test
	@echo "\trunning typecheck test ...\n"
	. .venv/bin/activate && mypy src \
	&& mypy ${MODEL_DEPLOY} \
	&& mypy ${MODEL_MONITOR}

lint:  # Run the linting test
	@echo "\trunning linting ...\n"
	. .venv/bin/activate && black ${SRC_CODE} ${MODEL_DEPLOY} ${MODEL_MONITOR} \
	&& isort ${SRC_CODE} ${MODEL_DEPLOY} ${MODEL_MONITOR}

stylecheck:
	@echo "\trunning stylecheck test ...\n"
	. .venv/bin/activate && pylint --recursive=y \
	src model_monitoring model_deployment exp_tracking

code_quality: lint typecheck stylecheck

# Main flow
checks: setup_venv test code_quality
