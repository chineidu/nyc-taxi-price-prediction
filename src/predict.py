import typing as tp

import numpy as np
import pandas as pd

# Custom Imports
from src.config.core import config
from src.processing.data_manager import load_data, load_model, validate_training_input


def make_predictions(*, data: pd.DataFrame) -> tp.Dict:
    """This returns the predictions.

    Params:
    -------
    data (Pandas DF): DF containing the input data.

    Returns:
    --------
    result (Dict): A dict containing the trip_duration,
            model_version and the possible errors.
    """
    data = data.copy()
    model = load_model(filename=config.path_config.MODEL_PATH)
    _version = "_version"

    # Validate data
    validated_data, errors = validate_training_input(data=data)

    result = {
        "trip_duration": None,
        "model_version": _version,
        "errors": errors,
    }

    if not errors:
        print("==========  Making Predictions ========== ")
        # Make predictions
        pred = model.predict(validated_data)
        pred = list(np.exp(pred))  # Convert from log to minutes

        result = {
            "trip_duration": [round(x, 1) for x in pred],  # type: ignore
            "model_version": _version,
            "errors": errors,
        }

    return result


if __name__ == "__main__":
    data = load_data(filename=config.path_config.TEST_DATA).iloc[:5]
    pred = make_predictions(data=data)
    print(pred)
