import pandas as pd
import numpy as np

# Custom Imports
from src.processing.data_manager import load_model, validate_training_input
from src.config.core import config

import typing as tp


def make_predictions(*, data: pd.DataFrame) -> tp.Dict:
    """This returns the predictions."""
    model = load_model(model_fp=config.path_config.MODEL_PATH)
    _version = "_version"
    validated_data, error = validate_training_input(data=data)
    result = {
        "trip_duration": None,
        "model_version": _version,
        "errors": error,
    }

    if not error:
        print("====== Making Predictions ======")
        # Make predictions
        pred = model.predict(validated_data)
        pred = list(np.exp(pred))  # Convert from log to minutes
        result = [round(x, 1) for x in pred]

        result = {
            "trip_duration": result,
            "model_version": _version,
            "errors": error,
        }

    return result


if __name__ == "__main__":
    from src.processing.data_manager import load_data
    from src.config.core import config

    data = load_data(filename=config.path_config.TEST_DATA).iloc[:5]
    pred = make_predictions(data=data)
    print(pred)
