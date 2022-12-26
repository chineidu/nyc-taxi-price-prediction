import typing as tp
from datetime import timedelta
from pathlib import Path

from prefect import flow, get_run_logger, task
from prefect.task_runners import ConcurrentTaskRunner
from prefect.tasks import task_input_hash

from src.config.core import config
# Custom Imports
from src.processing.data_manager import load_data, save_model
from src.train import train_model
from src.utilities.experiment import eval_metrics

# Create task(s). Use this syntax since the functions were imported.
load_data = task(load_data, retries=3, retry_delay_seconds=3)  # type: ignore
train_model = task(
    train_model,
    retries=3,
    retry_delay_seconds=3,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)  # type: ignore
eval_metrics = task(eval_metrics, retries=3, retry_delay_seconds=3)  # type: ignore
save_model = task(save_model, retries=3, retry_delay_seconds=3)  # type: ignore


@flow(task_runner=ConcurrentTaskRunner)  # type: ignore
def train_ML_model_flow(
    *,
    filename: Path,
) -> tp.Tuple:  # pragma: no cover
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


@flow(task_runner=ConcurrentTaskRunner)  # type: ignore
def run_flow(
    *, filename: Path, save_estimator: bool = True
) -> tp.Dict:  # pragma: no cover
    """This is the pipeline for running the workflow.

    Params:
    -------
    filename (Path): Input data filepath.
    save_estimator (bool) default=True: If true, it saves the model.

    Returns:
    --------
    None
    """
    logger = get_run_logger()
    logger.info("Training model ...")
    pipe, y_validate, y_pred = train_ML_model_flow(filename=filename)

    if save_estimator:
        save_model(filename=config.path_config.MODEL_PATH, pipe=pipe)
    rmse, mse, mae, r2 = eval_metrics(actual=y_validate, pred=y_pred)
    # Log Metrics
    logger.info(f"  RMSE: {rmse}")
    logger.info(f"  MSE: {mse}")
    logger.info(f"  MAE: {mae}")
    logger.info(f"  R2: {r2}")

    return {"status": "success"}


if __name__ == "__main__":  # pragma: no cover
    run_flow(filename=config.path_config.TRAIN_DATA)
