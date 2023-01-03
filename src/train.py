"""
This module is used to train the model.

author: Chinedu Ezeofor
"""
import typing as tp
import warnings

import pandas as pd

# Custom Imports
from src.config.core import config
from src.pipeline import rf_pipe
from src.processing.data_manager import load_data, logger, save_model, split_train_data
from src.utilities.experiment import eval_metrics

warnings.filterwarnings("error")


def train_model(*, train_data: pd.DataFrame) -> tp.Tuple:
    """This is used to train the model.

    Params:
    -------
    train_data (Pandas DF): DF containing the training data.

    Returns:
    --------
    pipe, y_validate, y_pred (Tuple): Tuple containing the
        trained_model_pipe, actual y and predicted y values.
    """

    pipe = rf_pipe
    target = target = config.model_config.TARGET
    test_size = config.model_config.TEST_SIZE
    random_state = config.model_config.RANDOM_STATE

    # Split the data
    X_train, X_validate, y_train, y_validate = split_train_data(
        data=train_data,
        target=target,
        test_size=test_size,
        random_state=random_state,
    )

    # Train Model
    logger.info("Training model ...")
    pipe.fit(X_train, y_train)

    # Predictions using validation data
    logger.info("Making Predictions ...")
    y_pred = rf_pipe.predict(X_validate)
    return pipe, y_validate, y_pred


if __name__ == "__main__":  # pragma: no cover
    # Load Data
    train_data = load_data(filename=config.path_config.TRAIN_DATA)

    # Train model
    pipe, y_validate, y_pred = train_model(train_data=train_data)

    # Save model
    save_model(filename=config.path_config.MODEL_PATH, pipe=rf_pipe)

    # Evaluate model performance
    rmse, mse, mae, r2 = eval_metrics(actual=y_validate, pred=y_pred)
