# EXPERIMENT TRACKING

## Workflow

1. Create a `remote` or `local server` which will bw used to run and track the experiment. A local server was used in this scenario.
2. Create an `S3 bucket` which will serve as the model registry (It stores all the model artifacts, environments used to run the experiment, etc).
3. Create a `DB` for storing the experiment meta data. SQLite was used in this scenario.

## Start The MLFlow Server (S3 is used as the remote model registry)

```console
S3_BUCKET_NAME="your-bucket-name"

mlflow server \
    --backend-store-uri=sqlite:///mlflow.db \
    --default-artifact-root=s3://${S3_BUCKET_NAME}
```

For info on how to run the server, check [here](https://mlflow.org/docs/latest/tracking.html)

## Using A Remote Server

1. You can create an EC2 instance and configure the instance. i.e enable inbound rules so that you can ssh, send requests and connect your DB to the instance.

### Sample Command

```console
export PORT="5000"
export DB_USER="your-db-username"
export DB_PASSWORD="your-db-password"
export DB_ENDPOINT="your-db-endpoint"
export DB_NAME="your-db-name"
export DB_PORT="your-db-port"
export S3_BUCKET_NAME="your-s3-bucket"

mlflow server -h 0.0.0.0 -p $PORT \
--backend-store-uri postgresql://$DB_USER:$DB_PASSWORD@$DB_ENDPOINT:$DB_PORT/$DB_NAME \
--default-artifact-root s3://$S3_BUCKET_NAME
```

For more info on connecting to a remote server and model registry using AWS, check [here](https://github.com/chineidu/MLFlow_example/blob/main/006_mlflow_client.ipynb)
