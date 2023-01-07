"""
This module is used to simulate the model usage in production.
i.e send requests to the prediction service.

source: https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/send_data.py
"""
import json
import uuid
from datetime import datetime
from time import sleep
from pprint import pprint as pp

import pyarrow.parquet as pq
import requests

URL = "http://0.0.0.0:8001/predict"

table = pq.read_table("yellow_tripdata_2022-01.parquet")
data = table.to_pylist()


class DateTimeEncoder(json.JSONEncoder):
    """This is used to encode datetime objects."""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


with open("target.csv", "w") as f_target:
    for row in data:
        row["id"] = str(uuid.uuid4())  # Add ID
        duration = (
            row["tpep_dropoff_datetime"] - row["tpep_pickup_datetime"]
        ).total_seconds() / 60
        row["tpep_pickup_datetime"] = str(row["tpep_pickup_datetime"])
        row["tpep_dropoff_datetime"] = str(row["tpep_dropoff_datetime"])
        row["duration"] = round(duration, 2)
        if duration != 0.0:
            f_target.write(f"{row['id']},{duration}\n")  # save data

        # Send data to the prediction service
        resp = requests.post(
            URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(row, cls=DateTimeEncoder),
        ).json()

        # pp(row)
        pp(f"prediction: {resp['trip_duration']}")
        sleep(1)
