import pandas as pd
from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder

# Custom imports
from config import settings
from src.predict import make_predictions
from src import __version__ as model_version
from schema import InputDataSchema, ResponsePredictSchema, APIDetails

from loguru import logger


api_router = APIRouter()


@api_router.get(
    path="/health/",
    response_model=APIDetails,
    status_code=status.HTTP_200_OK,
)
def health():
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
    input_data = input_data.inputs  # Get the input data
    logger.info("Fetching data ...")
    data = pd.DataFrame(jsonable_encoder(input_data))  # Convert to DF

    # Get prediction
    logger.info("Making predictions on data ...")
    pred = make_predictions(data=data)
    return pred
