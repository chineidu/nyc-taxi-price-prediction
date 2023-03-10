"""
This module is used for testing the Docker image built
for the streaming service.

author: Chinedu Ezeofor
"""
import requests  # type: ignore

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
response = requests.post(url, json=event)
print(response.json())
