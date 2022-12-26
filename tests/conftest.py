import pandas as pd
import pytest
from prefect.testing.utilities import prefect_test_harness

# Custom Imports
from src.config.core import config
from src.processing.data_manager import load_data


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
    with prefect_test_harness():
        yield
