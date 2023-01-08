"""
This module is used to simulate the model usage in production.
i.e send requests to the prediction service.

source: https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/05-monitoring/send_data.py
"""
import json
import uuid
import typing as tp
from argparse import ArgumentParser
from datetime import datetime
from time import sleep
from pprint import pprint as pp

import pyarrow.parquet as pq
import requests

URL = "http://0.0.0.0:8001/predict"

fp = "reduced_data.parquet"  # "yellow_tripdata_2022-01.parquet"
table = pq.read_table(fp)
data = table.to_pylist()


def load_batch_data(*, filename: str) -> tp.List:
    """This is used to load the data which will be
    used for sending batch requests."""
    table = pq.read_table(source=filename)
    data = table.to_pylist()
    return data

def get_parser()->float:
    """This is used to obtain value(s) from the CLI.
    It returns a float value for the timer."""
    parser = ArgumentParser()
    parser.add_argument(
        "-t",
        "--timer",
        help="The duration of the timer in seconds. e.g 0.2",
        type=float,
        required=False,
        default=0.01,
    )
    args = parser.parse_args()
    return args.timer

class DateTimeEncoder(json.JSONEncoder):
    """This is used to encode datetime objects."""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def send_data(*, timer: float) -> None:
    """This is used to simulate the sending of requests to the predictive service"""
    data = load_batch_data(filename=fp)
    print(f"Timer is set to: {timer}s\n")

    with open("target.csv", "w") as f_target:
        for row in data:
            row["id"] = str(uuid.uuid4())  # Add ID
            duration = (
                row["tpep_dropoff_datetime"] - row["tpep_pickup_datetime"]
            ).total_seconds() / 60
            row["tpep_pickup_datetime"] = str(row["tpep_pickup_datetime"])
            row["tpep_dropoff_datetime"] = str(row["tpep_dropoff_datetime"])

            # Don't make predictions for trips with 0 miles (duration)
            if duration != 0.0:
                f_target.write(f"{row['id']},{duration}\n")  # save data

            # Send data to the prediction service
            resp = requests.post(
                URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(row, cls=DateTimeEncoder),
            ).json()

            pp(f"prediction: {resp['trip_duration']}")
            sleep(timer)
    print("Done!!!")


if __name__ == "__main__":
    # Get the timer from the CLI
    timer = get_parser()
    # Run the main program
    send_data(timer=timer)
