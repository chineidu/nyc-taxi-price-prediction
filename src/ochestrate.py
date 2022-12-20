from pathlib import Path

from prefect import task, flow
from prefect.task_runners import ConcurrentTaskRunner

# Custom Imports
from src.train import train_model
from processing.data_manager import load_data
from src.config.core import config

# Create task(s). Use this syntax since the functions were imported.
train_model = task(train_model, retries=3, retry_delay_seconds=3)
load_data = task(load_data)

@flow(task_runner=ConcurrentTaskRunner)
def run_flow(*, filename: Path):
    """Docs"""
    train_data = load_data(filename=filename)
    train_model(train_data=train_data)


run_flow(filename=config.src_config.TRAIN_DATA)
