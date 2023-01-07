# Model Monitoring

This module simulates model monitoring in production. The `prediction service` is used for making predictions on live data which is stored on a `mongodb` instance and `evidently_service` is used to monitor the deployed model.

`Evidently_service` is integrated with `Prometheus` and `Graphana` for storing the live metrics and visualizing the metrics respectively.

In summary, the deployed model was monitored using awesome open source tools like:

1. **Evidently** (for monitoring data drift, target drift, model decay, model performance, etc)
2. **Graphana** (for visualizing the metrics stored on Prometheus)
3. **Prometheus** (for storing timeseries data obtained from evidently)
4. **Mongo DB** (for storing the records)
5. **Prefect** (for orchestration)

## Steps

1. Create a virtual envirionment and install the required dependencies by running:

```console
pip install -r requirements.txt
```

2. To download the data, run the `prepare.py` script.

```console
python prepare.py
```

3. Start the services using the `docker-compose.yml` file by running:

```console
# Build the docker images
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build

# Start the services
docker-compose up
```

4. Send the data (this mimics the usage of the `prediction_service` in production by running:)

```console
python send_data.py
```

* You can manually send data by sending a `POST` request to the endpoint:

```html
http://localhost:8001/predict
```
with the payload:

```json
{
    "DOLocationID": 107,
    "payment_type": 1.0,
    "PULocationID": 181,
    "RatecodeID": 1.0,
    "total_amount": 38.4,
    "tpep_pickup_datetime": "2022-05-01 00:01:28",
    "trip_distance": 8.1,
    "VendorID": 1
}
```

5. To view the metrics using `Graphana`, visit the url:

```html
http://localhost:3000/
```

6. To check the stats of the data stored on `Prometheus`, visit:

```html
http://localhost:9091/
```

7. To check the data stored on `mongodb`, run:

```console
# To get help
python check_mongodb.py -h

# To check the 1st 4 records
python check_mongodb.py --start-index 0 --stop-index 4 -v 
```
