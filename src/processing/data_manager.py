"""
This module is used to load the data.

author: Chinedu Ezeofor
"""
import typing as tp

import joblib

# Standard imports
import numpy as np
import pandas as pd
from pydantic import ValidationError
from sklearn.pipeline import Pipeline

# Custom Imports
from src.config.schema import ValidateInputSchema, ValidateTrainingData
from src.config.core import DATA_FILEPATH, TRAINED_MODELS_FILEPATH


Estimator = tp.Union[Pipeline, tp.Any]  # Alias for estimator


def load_data(*, filename: str) -> pd.DataFrame:
    """This returns the data as a Pandas DF.

    Params:
    -------
    filename (Path): The input filepath.

    Returns:
    --------
    data (Pandas DF): The loaded DF.
    """
    filename = DATA_FILEPATH / filename
    filename = str(filename)
    data = (
        pd.read_csv(filename) if filename.endswith("csv") else pd.read_parquet(filename)
    )
    TRIP_DUR_THRESH = 60  # trip_duration
    TRIP_DIST_THRESH = 30  # trip_distance
    TOTAL_AMT_THRESH = 100  # total_amount
    MIN_THRESH = 0

    if filename.endswith("parquet"):

        def calculate_trip_duration(data: pd.DataFrame) -> pd.DataFrame:
            """This returns a DF containing the calculated trip_duration in minutes."""
            data = data.copy()
            # Convert to minutes
            MINS = 60
            trip_duration = data["tpep_dropoff_datetime"] - data["tpep_pickup_datetime"]
            trip_duration = round(trip_duration.dt.total_seconds() / MINS, 2)
            return trip_duration

        data["trip_duration"] = calculate_trip_duration(data)
        data = data.loc[
            (data["trip_duration"] > MIN_THRESH)
            & (data["trip_duration"] <= TRIP_DUR_THRESH)
        ]
        data = data.loc[
            (data["trip_distance"] > MIN_THRESH)
            & (data["trip_distance"] <= TRIP_DIST_THRESH)
        ]
        data = data.loc[
            (data["total_amount"] > MIN_THRESH)
            & (data["total_amount"] <= TOTAL_AMT_THRESH)
        ]
        data["trip_duration"] = np.log1p(data["trip_duration"])  # Log transform
    return data


def validate_training_input(
    *,
    data: pd.DataFrame,
) -> tp.Tuple[pd.DataFrame, tp.Union[None, str]]:
    """This is used to validate the training data using a Pydantic Model.

    Params:
    -------
    data (Pandas DF): DF containing the training data.

    Returns:
    --------
    data (Pandas DF): The validated DF.
    error (str or None): None if there's no error else a str.
    """
    # load the data
    data = data.copy()
    error = None
    # Validate the data. Convert NaNs to None
    try:
        _ = ValidateTrainingData(
            inputs=data.replace({np.nan: None}).to_dict(orient="records")
        )
        return (data, error)
    except ValidationError as err:
        error = err.json()
        return (data, error)


def validate_input(
    *,
    data: pd.DataFrame,
) -> tp.Tuple[pd.DataFrame, tp.Union[None, str]]:
    """This is used to validate the input data using a Pydantic Model.

    Params:
    -------
    data (Pandas DF): DF containing the training data.

    Returns:
    --------
    data (Pandas DF): The validated DF.
    error (str or None): None if there's no error else a str.
    """
    # load the data
    data = data.copy()
    error = None

    # Validate the data. Convert NaNs to None
    try:
        _ = ValidateInputSchema(
            inputs=data.replace({np.nan: None}).to_dict(orient="records")
        )
        return (data, error)
    except ValidationError as err:
        error = err.json()
        return (data, error)


def save_model(*, filename: str, pipe: Pipeline) -> None:
    """This is used to persit a model.

    Params:
    -------
    filename (Path): Filepath to save the data.

    Returns:
    --------
    None
    """
    filename = TRAINED_MODELS_FILEPATH / filename 

    print("==========  Saving Model ========== ")
    with open(filename, "wb") as file:
        joblib.dump(pipe, file)


def load_model(*, filename: str) -> Estimator:
    """This is used to load the trained model.

    Params:
    -------
    None

    Returns:
    --------
    Estimator: The trained model.
    """
    filename =  TRAINED_MODELS_FILEPATH / filename 
    print("==========  Loading Model ========== ")
    with open(filename, "rb") as file:
        trained_model = joblib.load(filename=file)
    return trained_model
