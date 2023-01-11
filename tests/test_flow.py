"""
This module is used to test the workflow and deployments.

author: Chinedu Ezeofor
"""
from src.config.core import config

# Custom Imports
from src.orchestrate import run_flow


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
