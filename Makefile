.PHONY: setup-venv setup test typecheck lint stylecheck checks

CONTAINER_TAG=my_app # enter tag for building container
SRC_CODE=proj
COVERAGE_THRESH=85

setup-venv: # Create virtual env. You have to run this first!
	python3 -m venv .venv && . .venv/bin/activate
	python3 -m pip install --upgrade pip
	python3 -m pip install -r test_requirements.txt

setup-venv-local: setup-venv # Create virtual env (Run this locally)
	python3 -m venv .venv && . .venv/bin/activate
	python3 -m pip install --upgrade build && python3 \
	-m pip install -e .

train:  # This is used to run the flow runs that trains the model.
	. .venv/bin/activate
	python3 src/orchestrate.py


setup:  
	DOCKER_BUILDKIT=1 docker build -t ${CONTAINER_TAG} -f Dockerfile .

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: # Remove prev test logs/artifacts
	rm -f .coverage
	rm -f .coverage.*
	find . -name '.pytest_cache' -exec rm -fr {} +

clean: clean-pyc clean-test
	find . -name '.my_cache' -exec rm -fr {} +
	rm -rf logs/

test: clean # src is the source code
	. .venv/bin/activate && pytest -svv --cov=${SRC_CODE} \
	tests --cov-report=term-missing \
	--cov-fail-under ${COVERAGE_THRESH}

typecheck:  # Run the typecheck test
	. .venv/bin/activate && mypy ${SRC_CODE}

lint:  # Run the linting test
	. .venv/bin/activate && black ${SRC_CODE} && isort ${SRC_CODE}

stylecheck:
	. .venv/bin/activate && flake8 ${SRC_CODE} tests

checks: test lint typecheck stylecheck

run-checks: # opt is the name of the docker's workdir
	# Use the current working directory as the docker's volume. 
	docker run --rm -it --name run-checks -v $(shell pwd):/opt -t ${CONTAINER_TAG} make checks

bash:
	docker run --rm -it --name run-checks -v $(shell pwd):/opt -t ${CONTAINER_TAG} bash