"""
This module is the integration test for testing the Docker image built
for the streaming service.

author: Chinedu Ezeofor
"""
import requests
from pprint import pprint as pp

from deepdiff import DeepDiff


def test_docker_integration() -> None:
    # Given
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
    event = {
        "Records": [
            {
                "kinesis": {
                    "kinesisSchemaVersion": "1.0",
                    "partitionKey": "1",
                    "sequenceNumber": "49636674106407327729976759147118224854495581328161898498",
                    "data": "eyJyaWRlIjogeyJET0xvY2F0aW9uSUQiOiAxMzAsICJwYXltZW50X3R5cGUiOiAyLCAiUFVMb2NhdGlvbklEIjogMTE1LCAiUmF0ZWNvZGVJRCI6IDEuMCwgInRvdGFsX2Ftb3VudCI6IDEyLjIsICJ0cGVwX3BpY2t1cF9kYXRldGltZSI6ICIyMDIyLTAyLTAxIDE0OjI4OjA1IiwgInRyaXBfZGlzdGFuY2UiOiAyLjM0LCAiVmVuZG9ySUQiOiAxfSwgInJpZGVfaWQiOiAxMjN9",
                    "approximateArrivalTimestamp": 1672650485.394,
                },
                "eventSource": "aws:kinesis",
                "eventVersion": "1.0",
                "eventID": "shardId-000000000000:49636674106407327729976759147118224854495581328161898498",
                "eventName": "aws:kinesis:record",
                "invokeIdentityArn": "arn:aws:iam::126946216053:role/lambda_kinesis_custom",
                "awsRegion": "eu-west-1",
                "eventSourceARN": "arn:aws:kinesis:eu-west-1:126946216053:stream/ride_events",
            }
        ]
    }
    url = "http://localhost:8080/2015-03-31/functions/function/invocations"
    respose = requests.post(url, json=event).json()
    pp(respose)
    d_diff = DeepDiff(expected_output, respose)  # It compares the inputs

    # Then
    assert "values_changed" not in d_diff
