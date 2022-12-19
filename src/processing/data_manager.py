"""
This module is used to load the data.

author: Chinedu Ezeofor
"""

# Standard imports
import numpy as np
import pandas as pd
from pydantic import ValidationError
from schema import ValidateInputSchema, ValidateTrainingData

import typing as tp


def load_data(fp: str) -> pd.DataFrame:
    """This returns the data as a Pandas DF."""
    data = pd.read_csv(fp) if fp.endswith("csv") else pd.read_parquet(fp)
    TRIP_DUR_THRESH = 60  # trip_duration
    TRIP_DIST_THRESH = 30  # trip_distance
    TOTAL_AMT_THRESH = 100  # total_amount
    MIN_THRESH = 0

    if fp.endswith("parquet"):

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
        data[f"trip_duration"] = np.log1p(data["trip_duration"])  # Log transform
    return data


def validate_training_input(
    *,
    data: pd.DataFrame,
) -> tp.Tuple[pd.DataFrame, tp.Union[None, str]]:
    """This is used to validate the training data using a Pydantic Model."""
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
    """This is used to validate the input data using a Pydantic Model."""
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
    