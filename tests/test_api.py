"""
This module is used to test the API predictios.

author: Chinedu Ezeofor
"""

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from src.api.config import settings
from src.config.core import config


def test_api_home(client: TestClient) -> None:
    """This tests the API's home endpoint."""
    # Given
    expected_output = {"message": f"Welcome to the {settings.PROJECT_NAME!r}"}

    # When
    response = client.get("http://localhost:8001/")

    # Then
    assert response.status_code == 200
    assert response.json() == expected_output


def test_make_api_prediction(client: TestClient, test_data: pd.DataFrame) -> None:
    # Given
    test_data = test_data.iloc[:5].copy()
    expected_output = [17.3, 22.2, 32.7, 22.2, 28.8]

    # When
    # === Preprocess data ===
    test_data = test_data[config.model_config.INPUT_FEATURES]
    pickup_time = config.model_config.TEMPORAL_VAR
    test_data[pickup_time] = test_data[pickup_time].astype(str)
    payload = {
        # Replace NaNs with None
        "inputs": test_data.replace({np.nan: None}).to_dict(orient="records")
    }
    response = client.post(
        "http://localhost:8001/api/v1/predict",
        json=payload,
    )
    prediction_data = response.json()

    # Then
    assert response.status_code == 200
    assert prediction_data["trip_duration"]
    assert prediction_data["errors"] is None
    assert np.isclose(expected_output, prediction_data["trip_duration"], rtol=0.03).all()
