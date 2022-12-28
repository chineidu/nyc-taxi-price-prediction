.PHONY: setup-venv setup test typecheck lint stylecheck checks

IMAGE_NAME=my_app
TAG=v1
WORK_DIR=opt
SRC_CODE=src
COVERAGE_THRESH=85
PORT=8000


setup-venv: # Create virtual env. You have to run this first!
	python3 -m venv .venv && . .venv/bin/activate
	python3 -m pip install --upgrade pip
	python3 -m pip install -r test_requirements.txt

setup-venv-local: setup-venv # Create virtual env (Run this locally)
	python3 -m venv .venv && . .venv/bin/activate
	python3 setup.py sdist && python3 -m pip install -e .

train:  # This is used to run the flow runs that trains the model.
	. .venv/bin/activate && python3 -V
	python3 src/orchestrate.py


setup:  
	docker build -t ${IMAGE_NAME}:${TAG} -f Dockerfile .

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

run-container:
	docker run -it -p ${PORT}:${PORT} -t ${IMAGE_NAME}:${TAG}

run-checks: 
	# Use the current working directory as the docker's volume. 
	docker run --rm -it --name run-checks \
	-v $(shell pwd):/${WORK_DIR} -t ${IMAGE_NAME}:${TAG} make checks

bash: # --rm: 'remove' the image after building n running it
	docker run --rm -it --name run-checks \
	-v $(shell pwd):/${WORK_DIR} -t ${IMAGE_NAME}:${TAG} bash
