"""
This module contains utility functions for the
Kinesis streaning service.

author: Chinedu Ezeofor
"""

import os
import json
import typing as tp
import boto3
import base64

import pandas as pd
import mlflow

# Custom imports
from model_deployment.batch_deploy.utilities import get_predictions

# Environment variables
RIDE_PREDICTIONS_STREAM_NAME = os.getenv("RIDE_PREDICTIONS", "ride_predictions")
RUN_ID = os.getenv("RUN_ID", "98f43706f6184694be1ee10c41c7b69d")
TEST_RUN = os.getenv("TEST_RUN", "False") == "True"

kinesis_client = boto3.client("kinesis")


def predict(*, data: pd.DataFrame):
    S3_BUCKET_NAME = f"s3://mlflow-model-registry-neidu/1/{RUN_ID}/artifacts/model"
    model = model = mlflow.pyfunc.load_model(model_uri=f"{S3_BUCKET_NAME}")
    result = model.predict(data)[0]
    return float(result)


def prepare_data(*, features: tp.Dict):
    data = features.get("ride")
    df = pd.DataFrame(data, index=[0])
    df["tpep_pickup_datetime"] = pd.to_datetime(
        df["tpep_pickup_datetime"], errors="coerce"
    )
    return df


def lambda_handler(*, event: tp.Dict, context=None):
    predictions = []

    for record in event["Records"]:
        data = record.get("kinesis").get("data")
        decoded_data = base64.b64decode(data).decode("utf-8")
        ride_events = json.loads(decoded_data)

        # Add ID
        ride_id = ride_events.get("ride_id")
        data = prepare_data(features=ride_events)
        prediction = predict(data=data)

        pred_event = {
            "model": "ride_duration_prediction_model",
            "version": "123",
            "prediction": {"ride_duration": prediction, "ride_id": ride_id},
        }

        if not TEST_RUN:
            # Send the events to another kinesis stream
            kinesis_client.put_record(
                StreamName=RIDE_PREDICTIONS_STREAM_NAME,
                Data=json.dumps(pred_event),
                PartitionKey=str(ride_id),
            )

        predictions.append(pred_event)

    return {
        "predictions": predictions,
    }
