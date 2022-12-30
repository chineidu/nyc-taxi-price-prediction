"""
This module is used to perform batch prediction on the data.

author: Chinedu Ezeofor
"""
from argparse import ArgumentParser
from datetime import timedelta

from prefect import task, flow, get_run_logger
from prefect.tasks import task_input_hash
from prefect.task_runners import ConcurrentTaskRunner

# Custom Imports
from src.processing.data_manager import load_data
from batch_deploy.utilities import get_paths, compare_predictions, save_data_to_s3

# Create tasks
load_data = task(
    load_data,
    retries=3,
    retry_delay_seconds=10,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
get_paths = task(get_paths, retries=3, retry_delay_seconds=10)
compare_predictions = task(
    compare_predictions,
    retries=3,
    retry_delay_seconds=10,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
save_data_to_s3 = task(save_data_to_s3, retries=3, retry_delay_seconds=10)


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
    run_id, run_date, taxi_type = (args.run_id, args.run_date, args.taxi_type)

    input_file, output_file = get_paths(
        run_date=run_date, taxi_type=taxi_type, run_id=run_id
    )
    data = load_data(filename=input_file, uri=True)
    result_df = compare_predictions(data=data, run_id=run_id)
    save_data_to_s3(data=result_df, output=output_file)
    logger.info("Batch Prediction processing done!")


if __name__ == "__main__":
    # Run the program
    main()
