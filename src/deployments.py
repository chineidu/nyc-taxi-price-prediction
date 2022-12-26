from datetime import timedelta

from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import IntervalSchedule

from src.config.core import config
# Custom Imports
from src.orchestrate import run_flow

deployment = Deployment.build_from_flow(
    flow=run_flow,
    name="model_training",
    schedule=IntervalSchedule(interval=timedelta(seconds=60)),
    parameters={"filename": config.path_config.TRAIN_DATA},
    tags=["demo", "Neidu"],
    work_queue_name="ml",
)


if __name__ == "__main__":  # pragma: no cover
    deployment.apply()  # type: ignore
    print("Deployed!!!")
