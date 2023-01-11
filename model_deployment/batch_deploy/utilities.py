"""
This module contains helper functions used to perform batch 
prediction on  the data.

author: Chinedu Ezeofor
"""

# Standard imports
import numpy as np
import mlflow
import pandas as pd

# Custom Imports
from src.processing.data_manager import logger, load_data


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
    S3_BUCKET_NAME = f"s3://mlflow-model-registry-neidu/1/{run_id}/artifacts/model"
    # Load the model from the model registry
    logger.info("Fetching model from registry ...")
    try:
        model = mlflow.pyfunc.load_model(model_uri=f"{S3_BUCKET_NAME}")
    except Exception as err:
        logger.info(err)
    logger.info("Making predictions ...")
    pred = model.predict(data)
    pred = [(round(x, 1)) for x in list(np.expm1(pred))]  # Convert from log to minutes
    return np.array(pred)


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
