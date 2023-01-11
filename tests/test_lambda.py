import pandas as pd

from model_deployment.streaming.lambda_function import (
    prepare_data,
    decode_record,
    lambda_handler,
)
from tests.utilities import MockLambdaHandler

import typing as tp
import json


def test_prepare_data(test_event: tp.Dict) -> None:
    # Given
    res = {
        "DOLocationID": 130,
        "payment_type": 2,
        "PULocationID": 115,
        "RatecodeID": 1.0,
        "total_amount": 12.2,
        "tpep_pickup_datetime": "2022-02-01 14:28:05",
        "trip_distance": 2.34,
        "VendorID": 1,
    }
    expected_output = pd.DataFrame(res, index=[0])
    # Convert to datetime
    expected_output = expected_output.assign(
        tpep_pickup_datetime=lambda x: pd.to_datetime(
            x["tpep_pickup_datetime"], errors="coerce"
        )
    )

    # When
    result = prepare_data(features=test_event)

    # Then
    assert expected_output.equals(result)
    assert expected_output["tpep_pickup_datetime"].equals(
        result["tpep_pickup_datetime"]
    )


def test_decode_record(encoded_data: tp.Dict) -> None:
    """this tests the decode_record function."""
    # Given
    expected_output = {
        "ride": {
            "DOLocationID": 130,
            "payment_type": 2,
            "PULocationID": 115,
            "RatecodeID": 1.0,
            "total_amount": 12.2,
            "tpep_pickup_datetime": "2022-02-01 14:28:05",
            "trip_distance": 2.34,
            "VendorID": 1,
        },
        "ride_id": 123,
    }

    # When
    result = decode_record(data=encoded_data)

    # Then
    assert expected_output == result


def test_predict_event(sample_data_event: pd.DataFrame, mock_model) -> None:
    """This is used to test the predictions used in the lambda handler."""
    # Given
    expected_output = 122.0

    # When
    result = mock_model.predict(data=sample_data_event)

    # Then
    assert expected_output == result
    assert isinstance(result, float)


def test_lambda_handler(kinesis_stream: tp.Dict) -> None:
    """This tests the lambda_handler function."""
    # Given
    from pprint import pprint as pp

    mock_lh = MockLambdaHandler()
    expected_output = {
        "predictions": [
            {
                "model": "ride_duration_prediction_model",
                "version": "123",
                "prediction": {"ride_duration": 9.47, "ride_id": 123},
            }
        ]
    }

    # When
    result = mock_lh.lambda_handler(event=kinesis_stream)

    # Then
    assert expected_output == result
