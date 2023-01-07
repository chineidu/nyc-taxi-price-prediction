"""
This module containes helper functions and schemas.

author: Chinedu Ezeofor
"""
import numpy as np
import pandas as pd
from pydantic import BaseModel

import os
import joblib
import typing as tp

MODEL_FILE = os.getenv("MODEL_FILE", "model.pkl")


class InputSchema(BaseModel):
    """
    Config object for input data variables.
    """

    DOLocationID: int
    payment_type: int
    PULocationID: int
    RatecodeID: float
    total_amount: float
    tpep_pickup_datetime: str
    trip_distance: float
    VendorID: int
    duration: tp.Optional[float]

    class Config:
        """Sample Payload"""

        schema_extra = {
            "example": {
                "DOLocationID": 122,
                "payment_type": 1,
                "PULocationID": 236,
                "RatecodeID": 1.0,
                "total_amount": 12.36,
                "tpep_pickup_datetime": "2022-02-01 10:15:17",
                "trip_distance": 3.17,
                "VendorID": 2,
            }
        }


class InputDataSchema(BaseModel):
    """
    Config object for input data.
    """

    inputs: tp.List[InputSchema]

    class Config:
        """Sample Payload"""

        schema_extra = {
            "example": {
                "inputs": [
                    {
                        "DOLocationID": 122,
                        "payment_type": 1,
                        "PULocationID": 236,
                        "RatecodeID": 1.0,
                        "total_amount": 12.36,
                        "tpep_pickup_datetime": "2022-02-01 10:15:17",
                        "trip_distance": 3.17,
                        "VendorID": 2,
                    }
                ]
            }
        }


class ResponsePredictSchema(BaseModel):
    """This schema validates the prediction response."""

    trip_duration: tp.Optional[float]
    model_version: tp.Optional[str]


def predict(*, data: pd.DataFrame) -> float:
    """This is used to make predictions on unseen data using
    the trained model."""
    with open(MODEL_FILE, "rb") as file:
        model = joblib.load(file)

    result = model.predict(data)[0]
    result = np.expm1(result)
    return round(float(result), 2)
