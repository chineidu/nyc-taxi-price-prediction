import os
import json
import typing as tp
from datetime import datetime, timedelta

import numpy as np
import joblib
import pandas as pd
from prefect import flow, task, get_run_logger
from pymongo import MongoClient
from evidently import ColumnMapping
from prefect.tasks import task_input_hash
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, RegressionPreset, DataQualityPreset

MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27018")


@task(retries=3, retry_delay_seconds=10)
def upload_target_to_db(*, filename: str) -> None:
    """This is used to upload the target feature to
    the MongoDB collection.

    params:
    -------
    filename (str): The file containing the actual trip duration.
    """
    db_name = "prediction_service"
    collection_name = "data"
    with MongoClient(MONGODB_ADDRESS) as client:
        collection = client.get_database(db_name).get_collection(collection_name)
        # Load the target from the file
        with open(filename, "r") as file_in:
            for line in file_in.readlines():
                row = line.split(",")
                # Update the data in the collection
                filter = {"id": row[0]}
                updated_val = {"$set": {"target": round(float(row[1]))}}
                collection.update_one(filter, updated_val)


def predict(*, data: pd.DataFrame) -> float:
    """This is used to make predictions on unseen data using
    the trained model."""
    MODEL_FILE = os.getenv("MODEL_FILE", "./prediction_service/model.pkl")
    with open(MODEL_FILE, "rb") as file:
        model = joblib.load(file)

    pred = model.predict(data)
    pred = [(round(x)) for x in list(np.expm1(pred))]  # Convert from log to minutes
    return pred


@flow(retries=3, retry_delay_seconds=10)
def load_ref_data(*, filename: str) -> pd.DataFrame:
    """This is used to load the reference data.

    params:
    -------
    filename (str): The file containing the training data.

    Returns:
    --------
    ref_data (Pandas DF): DF containing the loaded training data.
    """
    ref_data = pd.read_parquet(filename)
    logger = get_run_logger()

    numerical_features = ["trip_distance", "total_amount"]
    categorical_features = [
        "tpep_pickup_datetime",
        "PULocationID",
        "DOLocationID",
        "RatecodeID",
        "payment_type",
        "VendorID",
    ]

    def calculate_trip_duration(*, data: pd.DataFrame) -> np.ndarray:
        """This returns a DF containing the calculated trip_duration in minutes."""
        data = data.copy()
        # Convert to minutes
        MINS = 60
        try:
            trip_duration = data["tpep_dropoff_datetime"] - data["tpep_pickup_datetime"]
        except ValueError:
            trip_duration = data["lpep_dropoff_datetime"] - data["lpep_pickup_datetime"]
        trip_duration = round(trip_duration.dt.total_seconds() / MINS)
        return trip_duration

    logger.info("Calculating target and making predictions ...")
    ref_data["target"] = calculate_trip_duration(data=ref_data)
    # ref_data = ref_data[(ref_data["target"] >= 1) & (ref_data["target"] <= 60)]
    features = numerical_features + categorical_features
    ref_data = ref_data[features + ["target"]]
    ref_data["prediction"] = predict(data=ref_data)
    return ref_data


@task(retries=3, retry_delay_seconds=10)
def fetch_live_data():
    """This is used to fetch the live data from MongoDB."""
    db_name = "prediction_service"
    collection_name = "data"

    with MongoClient(MONGODB_ADDRESS) as client:
        data = client.get_database(db_name).get_collection(collection_name).find()
        df = pd.DataFrame(list(data))
        df = df.drop(columns=["id"])
        return df


@task(retries=3, retry_delay_seconds=10)
def run_evidently(ref_data: pd.DataFrame, curr_data: pd.DataFrame) -> tp.Tuple:
    """This is used to batch monitor the model. It calculates Data drift,
    data quality, and regression report using Evidently.

    params:
    -------
    ref_data (Pandas DF): DF containing the loaded training data.
    curr_data (Pandas DF): DF containing the production (live) data.

    Returns:
    --------
    result (Tuple): The data_drift_n_qty_report, regression_report, json_logs
    """
    # Ensure that size of reference data == current data
    data_size = curr_data.shape[0]
    ref_data = ref_data.iloc[:data_size]
    curr_data = curr_data.drop(columns=["_id"])

    logger = get_run_logger()

    column_mapping = ColumnMapping()
    numerical_features = ["trip_distance", "total_amount"]
    categorical_features = [
        "PULocationID",
        "DOLocationID",
        "RatecodeID",
        "payment_type",
        "VendorID",
    ]
    datetime_features = ["tpep_pickup_datetime"]
    column_mapping.target = "target"
    column_mapping.prediction = "prediction"

    column_mapping.numerical_features = numerical_features
    column_mapping.categorical_features = categorical_features
    column_mapping.datetime_features = datetime_features

    logger.info("Calculating metrics ...")
    data_drift_n_qty_report = Report(metrics=[DataDriftPreset(), DataQualityPreset()])
    data_drift_n_qty_report.run(
        reference_data=ref_data,
        current_data=curr_data,
        column_mapping=column_mapping,
    )
    regression_report = Report(metrics=[RegressionPreset()])
    regression_report.run(
        reference_data=ref_data,
        current_data=curr_data,
        column_mapping=column_mapping,
    )
    json_report = json.loads(data_drift_n_qty_report.json())
    return (data_drift_n_qty_report, regression_report, json_report)


@task(
    retries=3,
    retry_delay_seconds=10,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
def save_report_logs(*, json_report: tp.Dict) -> None:
    """This is used to save the metrics in MongoDB."""
    logger = get_run_logger()
    db_name = "prediction_service"
    collection_name = "report"
    with MongoClient(MONGODB_ADDRESS) as client:
        client.get_database(db_name).get_collection(collection_name).insert_one(json_report)
    logger.info("Reports saved!")


@task(retries=3, retry_delay_seconds=10)
def save_html_report(*, report: Report, type: str = "drift") -> None:
    """This is used to save the metrics report as HTML.

     params:
     -------
     report (Report): An Evidently report object.
     type (str): "drift" or "reg_report"

     Returns:
     --------
    None
    """
    logger = get_run_logger()
    name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if type == "drift":
        report.save_html(f"data_drift_n_qty_report_{name}.html")
    elif type == "reg_report":
        report.save_html(f"regression_report_{name}.html")
    logger.info("Report saved as HTML!")


@flow
def run_batch_analyses() -> None:
    """This is the workflow for running the batch model monitoring analyses."""
    logger = get_run_logger()

    logger.info("Updating records in MongoDB ...")
    upload_target_to_db(filename="target.csv")

    logger.info("Fetching reference data ...")
    ref_data = load_ref_data(filename="./evidently_service/datasets/reduced_data.parquet")
    logger.info("Fetching data from MongoDB ...")
    curr_data = fetch_live_data()

    logger.info("Running Evidently Service ...")
    data_drift_n_qty_report, regression_report, json_report = run_evidently(  # type: ignore
        ref_data=ref_data, curr_data=curr_data
    )

    logger.info("Saving reports to MongoDB ...")
    save_report_logs(json_report=json_report)  # type: ignore

    logger.info("Saving reports as HTML ...")
    save_html_report(report=data_drift_n_qty_report, type="drift")  # type: ignore
    save_html_report(report=regression_report, type="reg_report")  # type: ignore


if __name__ == "__main__":
    run_batch_analyses()
