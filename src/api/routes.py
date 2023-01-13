"""
This module contains the endpoints for making predictions
and checking the health of the API.

author: Chinedu Ezeofor
"""
import pandas as pd
from loguru import logger
from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder

# Custom imports
from src import __version__ as model_version
from src.predict import make_predictions
from src.api.config import settings
from src.api.schema import APIDetails, InputDataSchema, ResponsePredictSchema

api_router = APIRouter()


@api_router.get(
    path="/health/",
    response_model=APIDetails,
    status_code=status.HTTP_200_OK,
)
def health():  # pragma: no cover
    """This displays the API details."""
    logger.info("Fetching API details ...")
    return {
        "project_name": settings.PROJECT_NAME,
        "api_version": settings.API_FULL_VERSION,
        "model_version": model_version,
    }


@api_router.post(
    path="/predict/",
    response_model=ResponsePredictSchema,
    status_code=status.HTTP_200_OK,
)
def predict_trip_duration(input_data: InputDataSchema) -> ResponsePredictSchema:
    """This endpoint is used for predicting the trip
    duration in minutes.

    Example:
        >>> "inputs": [
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
        result: 3.12

    Params:
        input_data (InputDataSchema): This is a Pydantic schema for validating
        the input data.

    Returns:
        pred (ResponsePredictSchema): This is a Pydantic schema for validating
        the output data.
    """
    # Get the input data
    input_data = input_data.inputs  # type: ignore
    logger.info("Fetching data ...")
    data = pd.DataFrame(jsonable_encoder(input_data))  # Convert to DF

    # Get prediction
    logger.info("Making predictions on data ...")
    pred = make_predictions(data=data)
    return pred
