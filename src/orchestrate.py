from pathlib import Path
import typing as tp
from datetime import timedelta

from prefect import task, flow, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from prefect.tasks import task_input_hash
from prefect.filesystems import LocalFileSystem
from prefect.infrastructure.process import Process


# Custom Imports
from src.train import train_model
from processing.data_manager import load_data, save_model
from src.utilities.experiment import eval_metrics
from src.config.core import config


# Create task(s). Use this syntax since the functions were imported.
load_data = task(load_data, retries=3, retry_delay_seconds=3)
train_model = task(
    train_model,
    retries=3,
    retry_delay_seconds=3,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
eval_metrics = task(eval_metrics, retries=3, retry_delay_seconds=3)
save_model = task(save_model, retries=3, retry_delay_seconds=3)

local_file_system_block = LocalFileSystem.load("demo-storage-block")
process_block = Process.load("process-infra")

@flow(task_runner=ConcurrentTaskRunner)
def train_ML_model_flow(*, filename: Path,) -> tp.Tuple:
    """This is the subflow for training the model.

    Params:
    -------
    filename (Path): Input data filepath.

    Returns:
    --------
    pipe, y_validate, y_pred (Tuple): Tuple containing the pipeline (estimator),
        validation y_values and the predicted values (obtaiined from the estimator)
    """
    train_data = load_data(filename=filename)
    pipe, y_validate, y_pred = train_model(train_data=train_data)
    return pipe, y_validate, y_pred


@flow(task_runner=ConcurrentTaskRunner)
def run_flow(*, filename: Path):
    """This is the pipeline for running the workflow.

    Params:
    -------
    filename (Path): Input data filepath.

    Returns:
    --------
    None
    """
    logger = get_run_logger()
    logger.info("====== Training model ======")
    pipe, y_validate, y_pred = train_ML_model_flow(filename=filename)
    save_model(filename=config.src_config.MODEL_PATH, pipe=pipe)
    rmse, mse, mae, r2 = eval_metrics(actual=y_validate, pred=y_pred)
    # Log Metrics
    logger.info(f"  RMSE: {rmse}")
    logger.info(f"  MSE: {mse}")
    logger.info(f"  MAE: {mae}")
    logger.info(f"  R2: {r2}")



if __name__ == '__main__':
    local_file_system_block = LocalFileSystem.load("demo-storage-block")
    process_block = Process.load("process-infra")
    run_flow(filename=config.src_config.TRAIN_DATA)
