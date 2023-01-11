"""
This module contains helper classes/functions used for
unit testing.

author: Chinedu Ezeofor
"""
import os
import typing as tp
from pathlib import Path

import pandas as pd

from model_deployment.streaming.lambda_function import decode_record, prepare_data

RIDE_PREDICTIONS_STREAM_NAME = os.getenv("RIDE_PREDICTIONS", "ride_predictions")
TEST_RUN = os.getenv("TEST_RUN", "False") == "True"


class MockModel:
    def __init__(self, value: int) -> None:
        self.value = value

    def predict(self, data: pd.DataFrame) -> float:
        """This is a mock prediction method."""
        result = data["total_amount"].values[0]
        return result * self.value


class MockLambdaHandler:
    def __init__(self) -> None:
        self.test_run = TEST_RUN
        return None

    def lambda_handler(self, event: tp.Dict, context=None) -> tp.Dict:
        """This is a mock lambda function."""
        predictions = []

        for record in event["Records"]:
            data = record.get("kinesis").get("data")
            ride_events = decode_record(data=data)

            # Add ID
            ride_id = ride_events.get("ride_id")
            data = prepare_data(features=ride_events)

            prediction = 9.47

            pred_event = {
                "model": "ride_duration_prediction_model",
                "version": "123",
                "prediction": {"ride_duration": prediction, "ride_id": ride_id},
            }

            predictions.append(pred_event)

        return {
            "predictions": predictions,
        }


def load_encoded_data() -> tp.Dict:
    """This function loads the encoded data."""
    BASE_DIR = Path(__name__).absolute().parent
    with open(f"{BASE_DIR}/tests/encoded_data.txt", "r", encoding="utf-8") as file:
        encoded_data = file.read().strip()
    return encoded_data
