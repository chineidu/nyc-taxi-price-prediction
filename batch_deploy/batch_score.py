"""
This module is used to perform batch prediction on the data.

author: Chinedu Ezeofor
"""
import typing as tp
from argparse import ArgumentParser
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from prefect import task, flow, get_run_logger
from prefect.tasks import task_input_hash
from prefect.task_runners import ConcurrentTaskRunner
from prefect.context import get_run_context

# Custom Imports
from src.processing.data_manager import load_data
from batch_deploy.utilities import compare_predictions, save_data_to_s3

# Create tasks
load_data = task(
    load_data,
    retries=3,
    retry_delay_seconds=5,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
compare_predictions = task(
    compare_predictions,
    retries=3,
    retry_delay_seconds=5,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
save_data_to_s3 = task(save_data_to_s3, retries=3, retry_delay_seconds=5)


@task(retries=3, retry_delay_seconds=5)
def get_paths(*, taxi_type: str, run_id: str, run_date: datetime) -> tp.Tuple:
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
    prev_month = run_date - relativedelta(months=1)
    year = prev_month.year
    month = prev_month.month

    input_file = (
        f"s3://nyc-tlc/trip data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet"
    )
    output_file = f"s3://nyc-duration-prediction-neidu/taxi_type={taxi_type}/year={year:04d}/month={month:02d}/{run_id}.parquet"

    return input_file, output_file


@flow(task_runner=ConcurrentTaskRunner)  # type: ignore
def main():
    """This is the main function"""
    logger = get_run_logger()
    logger.info("Starting batch predictions ...")

    parser = ArgumentParser(
        prog="Batch predictions",
        description="This is used to make batch predictions of the NYC taxi trip duration.",
    )
    parser.add_argument(
        "--run-id",
        "-r",
        help="The run id associated with the model e.g `98f43706f6184694be1ee10c41c7b69d`",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--run-date",
        "-d",
        help="The date the script was run in `year-month-day format`. e.g `2022-03-30`",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--taxi-type",
        "-t",
        help="The taxi colour. e.g `yellow`, `green`, etc",
        type=str,
        required=True,
    )
    args = parser.parse_args()
    # Extract the variables
    run_id, run_date, taxi_type = (args.run_id, args.run_date.lower(), args.taxi_type)

    if run_date == "none":
        ctx = get_run_context()
        run_date = ctx.flow_run.expected_start_time
    else:
        date = run_date.split("-")
        year, month, day = (int(date[0]), int(date[1]), int(date[2]))
        run_date = datetime(year=year, month=month, day=day)

    logger.info("Getting input and output filepaths ...")
    input_file, output_file = get_paths(
        run_date=run_date, taxi_type=taxi_type, run_id=run_id
    )
    logger.info("Loading data using input filepath ...")
    data = load_data(filename=input_file, uri=True)
    logger.info("Making predictions on input data ...")
    result_df = compare_predictions(data=data, run_id=run_id)
    logger.info("Saving data to S3 ...")
    save_data_to_s3(data=result_df, output=output_file)
    logger.info("Batch Prediction processing done!")
    logger.info(input_file)


if __name__ == "__main__":
    # Run the program
    main()
