"""
This module is used to test the model training functions.

author: Chinedu Ezeofor
"""
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Custom imports
from src.train import train_model
from src.config.core import config
import src.processing.feat_engineering as fe
from src.processing.data_manager import save_model, remove_old_pipelines


# From feature-engine
from feature_engine.imputation import AddMissingIndicator, MeanMedianImputer
from feature_engine.transformation import (
    YeoJohnsonTransformer,
)
from feature_engine.selection import DropFeatures


def test_train_model(train_data: pd.DataFrame) -> None:
    """This is used to test the model training function."""
    # Given
    expected_y_validate = [
        2.930126516455997,
        1.3029127521808397,
        1.7263316639055997,
        2.47232786758114,
        1.4469189829363254,
        1.5830939370944985,
        1.6428726885203377,
        3.6933693593867885,
        2.189416394888408,
        2.531313022602156,
    ]
    expected_y_pred = [
        3.3026129386292205,
        1.5118944159832697,
        1.9196984116075355,
        2.460641046680437,
        1.7487872923637577,
        1.4586509603085802,
        1.789247276011728,
        3.7140790240006263,
        2.2939813764592034,
        2.320481252394008,
    ]

    # When
    pipe, y_validate, y_pred = train_model(train_data=train_data)
    # Save model
    save_model(filename=config.path_config.TEST_MODEL_PATH, pipe=pipe)

    # Delete model
    remove_old_pipelines(files_to_remove=None)

    # Then
    assert expected_y_validate == list(y_validate.iloc[:10])  # Series
    assert expected_y_pred == list(y_pred[:10])  # Array


def test_train_pipeline(train_data: pd.DataFrame) -> None:
    """This is used to test the model training pipeline."""
    # Given
    expected_features = [
        "DOLocationID",
        "payment_type",
        "PULocationID",
        "RatecodeID",
        "total_amount",
        "tpep_pickup_datetime",
        "trip_distance",
        "VendorID",
    ]
    expected_output = {
        "input vars": fe.SelectFeatures(
            features=[
                "DOLocationID",
                "payment_type",
                "PULocationID",
                "RatecodeID",
                "total_amount",
                "tpep_pickup_datetime",
                "trip_distance",
                "VendorID",
            ]
        ),
        "add na_flag": AddMissingIndicator(variables=["RatecodeID"]),
        "impute num_vars": MeanMedianImputer(variables=["RatecodeID"]),
        "cal day_of_week": fe.CalculateDayOfWeek(feature="tpep_pickup_datetime"),
        "cal hour_of_day": fe.CalculateHourOfDay(feature="tpep_pickup_datetime"),
        "important vars": fe.SelectFeatures(
            features=[
                "day_of_week",
                "DOLocationID",
                "hour_of_day",
                "payment_type",
                "PULocationID",
                "RatecodeID",
                "RatecodeID_na",
                "total_amount",
                "tpep_pickup_datetime",
                "trip_distance",
                "VendorID",
            ]
        ),
        "drop features": DropFeatures(features_to_drop=["tpep_pickup_datetime"]),
        "YeoJohnson transformation": YeoJohnsonTransformer(
            variables=["trip_distance", "total_amount"]
        ),
        "scale data": StandardScaler(),
        "RF model": RandomForestRegressor(
            max_depth=10, n_estimators=10, random_state=123
        ),
    }

    # When
    pipe, *_ = train_model(train_data=train_data)
    result = pipe.named_steps  # Get the steps associated with the pipeline

    # Then
    assert str(expected_output.get("drop features")) == str(result.get("drop features"))
    assert str(expected_output.get("input vars")) == str(result.get("input vars"))
    assert set(expected_features) == set(expected_output.get("input vars").features)
