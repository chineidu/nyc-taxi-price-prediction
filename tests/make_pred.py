"""
This module is used to test predictions.

author: Chinedu Ezeofor
"""

import typing as tp

import numpy as np
import pandas as pd

# Custom imports
from src.predict import make_predictions
from src.processing.data_manager import load_data
from src.config.core import config


data = load_data(filename=config.path_config.TEST_DATA).iloc[:10]

def test_make_predictions(test_data: pd.DataFrame):
    """This tests the the predictions."""
    # Given
    expected_output = [17.3, 22.2, 32.7, 22.2, 28.8, 12.3, 22.2, 4.9, 22.2, 10.6]
    print(test_data.head())

    # When
    print("Here")
    pred = make_predictions(data=test_data.iloc[:10])  # Make predictions
    results = pred.get("trip_duration")
    print(pred)

test_make_predictions(test_data=data)
