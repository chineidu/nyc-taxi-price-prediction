import warnings
import logging
import typing as tp

import pandas as pd

# from Scikit-learn
from sklearn.model_selection import train_test_split


# Custom Imports
from processing.data_manager import load_data, save_model
from src.config.core import config
from src.pipeline import rf_pipe
from src.config.schema import ValidateSklearnPipe
from src.utilities.experiment import eval_metrics

warnings.filterwarnings("error")

# def train_model(*, train_data: pd.DataFrame, pipe_obj: ValidateSklearnPipe) -> tp.Tuple:
def train_model(*, train_data: pd.DataFrame) -> tp.Tuple:
    """This is used to train the model.

    Params:
    -------
    train_data (Pandas DF): DF containing the training data.

    Returns:
    --------
    None
    """

    def _set_up_logger(delim: str = "::") -> tp.Tuple:
        """This is used to create a basic logger."""
        format_ = f"%(levelname)s {delim} %(asctime)s {delim} %(message)s"
        logging.basicConfig(level=logging.INFO, format=format_)
        logger = logging.getLogger(__name__)
        return logger

    logger = _set_up_logger()

    pipe = rf_pipe
    # Split the data
    X = train_data.drop(columns=[config.model_config.TARGET])
    y = train_data[config.model_config.TARGET]

    X_train, X_validate, y_train, y_validate = train_test_split(
        X,
        y,
        test_size=config.model_config.TEST_SIZE,
        random_state=config.model_config.RANDOM_STATE,
    )

    # Train Model
    logger.info("========== Training model ==========")
    pipe.fit(X_train, y_train)

    # Predictions using train data
    logger.info("========== Making Predictions ==========")
    _ = pipe.predict(X_train)

    # Predictions using validation data
    y_pred = rf_pipe.predict(X_validate)
    return pipe, y_validate, y_pred


if __name__ == "__main__":
    # Load Data
    train_data = load_data(filename=config.src_config.TRAIN_DATA)

    # Train model
    pipe, y_validate, y_pred = train_model(train_data=train_data)

    # Save model
    save_model(filename=config.src_config.MODEL_PATH, pipe=rf_pipe)

    # Evaluate model performance
    rmse, mse, mae, r2 = eval_metrics(actual=y_validate, pred=y_pred)
