"""
This module contains helper functions used to perform batch 
prediction on  the data.

author: Chinedu Ezeofor
"""

# Standard imports
import numpy as np
import pandas as pd

# Built-in library
import typing as tp
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Custom Imports
from src.processing.data_manager import logger


def get_predictions(*, data: pd.DataFrame, run_id: str) -> np.ndarray:
    """This returns the predicted trip duration using the model
    from the model registry on S3.

    Params:
    -------
    run_id (str): The run id associated with the model.
    run_id (str): The run id associated with the model.

    Returns:
    --------
    pred (ndarray): The predicted trip duration.
    """
    import mlflow

    S3_BUCKET_NAME = f"s3://mlflow-model-registry-neidu/1/{run_id}/artifacts/model"
    # Load the model from the model registry
    logger.info("Fetching model from registry ...")
    try:
        model = mlflow.pyfunc.load_model(model_uri=f"{S3_BUCKET_NAME}")
    except Exception as err:
        logger.info(err)
    logger.info("Making predictions ...")
    pred = model.predict(data)
    pred = [(round(x, 1)) for x in list(np.exp(pred))]  # Convert from log to minutes
    return np.array(pred)


def get_paths(*, run_date: str, taxi_type: str, run_id: str) -> tp.Tuple:
    """This returns the input and output S3 bucket URIs for the data.

    Params:
    -------
    run_date (str): The date the script was run in  `year-month-day format`. e.g "2022-12-30"
    taxi_type (str): The taxi colour. e.g yellow, green, etc
    run_id (str): The run id associated with the model.

    Returns:
    --------
    input_file, output_file (S3 URIs): The input and output S3 URIs respectively.
    """
    date_obj = datetime.strptime(run_date, "%Y-%m-%d")
    prev_month = date_obj - relativedelta(months=1)
    year = prev_month.year
    month = prev_month.month

    input_file = (
        f"s3://nyc-tlc/trip data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet"
    )
    output_file = f"s3://nyc-duration-prediction-neidu/taxi_type={taxi_type}/year={year:04d}/month={month:02d}/{run_id}.parquet"

    return input_file, output_file


def compare_predictions(*, data: pd.DataFrame, run_id: str) -> pd.DataFrame:
    """This compares the actual vs predicted trip duration.

    Params:
    -------
    data (Pandas DF): DF containing the NYC taxi data.
    run_id (str): The run id associated with the model.

    Returns:
    --------
    result_df (Pandas DF): DF containing the predicted trip duration and other info.
    """
    result_df = pd.DataFrame()
    try:
        pred_trip_duration = get_predictions(data=data, run_id=run_id)
    except Exception as err:
        logger.info(err)

    result_df["id"] = data["id"]
    result_df["tpep_pickup_datetime"] = data["tpep_pickup_datetime"]
    result_df["trip_distance"] = data["trip_distance"]
    result_df["PULocationID"] = data["PULocationID"]
    result_df["DOLocationID"] = data["DOLocationID"]
    result_df["actual_trip_duration"] = data["trip_duration"].apply(
        np.exp
    )  # Convert to minutes
    result_df["pred_trip_duration"] = pred_trip_duration
    result_df["diff"] = (
        result_df["actual_trip_duration"] - result_df["pred_trip_duration"]
    )
    result_df["model_run_id"] = run_id
    return result_df


def save_data_to_s3(data: pd.DataFrame, output: str) -> None:
    """This saves the parquet data to S3"""
    try:
        logger.info("Saving to S3 ...")
        data.to_parquet(path=output, index=False)
    except Exception as err:
        logger.info(err)
