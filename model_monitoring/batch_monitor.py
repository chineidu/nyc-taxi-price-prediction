import os
import json
import typing as tp
import joblib

import pandas as pd
from pymongo import MongoClient
from prefect import task, flow, get_run_logger
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset,
    DataQualityPreset,
    RegressionPreset,
)

MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27018")
logger = get_run_logger()


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
                filter = row[0]
                updated_val = {"$set": {"target": round(row[1])}}
                collection.update_one(filter=filter, update=updated_val)


def predict(*, data: pd.DataFrame) -> float:
    """This is used to make predictions on unseen data using
    the trained model."""
    MODEL_FILE = os.getenv("MODEL_FILE", "model.pkl")
    with open(MODEL_FILE, "rb") as file:
        model = joblib.load(file)

    pred = model.predict(data)
    pred = [(round(x)) for x in list(np.expm1(pred))]  # Convert from log to minutes
    return pred


@task(retries=3, retry_delay_seconds=10)
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

    def calculate_trip_duration(*, data: pd.DataFrame) -> np.ndarray:
        """This returns a DF containing the calculated trip_duration in minutes."""
        data = data.copy()
        # Convert to minutes
        MINS = 60
        try:
            trip_duration = data["tpep_dropoff_datetime"] - data["tpep_pickup_datetime"]
        except:
            trip_duration = data["lpep_dropoff_datetime"] - data["lpep_pickup_datetime"]
        trip_duration = round(trip_duration.dt.total_seconds() / MINS)
        return trip_duration

    logger.info("Calculating target and makin predictions ...")
    ref_data["target"] = calculate_trip_duration(data=ref_data)
    ref_data["predictions"] = predict(data=ref_data)

    return ref_data


@flow(retries=3, retry_delay_seconds=10)
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
    ref_data = ref_data.sample(n=data_size, random_state=123)

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


@task(retries=3, retry_delay_seconds=10)
def fetch_data():
    """This is used to fetch the live data from MongoDB."""
    db_name = "prediction_service"
    collection_name = "data"

    with MongoClient(MONGODB_ADDRESS) as client:
        data = client.get_database(db_name).get_collection(collection_name).find()
        df = pd.DataFrame(list(data))
        return df


@task(retries=3, retry_delay_seconds=10)
def save_report_logs(*, json_report: tp.Dict):
    """This is used to save the metrics in MongoDB."""
    db_name = "prediction_service"
    collection_name = "report"
    with MongoClient(MONGODB_ADDRESS) as client:
        client.get_database(db_name).get_collection(collection_name).insert_one(
            json_report
        )
    logger.info("Reports saved!")


@task(retries=3, retry_delay_seconds=10)
def save_html_report(*, report: tp.Any, name: str):
    """This is used to save the metrics report as HTML."""
    report.save(f"{name}.html")
    logger.info("Report saved as HTML!")


@flow
def run_batch_analyses():
    """This is the workflow for running the batch model monitoring analyses."""
    upload_target_to_db("target.csv")
    print("Fetching reference data ...")

    ref_data = load_ref_data(
        "./evidently_service/datasets/yellow_tripdata_2022-01.parquet"
    )
    print("Fetching data from MongoDB ...")
    data = fetch_data()

    print("Running Evidently Service ...")
    data_drift_n_qty_report, regression_report, json_report = run_evidently(
        ref_data, data
    )

    print("Saving reports to MongoDB ...")
    save_report_logs(json_report=json_report)

    print("Saving reports as HTML ...")
    save_html_report(data_drift_n_qty_report)
    save_html_report(regression_report)


if __name__ == '__main__':
    run_batch_analyses()