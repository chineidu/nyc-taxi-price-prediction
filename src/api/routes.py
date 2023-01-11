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
def predict_trip_duration(input_data: InputDataSchema):
    """This endpoint is used for predicting the trip
    duration in minutes.
    """
    # Get the input data
    input_data = input_data.inputs  # type: ignore
    logger.info("Fetching data ...")
    data = pd.DataFrame(jsonable_encoder(input_data))  # Convert to DF

    # Get prediction
    logger.info("Making predictions on data ...")
    pred = make_predictions(data=data)
    return pred
