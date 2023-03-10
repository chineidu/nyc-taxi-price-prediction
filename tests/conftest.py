"""
This module contains all the pytest fixtures.

author: Chinedu Ezeofor
"""
import typing as tp

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from prefect.testing.utilities import prefect_test_harness

from src.api import app

# Custom Imports
from src.config.core import config
from tests.utilities import MockModel, load_encoded_data
from src.processing.data_manager import load_data


@pytest.fixture()
def test_data() -> pd.DataFrame:
    """This is used to load the test data."""
    data = load_data(filename=config.path_config.TEST_DATA)
    return data.iloc[:2_000]


@pytest.fixture()
def test_data_no_target() -> pd.DataFrame:
    """This is used to load the test data."""
    data = load_data(filename=config.path_config.TEST_DATA_WF_NO_TARGET)
    return data


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


@pytest.fixture()
def client() -> tp.Generator:
    """Config for FastAPI"""
    with TestClient(app) as _client:
        yield _client
        app.dependency_overrides = {}


@pytest.fixture()
def test_event() -> tp.Dict:
    """Sample event for testing lambda function."""
    event = {
        "ride": {
            "DOLocationID": 130,
            "payment_type": 2,
            "PULocationID": 115,
            "RatecodeID": 1.0,
            "total_amount": 12.2,
            "tpep_pickup_datetime": "2022-02-01 14:28:05",
            "trip_distance": 2.34,
            "VendorID": 1,
        },
        "ride_id": 123,
    }
    return event


@pytest.fixture()
def encoded_data() -> tp.Dict:
    """This loads the encoded data as a fixture."""
    return load_encoded_data()


@pytest.fixture()
def sample_data_event() -> tp.Dict:
    """Test data for Lambda event."""
    data = {
        "DOLocationID": 130,
        "payment_type": 2,
        "PULocationID": 115,
        "RatecodeID": 1.0,
        "total_amount": 12.2,
        "tpep_pickup_datetime": "2022-02-01 14:28:05",
        "trip_distance": 2.34,
        "VendorID": 1,
    }
    df = pd.DataFrame(data, index=[0])
    # Convert to datetime
    df = df.assign(
        tpep_pickup_datetime=lambda x: pd.to_datetime(
            x["tpep_pickup_datetime"], errors="coerce"
        )
    )
    return df


@pytest.fixture()
def kinesis_stream() -> tp.Dict:
    """Load a Kinesis stream"""
    encoded_data = load_encoded_data()
    stream = {
        "Records": [
            {
                "kinesis": {
                    "data": encoded_data,
                },
            }
        ]
    }
    return stream


@pytest.fixture()
def mock_model() -> MockModel:
    """This loads the mock model."""
    return MockModel(value=10)
