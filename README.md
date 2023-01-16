# nyc-taxi-price-prediction

New York Taxi Trip Duration Prediction ML Project

## Install The Package

* To install, run:

```bash
pip install -e .
```

* To install with the developer tools (this installs ALL the packages), run:

```bash
pip install -e ".[dev]"
```

* To install ONLY the packages required for making documentation, run:

```bash
pip install -e ".[docs]"
```

* To install ONLY the packages required for testing, run:

```bash
pip install -e ".[test]"
```

## Pre-commit Hook

* Run:

```bash
# For help
pre-commit --help

# Install hook
pre-commit install
```

## Running The Prediction Service With Docker

```bash
# To build with docker-compose
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build

# To build the Dockerfile
docker build -t image_name:tag -f Dockerfile .

# To run the service (docker-compose)
docker-compose up

# To run the service (w/o docker-compose)
docker run -it -p 8000:8000 image_name:tag
```

## Stopping The Service

```bash

# (docker-compose)
docker-compose down
```
