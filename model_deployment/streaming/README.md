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

```python
# I used Python's API instead of the AWS CLI to send the record
def send_events(*, event: tp.Any) -> tp.Dict:
    """This is used to send events to the Kinesis stream"""
    client = boto3.client("kinesis")
    stream_name = "ride_events"

    response = client.put_record(
        StreamName=stream_name, Data=json.dumps(event), PartitionKey="1"
    )

    pp(json.dumps(event))
    return response

event = {
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
producer = send_events(event=event)
```

### Test event


```json
// The event above generated the record base64 encoded below:
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
export RUN_ID="98f43706f6184694be1ee10c41c7b69d"
export TEST_RUN="True"

python app.py
```

### Putting everything to Docker

* The Dockerfile used to build the image is located in the `streaming` directory.

```bash
docker build -t stream-model-duration:v1 -f Dockerfile .
```

### Configuring AWS CLI to run in Docker

To use AWS CLI, you may need to set the env variables:

```bash
# Set env
export AWS_ACCESS_KEY_ID="your_secret_key"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"

docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e TEST_RUN="True" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e AWS_DEFAULT_REGION="eu-west-1" \
    stream-model-duration:v1
```

Alternatively, you can mount the `.aws` folder with your credentials to the `.aws` folder in the container:

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e TEST_RUN="True" \
    -v ~/.aws:/root/.aws \
    stream-model-duration:v1
```

URL for testing:

* http://localhost:8080/2015-03-31/functions/function/invocations

* To test, run:

```console
python run_docker.py
```

### Publishing Docker images

Creating an ECR repo

```bash
# This command generates a `repositoryUri` which will be required to push to `ECR`
aws ecr create-repository --repository-name ride-duration-model
```

#### Logging in

* Authenticate (Log in)

```bash
export repository_name="126946216053.dkr.ecr.eu-west-1.amazonaws.com/ride-duration-model"
export aws_region="eu-west-1"
export aws_account="enter-your-account-id"

aws ecr get-login-password \
    | docker login \
        --password-stdin \
        --username AWS \
        "${aws_account}.dkr.ecr.${aws_region}.amazonaws.com/${repository_name}"
```

### Pushing

#### Note

`REMOTE_URI` and `repository_name` are the same as: `repositoryUri`

```bash
export REMOTE_URI="126946216053.dkr.ecr.eu-west-1.amazonaws.com/ride-duration-model"
export REMOTE_TAG="v1"
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE="stream-model-duration:v1"
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```
