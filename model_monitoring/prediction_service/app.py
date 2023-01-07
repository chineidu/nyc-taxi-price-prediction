"""
This module is used for making predictions via the API's
endpoint and sending the predictions for monitoring.

author: Chinedu Ezeofor
"""
import pandas as pd
import uvicorn
from fastapi import FastAPI, status
from pymongo import MongoClient

import os
import logging
import requests
import typing as tp

from utilities import InputSchema, ResponsePredictSchema, predict

EVIDENTLY_SERVICE_ADDRESS = os.getenv("EVIDENTLY_SERVICE", "http://0.0.0.0:8085")
MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27018")

mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database("prediction_service")  # Create db
collection = db.get_collection("data")  # Create collection ~= SQL table


def set_up_logger(delim: str = "::") -> tp.Any:
    """This is used to create a basic logger."""
    format_ = f"[%(levelname)s] {delim} %(asctime)s {delim} %(message)s"
    logging.basicConfig(level=logging.INFO, format=format_)
    logger = logging.getLogger(__name__)
    return logger


logger = set_up_logger(delim="")
app = FastAPI()
model_version = "v1"


@app.post(
    path="/predict",
    # response_model=ResponsePredictSchema,
    status_code=status.HTTP_200_OK,
)
def predict_trip_duration(input_data: InputSchema) -> None:
    """This endpoint is used for predicting the trip
    duration in minutes.
    """
    # Get the input data
    input_data = input_data.dict()
    logger.info("Fetching data ...")
    data = pd.DataFrame([input_data])  # Convert to DF
    data["tpep_pickup_datetime"] = pd.to_datetime(
        data["tpep_pickup_datetime"], errors="coerce"
    )
    logger.info("Making predictions on data ...")
    pred = {}
    y_pred = predict(data=data)
    pred["trip_duration"] = y_pred
    pred["model_version"] = model_version

    logger.info("Saving data to Mongo DB ...")
    save_to_mongo_db(data=input_data, prediction=y_pred)
    logger.info("Sending data to Evidently Service ...")
    save_to_evidently_service(data=input_data, prediction=y_pred)
    return pred


def save_to_mongo_db(*, data: pd.DataFrame, prediction: float) -> None:
    """This is used to save the input data with the prediction to
    the Mongo DB."""
    record = data.copy()
    record["prediction"] = prediction
    collection.insert_one(record)


def save_to_evidently_service(*, data: pd.DataFrame, prediction: float) -> None:
    """This is used to save the input data with the prediction to
    the Evidently Monitoring Service for monitoring."""
    record = data.copy()
    record["prediction"] = prediction
    requests.post(url=f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/taxi", json=record)


if __name__ == "__main__":
    # Use this for debugging purposes only
    logger.warning("Running in development mode. Do not run like this in production.")
    host, port = "0.0.0.0", 8000

    uvicorn.run("app:app", host=host, port=port, log_level="info", reload=True)
