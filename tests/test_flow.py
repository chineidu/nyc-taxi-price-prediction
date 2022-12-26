# Custom Imports
from src.orchestrate import run_flow
from src.train import train_model
from src.config.core import config


import pandas as pd


def test_flow_run():
    """This is used to test the run_flow workflow"""
    # Given
    expected_output = "success"

    # When
    result = run_flow(filename=config.path_config.TEST_DATA, save_estimator=False)
    print(result)

    # Then
    assert expected_output == result.get("status")
