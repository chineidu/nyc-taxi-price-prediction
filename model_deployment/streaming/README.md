# Machine Learning for Streaming

## Steps

* Create IAM role
* Create a Lambda function and test it
* Create a Kinesis stream
* Connect the Lambda function to the stream
* Send the records

Links

* [Tutorial: Using Amazon Lambda with Amazon Kinesis](https://docs.amazonaws.cn/en_us/lambda/latest/dg/with-kinesis-example.html)

## Code snippets

### Sending data

1. Create a lambda function and a Kinesis stream. I called the Kinesis stream `ride_events` in this particular example.


```bash
KINESIS_STREAM_INPUT=ride_events
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data "Hello, this is a test."
```

Decoding base64

```python
base64.b64decode(data_encoded).decode('utf-8')
```

Record example

```json
{
    "ride": {
        "DOLocationID": 130,
        "payment_type": 2,
        "PULocationID": 115,
        "RatecodeID": 1.0,
        "total_amount": 12.2,
        "tpep_pickup_datetime": "2022-02-01 14:28:05",
        "trip_distance": 2.34,
        "VendorID": 1
    },
    "ride_id": 123
}
```

Sending this record

```bash
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data '{
       "ride": {
           "DOLocationID": 130,
           "payment_type": 2,
           "PULocationID": 115,
           "RatecodeID": 1.0,
           "total_amount": 12.2,
           "tpep_pickup_datetime": "2022-02-01 14:28:05",
           "trip_distance": 2.34,
           "VendorID": 1
       },
       "ride_id": 100233
   }'
```

### Test event


```json
{
  "Records": [
    {
      "kinesis": {
        "kinesisSchemaVersion": "1.0",
        "partitionKey": "1",
        "sequenceNumber": "49636674106407327729976759147118224854495581328161898498",
        "data": "eyJyaWRlIjogeyJET0xvY2F0aW9uSUQiOiAxMzAsICJwYXltZW50X3R5cGUiOiAyLCAiUFVMb2NhdGlvbklEIjogMTE1LCAiUmF0ZWNvZGVJRCI6IDEuMCwgInRvdGFsX2Ftb3VudCI6IDEyLjIsICJ0cGVwX3BpY2t1cF9kYXRldGltZSI6ICIyMDIyLTAyLTAxIDE0OjI4OjA1IiwgInRyaXBfZGlzdGFuY2UiOiAyLjM0LCAiVmVuZG9ySUQiOiAxfSwgInJpZGVfaWQiOiAxMjN9",
        "approximateArrivalTimestamp": 1672650485.394
      },
      "eventSource": "aws:kinesis",
      "eventVersion": "1.0",
      "eventID": "shardId-000000000000:49636674106407327729976759147118224854495581328161898498",
      "eventName": "aws:kinesis:record",
      "invokeIdentityArn": "arn:aws:iam::126946216053:role/lambda_kinesis_custom",
      "awsRegion": "eu-west-1",
      "eventSourceARN": "arn:aws:kinesis:eu-west-1:126946216053:stream/ride_events"
    }
  ]
}
```

### Reading from the stream

```bash
KINESIS_STREAM_OUTPUT='ride_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo $RESULT | jq 

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode | jq
``` 


### Running the test

```bash
export PREDICTIONS_STREAM_NAME="ride_predictions"
export RUN_ID="e1efc53e9bd149078b0c12aeaa6365df"
export TEST_RUN="True"

python test.py
```

### Putting everything to Docker

```bash
docker build -t stream-model-duration:v1 .

docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="e1efc53e9bd149078b0c12aeaa6365df" \
    -e TEST_RUN="True" \
    -e AWS_DEFAULT_REGION="eu-west-1" \
    stream-model-duration:v1
```

URL for testing:

* http://localhost:8080/2015-03-31/functions/function/invocations



### Configuring AWS CLI to run in Docker

To use AWS CLI, you may need to set the env variables:

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="e1efc53e9bd149078b0c12aeaa6365df" \
    -e TEST_RUN="True" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    stream-model-duration:v1
```

Alternatively, you can mount the `.aws` folder with your credentials to the `.aws` folder in the container:

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="e1efc53e9bd149078b0c12aeaa6365df" \
    -e TEST_RUN="True" \
    -v c:/Users/alexe/.aws:/root/.aws \
    stream-model-duration:v1
```

### Publishing Docker images

Creating an ECR repo

```bash
aws ecr create-repository --repository-name duration-model
```

Logging in

```bash
$(aws ecr get-login --no-include-email)
```

Pushing 

```bash
REMOTE_URI="387546586013.dkr.ecr.eu-west-1.amazonaws.com/duration-model"
REMOTE_TAG="v1"
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE="stream-model-duration:v1"
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```
