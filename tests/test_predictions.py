"""
This module is used to test predictions.

author: Chinedu Ezeofor
"""

import typing as tp

import numpy as np
import pandas as pd

# Custom imports
# from src.predict import make_predictions
from src import make_predictions


def test_make_predictions(test_data: pd.DataFrame):
    """This tests the the predictions."""
    # Given
    expected_output = [17.3, 22.2, 32.7, 22.2, 28.8, 12.3, 22.2, 4.9, 22.2, 10.6]

    # When
    pred = make_predictions(data=test_data.iloc[:10])  # Make predictions
    print(pred)
    results = pred.get("trip_duration")

    # Then
    assert np.isclose(expected_output, results, rtol=0.04).all()
    assert pred.get("errors") is None
