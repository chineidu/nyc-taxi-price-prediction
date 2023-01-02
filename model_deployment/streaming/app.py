from model_deployment.streaming.lambda_function import (
    lambda_handler,
    prepare_data,
    predict,
)
from src import logger


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
"""


"""



if __name__ == "__main__":
    from pprint import pprint as pp
    from src import logger

    # df = prepare_data(features=event)
    # pp(df)
    # print()
    # pred = predict(data=df)
    # pp(pred)

    response = lambda_handler(event=event, context=None)
    pp(response)
    logger.info("Done ...")
