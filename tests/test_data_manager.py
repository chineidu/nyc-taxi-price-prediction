"""
This module is used to test the functions used for loading
and manipulating data.

author: Chinedu Ezeofor
"""

import pandas as pd
import pytest

from src.config.core import TRAINED_MODELS_FILEPATH, config

# Custom Imports
from src.processing.data_manager import (
    load_data,
    load_model,
    get_unique_IDs,
    validate_input,
    split_train_data,
    validate_training_input,
    split_into_features_n_target,
)


def test_split_into_features_n_target(test_data: pd.DataFrame) -> None:
    """
    This function is tests the splitting of a DF into features and target.
    """
    # Given
    target = config.model_config.TARGET
    data = test_data.copy().iloc[:5]
    expected_output = [
        2.5974910105351463,
        2.920469789053444,
        3.204776900488699,
        3.0483247236731614,
        3.307619034702589,
    ]

    # When
    X, y = split_into_features_n_target(data=data, target=target)

    # Then
    assert X is not None
    assert expected_output == list(y)


def test_split_into_features_n_target_wf_error(
    test_data_no_target: pd.DataFrame,
) -> None:
    """
    This function is tests the splitting of a DF into features and target
    when the target variable is NOT present.
    """
    # Given
    target = config.model_config.TARGET

    # When
    with pytest.raises(NotImplementedError) as exc_info:
        _ = split_into_features_n_target(data=test_data_no_target, target=target)

    # Then
    assert exc_info.type is NotImplementedError
    assert exc_info.value.args[0] == "Unsupported Dataframe"


def test_validate_input(test_data: pd.DataFrame) -> None:
    """This tests the validation of input data."""
    # Given
    test_data = test_data.iloc[:20].copy()
    expected_output = {
        "DOLocationID",
        "payment_type",
        "PULocationID",
        "RatecodeID",
        "total_amount",
        "tpep_pickup_datetime",
        "trip_distance",
        "VendorID",
    }

    # When
    data, error = validate_input(data=test_data)

    # Then
    assert expected_output == set(data.columns)
    assert error is None


def test_validate_training_input(test_data: pd.DataFrame) -> None:
    """This tests the validation of training data."""
    # Given
    test_data = test_data.iloc[:20].copy()
    expected_output = {
        "airport_fee",
        "congestion_surcharge",
        "day_of_week",
        "DOLocationID",
        "extra",
        "fare_amount",
        "hour_of_day",
        "improvement_surcharge",
        "mta_tax",
        "passenger_count",
        "payment_type",
        "RatecodeID",
        "PULocationID",
        "store_and_fwd_flag",
        "tip_amount",
        "tolls_amount",
        "total_amount",
        "tpep_dropoff_datetime",
        "tpep_pickup_datetime",
        "trip_distance",
        "VendorID",
    }

    # When
    data, error = validate_training_input(data=test_data)

    # Then
    assert expected_output == set(data.columns)
    assert error is None


def test_load_model() -> None:
    """This tests the loading of the predictive model"""
    # Given
    filename = config.path_config.MODEL_PATH

    # When
    trained_model = load_model(filename=filename)

    # Then
    for f_ in TRAINED_MODELS_FILEPATH.iterdir():
        assert f_.name in filename
    assert trained_model.named_steps


def test_get_unique_IDs(test_data: pd.DataFrame) -> None:
    """Docs"""
    # Given
    test_data = test_data.iloc[:10].copy()
    expected_output = 10

    # When
    test_data["id"] = test_data["VendorID"].apply(get_unique_IDs)

    # Then
    assert expected_output == len(test_data["id"])


def test_load_data() -> None:
    """Docs"""
    # Given
    filename = config.path_config.TEST_DATA
    expected_output = 10

    # When
    result = load_data(filename=filename).iloc[:10]

    # Then
    assert expected_output == len(result)
    assert result.columns is not None


def test_split_train_data(test_data: pd.DataFrame) -> None:
    """Docs"""
    # Given
    test_data = test_data.iloc[:10].copy()

    # When
    X_train, X_validate, y_train, y_validate = split_train_data(
        data=test_data,
        target=config.model_config.TARGET,
        test_size=config.model_config.TEST_SIZE,  # 0.1
        random_state=config.model_config.RANDOM_STATE,
    )

    # Then
    assert test_data.shape[0] == X_train.shape[0] + X_validate.shape[0]
    assert test_data.shape[0] == y_train.shape[0] + y_validate.shape[0]
