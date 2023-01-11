"""
This module is used to deploy the batch prediction of the data
using Prefect. Note: you can specify how often the flow should run.

author: Chinedu Ezeofor
"""

from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

# from deployment.batch_deploy.batch_score import batch_predict_flow, batch_predict_backfill_flow
from model_deployment import batch_predict_backfill_flow

deployment = Deployment.build_from_flow(
    # flow=batch_predict_flow,
    flow=batch_predict_backfill_flow,
    name="batch-prediction-deployment",
    parameters={
        "taxi_type": "yellow",
        "run_id": "98f43706f6184694be1ee10c41c7b69d",
    },
    version=1,
    schedule=CronSchedule(cron="34 21 31 * *"),
    work_queue_name="batch_predict",
    tags=["regression", "batch_prediction"],
)

if __name__ == "__main__":  # pragma: no cover
    deployment.apply()  # type: ignore
    print("Deployed!!!")
