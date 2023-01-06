"""
This module is used to simulate the model usage in production.
i.e send requests to the prediction service.

source: https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/send_data.py
"""
import json
import uuid
from datetime import datetime
from time import sleep

import pyarrow.parquet as pq
import requests

URL = "0.0.0.0:8000/predict"

table = pq.read_table("green_tripdata_2022-01.parquet")
data = table.to_pylist()


class DateTimeEncoder(json.JSONEncoder):
    """This is used to encode datetime objects."""
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


with open("target.csv", 'w') as f_target:
    for row in data:
        row['id'] = str(uuid.uuid4())  # Add ID
        duration = (row['lpep_dropoff_datetime'] - row['lpep_pickup_datetime']).total_seconds() / 60
        if duration != 0.0:
            f_target.write(f"{row['id']},{duration}\n")  # save data
        # Send data to the prediction service
        resp = requests.post(URL,
                             headers={"Content-Type": "application/json"},
                             data=json.dumps(row, cls=DateTimeEncoder)).json()
        print(f"prediction: {resp['duration']}")
        sleep(1)