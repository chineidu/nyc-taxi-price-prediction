import numpy as np
import pandas as pd

# Custom imports
from src.predict import make_predictions


def test_make_predictions(test_data: pd.DataFrame):
    """This tests the the predictions."""
    # Given
    expected_output = [20.0, 25.9, 39.5, 31.2, 36.0, 12.6, 26.8, 6.8, 22.8, 13.5]
    data = test_data.iloc[:10]
    print(data)

    # When
    pred = make_predictions(data=data)  # Make predictions

    # Then
    # assert np.isclose(expected_output, pred, rtol=0.04).all()
