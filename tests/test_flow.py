"""
This module is used to test the workflow and deployments.

author: Chinedu Ezeofor
"""
# Custom Imports
from src.orchestrate import run_flow
from src.deployments import deployment
from src.config.core import config


def test_flow_run() -> None:
    """This is used to test the run_flow workflow"""
    # Given
    expected_output = "success"

    # When
    result = run_flow(
        filename=config.path_config.TEST_DATA,
        save_estimator=False,
    )

    # Then
    assert expected_output == result.get("status")


def test_deployment() -> None:
    """This is used to test the prefect deployment"""
    # Given
    work_queue_name = deployment.work_queue_name
    name = deployment.name
    filename = deployment.parameters.get("filename")

    # When

    # Then
    assert str(work_queue_name) == "ml"
    assert str(name) == "model_training"
    assert str(filename) == "yellow_tripdata_2022-01.parquet"
