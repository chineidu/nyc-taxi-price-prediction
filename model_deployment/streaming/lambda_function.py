"""
This module contains utility functions for the
Kinesis streaning service.

author: Chinedu Ezeofor
"""

import os
import json
import typing as tp
import boto3
from pathlib import Path
from pprint import pprint as pp
import joblib
import base64

import numpy as np
import pandas as pd


# Environment variables
RIDE_PREDICTIONS_STREAM_NAME = os.getenv("RIDE_PREDICTIONS", "ride_predictions")
TEST_RUN = os.getenv("TEST_RUN", "False") == "True"

kinesis_client = boto3.client("kinesis")


def predict(*, data: pd.DataFrame) -> float:
    """This is used to make predictions on unseen data using
    the trained model."""
    fp = "./trained_models/model.pkl"
    with open(fp, "rb") as file:
        model = joblib.load(file)

    result = model.predict(data)[0]
    result = np.expm1(result)
    return round(float(result), 2)


def prepare_data(*, features: tp.Dict) -> pd.DataFrame:
    """This is used to preprocess the data."""
    data = features.get("ride")
    df = pd.DataFrame(data, index=[0])
    df["tpep_pickup_datetime"] = pd.to_datetime(
        df["tpep_pickup_datetime"], errors="coerce"
    )
    return df


def send_events(event: tp.Any) -> tp.Dict:
    """This is used to send events to the Kinesis stream"""
    client = boto3.client("kinesis")
    RIDE_EVENTS_STREAM_NAME = "ride_events"
    response = client.put_record(
        StreamName=RIDE_EVENTS_STREAM_NAME, Data=json.dumps(event), PartitionKey="1"
    )
    pp(json.dumps(event))
    return response

def decode_record(*, data: tp.Dict) -> tp.Dict:
    """This is used to decode the encoded data."""
    decoded_data = base64.b64decode(data).decode("utf-8")
    ride_events = json.loads(decoded_data)
    return ride_events


def lambda_handler(event: tp.Dict, context=None) -> tp.Dict:
    """This is the lambda function that consumes events
    from the Kinesis stream. It decodes the encoded record
    and makes the trip prediction using the trained model."""
    predictions = []

    for record in event["Records"]:
        data = record.get("kinesis").get("data")
        ride_events = decode_record(data=data)

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
            # Send the events to prediction stream
            kinesis_client.put_record(
                StreamName=RIDE_PREDICTIONS_STREAM_NAME,
                Data=json.dumps(pred_event),
                PartitionKey=str(ride_id),
            )

        predictions.append(pred_event)

    return {
        "predictions": predictions,
    }
