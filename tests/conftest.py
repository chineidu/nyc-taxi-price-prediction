import pandas as pd
import pytest
from prefect.testing.utilities import prefect_test_harness
from fastapi.testclient import TestClient

# Custom Imports
from src.config.core import config
from src.processing.data_manager import load_data
from src.api import app

import typing as tp


@pytest.fixture()
def test_data() -> pd.DataFrame:
    """This is used to load the test data."""
    data = load_data(filename=config.path_config.TEST_DATA)
    return data.iloc[:2_000]


@pytest.fixture()
def train_data() -> pd.DataFrame:
    """This is used to load the train data."""
    data = load_data(filename=config.path_config.TRAIN_DATA)
    return data.sample(n=10_000, random_state=config.model_config.RANDOM_STATE)


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    """Config for Prefect."""
    with prefect_test_harness():
        yield


# @pytest.fixture(scope="module")
# def test_data() -> pd.DataFrame:
#     data = load_data(filepath=config.app_config.test_data_file, is_train=False)
#     return data.head(1)


@pytest.fixture()
def client() -> tp.Generator:
    """Config for FastAPI"""
    with TestClient(app) as _client:
        yield _client
        app.dependency_overrides = {}
