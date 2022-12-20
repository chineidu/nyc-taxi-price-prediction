from pathlib import Path

from prefect import task, flow
from prefect.task_runners import ConcurrentTaskRunner
from prefect.tasks import task_input_hash



# Custom Imports
from src.train import train_model
from src.pipeline import rf_pipe
from processing.data_manager import load_data, save_model
from src.utilities.experiment import eval_metrics
from src.config.schema import ValidateSklearnPipe
from src.config.core import config


from datetime import timedelta

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


@flow(task_runner=ConcurrentTaskRunner)
def run_flow(*, filename: Path, pipe_obj: ValidateSklearnPipe):
    """This is the pipeline for running the workflow.

    Params:
    -------
    filename (Path): Input data filepath.
    pipe_obj (ValidateSklearnPipe): A pipeline (estimator) object created by validating an
        Sklearn pipeline using Pydantic.

    Returns:
    --------
    None
    """
    train_data = load_data(filename=filename)
    pipe, y_validate, y_pred = train_model(train_data=train_data, pipe=pipe_obj.pipe)
    save_model(filename=config.src_config.MODEL_PATH, pipe=pipe)
    _ = eval_metrics(actual=y_validate, pred=y_pred)


# Created because Prefect needs to validate the Pipeline.
pipe_obj = ValidateSklearnPipe(pipe=rf_pipe)
run_flow(filename=config.src_config.TRAIN_DATA, pipe_obj=pipe_obj)
