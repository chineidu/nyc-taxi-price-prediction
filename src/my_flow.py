import warnings
import logging

# from Scikit-learn
from sklearn.model_selection import train_test_split

from prefect import task, flow

# Custom Imports
from processing.data_manager import load_data, save_model
from src.config.core import config
from src.pipeline import rf_pipe
from src.utilities.experiment import eval_metrics

warnings.filterwarnings("error")


@task(retries=3, retry_delay_seconds=3)
def train_model() -> None:
    """This is used to train the model.

    Params:
    -------
    data (Pandas DF): DF containing the training data.

    Returns:
    --------
    data (Pandas DF): The validated DF.
    error (str or None): None if there's no error else a str.
    """

    def _set_up_logger(delim: str = "::") -> None:
        """This is used to create a basic logger."""
        format_ = f"%(levelname)s {delim} %(asctime)s {delim} %(message)s"
        logging.basicConfig(level=logging.INFO, format=format_)
        logger = logging.getLogger(__name__)
        return logger

    logger = _set_up_logger()
    # Load Data
    train_data = load_data(filename=config.src_config.TRAIN_DATA)

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
    rf_pipe.fit(X_train, y_train)

    # Predictions using train data
    logger.info("========== Making Predictions ==========")
    y_pred_train = rf_pipe.predict(X_train)
    # Predictions using validation data
    y_pred = rf_pipe.predict(X_validate)

    # Persist Model
    save_model(filename=config.src_config.MODEL_PATH, pipe=rf_pipe)

    logger.info("========== Evaluating Performance ==========")
    rmse, mse, mae, r2 = eval_metrics(actual=y_validate, pred=y_pred)

    logger.info(f"  RMSE: {rmse}")
    logger.info(f"  MSE: {mse}")
    logger.info(f"  MAE: {mae}")
    logger.info(f"  R2: {r2}")


@flow
def run_flow():
    train_model()


run_flow()
