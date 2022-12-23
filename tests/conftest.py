import pandas as pd
import pytest

# Custom Imports
from src.config.core import config
from src.processing.data_manager import load_data


@pytest.fixture()
def test_data() -> pd.DataFrame:
    """This is used to load the test data."""
    data = load_data(filename=config.path_config.TEST_DATA)
    return data.iloc[:2_000]
