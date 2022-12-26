import typing as tp

import numpy as np
import pandas as pd

# Custom Imports
from src.config.core import config
from src.processing.data_manager import (load_model, load_version, logger,
                                         validate_training_input)


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
    _version = load_version()
    _model = load_model(filename=config.path_config.MODEL_PATH)

    # Validate data
    validated_data, errors = validate_training_input(data=data)

    result = {
        "trip_duration": None,
        "model_version": _version,
        "errors": errors,
    }

    if not errors:
        logger.info("Making Predictions ...")
        # Make predictions
        pred = _model.predict(validated_data)
        pred = list(np.exp(pred))  # Convert from log to minutes

        result = {
            "trip_duration": [round(x, 1) for x in pred],  # type: ignore
            "model_version": _version,
            "errors": errors,
        }

    return result
