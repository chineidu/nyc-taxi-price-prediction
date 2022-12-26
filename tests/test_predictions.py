"""
This module is used to test predictions.

author: Chinedu Ezeofor
"""
import numpy as np
import pandas as pd
import pytest

# Custom imports
from src import make_predictions
from src.utilities.experiment import eval_metrics


def test_make_predictions(test_data: pd.DataFrame):
    """This tests the predictions."""
    # Given
    expected_output = [17.3, 22.2, 32.7, 22.2, 28.8, 12.3, 22.2, 4.9, 22.2, 10.6]

    # When
    pred = make_predictions(data=test_data.iloc[:10])  # Make predictions
    print(pred)
    results = pred.get("trip_duration")

    # Then
    assert np.isclose(expected_output, results, rtol=0.04).all()
    assert pred.get("errors") is None


def test_evaluate_metrics():
    """This tests the function for calculating
    the evaluation metrics."""
    # Given
    actual, pred = np.array([20.0, 25.9, 39.5, 31.2]), np.array(
        [20.5, 22.2, 38.2, 31.9]
    )
    expected_output = (2.0074859899884725, 4.029999999999997, 1.549999999999999)

    # When
    rmse, mse, mae, _ = eval_metrics(actual, pred)

    # Then
    assert expected_output == (rmse, mse, mae)
