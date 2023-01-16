"""
This module is used to load/save the data.

author: Chinedu Ezeofor
"""
import uuid
import typing as tp
from pathlib import Path

# Standard imports
import numpy as np
import joblib
import pandas as pd
from pydantic import ValidationError
from sklearn.pipeline import Pipeline

# Scikit-learn
from sklearn.model_selection import train_test_split

# Custom Imports
from src.config.core import SRC_ROOT, DATA_FILEPATH, TRAINED_MODELS_FILEPATH, config
from src.config.schema import ValidateInputSchema, ValidateTrainingData


def custom_logger():
    """This is used to create a custom logger that saves the output
    to the path: logs/

    Sample messages:
    ----------------
        logger.debug("Used for debugging your code.")
        logger.info("Informative messages from your code.")
        logger.warning("Everything works but there is something to be aware of.")
        logger.error("There's been a mistake with the process.")
        logger.critical("There is something terribly wrong and process may terminate.")

    """
    import logging

    from rich.logging import RichHandler

    BASE_DIR = Path(__name__).absolute().parent
    LOGS_DIR = Path(BASE_DIR, "logs")
    # Create directory
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Use config file to initialize logger
    CONFIG_DIR = BASE_DIR
    logging.config.fileConfig(Path(CONFIG_DIR, "logging.config"))
    logger = logging.getLogger()
    logger.handlers[0] = RichHandler(markup=True)  # set rich handler
    return logger


# logger = _set_up_logger()
logger = custom_logger()
Estimator = tp.Union[Pipeline, tp.Any]  # Alias for estimator


def get_unique_IDs(feat: str) -> str:
    """This returns a universally unique generated ID."""
    if feat is not None:
        return str(uuid.uuid4())


def load_data(*, filename: tp.Union[str, Path], uri: bool = False) -> pd.DataFrame:
    """This returns the data as a Pandas DF.

    Params:
    -------
    filename (Path): The relative input filepath.
    uri (bool, default=False): True if the filename is an S3 URI else False

    Returns:
    --------
    data (Pandas DF): The loaded DF.
    """
    if not uri:
        filename = f"{DATA_FILEPATH}/{filename}"
    filename = str(filename)

    logger.info("Loading Data ... ")
    try:
        data = (
            pd.read_csv(filename)
            if filename.endswith("csv")
            else pd.read_parquet(filename)
        )
    except FileNotFoundError as err:
        logger.info(err)

    TRIP_DUR_THRESH = 60  # trip_duration
    TRIP_DIST_THRESH = 30  # trip_distance
    TOTAL_AMT_THRESH = 100  # total_amount
    MIN_THRESH = 0

    if filename.endswith("parquet"):

        def calculate_trip_duration(data: pd.DataFrame) -> np.ndarray:
            """This returns a DF containing the calculated trip_duration in minutes."""
            data = data.copy()
            # Convert to minutes
            MINS = 60
            try:
                trip_duration = (
                    data["tpep_dropoff_datetime"] - data["tpep_pickup_datetime"]
                )
            except:
                trip_duration = (
                    data["lpep_dropoff_datetime"] - data["lpep_pickup_datetime"]
                )
            trip_duration = round(trip_duration.dt.total_seconds() / MINS, 2)
            return trip_duration

        data["id"] = data["VendorID"].apply(get_unique_IDs)  # Generate IDs
        logger.info("Added IDs! ")
        data["trip_duration"] = calculate_trip_duration(data)
        data = data.loc[
            (data["trip_duration"] > MIN_THRESH)
            & (data["trip_duration"] <= TRIP_DUR_THRESH)
        ]
        data = data.loc[
            (data["trip_distance"] > MIN_THRESH)
            & (data["trip_distance"] <= TRIP_DIST_THRESH)
        ]
        data = data.loc[
            (data["total_amount"] > MIN_THRESH)
            & (data["total_amount"] <= TOTAL_AMT_THRESH)
        ]
        data["trip_duration"] = np.log1p(data["trip_duration"])  # Log transform
    return data


def split_into_features_n_target(*, data: pd.DataFrame, target: str) -> tp.Tuple:
    """Split the data into independentand dependent features.

    Params:
    -------
    data (Pandas DF): DF containing the training data.
    target (int): The dependent feature.

    Returns:
    --------
    X, y (Tuple): The independent and dependent features respectively.
    """
    if target in data.columns:
        X = data.drop(columns=[target])
        y = data[target]
    else:
        raise NotImplementedError("Unsupported Dataframe")
    return (X, y)


def split_train_data(
    *, data: pd.DataFrame, target: str, test_size: float, random_state: int
) -> tp.Tuple:
    """This returns a split training data containing the
    X_train, X_validate, y_train and y_validate

    Params:
    -------
    data (Pandas DF): DF containing the training data.
    target (int): The dependent feature.
    test_size (float): The proportion of the data to include in the test split.
    random_state (int): Controls the shuffling applied and ensures reproducibility.

    Returns:
    --------
    X_train, X_validate, y_train and y_validate (tuple):
        A tuple containing the training and validation sets.
    """
    X, y = split_into_features_n_target(data=data, target=target)

    X_train, X_validate, y_train, y_validate = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return (X_train, X_validate, y_train, y_validate)


def validate_training_input(
    *,
    data: pd.DataFrame,
) -> tp.Tuple[tp.Optional[pd.DataFrame], tp.Union[None, str]]:
    """This is used to validate the training data using a Pydantic Model.

    Params:
    -------
    data (Pandas DF): DF containing the training data.

    Returns:
    --------
    data (Pandas DF): The validated DF.
    error (str or None): None if there's no error else a str.
    """
    # load the data
    data = data.copy()
    error = None
    # Validate the data. Convert NaNs to None
    try:
        validated_data = ValidateTrainingData(
            inputs=data.replace({np.nan: None}).to_dict(orient="records")
        )
        validated_dict = validated_data.dict().get("inputs")  # Extract the data
        data = pd.DataFrame(data=validated_dict)
        return (data, error)

    except ValidationError as err:  # pragma: no cover
        error = err.json()
        return (None, error)


def validate_input(
    *,
    data: pd.DataFrame,
) -> tp.Tuple[tp.Optional[pd.DataFrame], tp.Union[None, str]]:
    """This is used to validate the input data using a Pydantic Model.

    Params:
    -------
    data (Pandas DF): DF containing the training data.

    Returns:
    --------
    data (Pandas DF): The validated DF.
    error (str or None): None if there's no error else a str.
    """
    # load the data
    data = data.copy()  # pragma: no cover
    error = None  # pragma: no cover

    # Validate the data. Convert NaNs to None
    try:  # pragma: no cover
        validated_data = ValidateInputSchema(
            inputs=data.replace({np.nan: None}).to_dict(orient="records")
        )
        validated_dict = validated_data.dict().get("inputs")  # Extract the data
        data = pd.DataFrame(data=validated_dict)
        return (data, error)

    except ValidationError as err:  # pragma: no cover
        error = err.json()
        return (None, error)


def save_model(*, filename: tp.Union[str, Path], pipe: Pipeline) -> None:
    """This is used to persit a model.

    Params:
    -------
    filename (Path): Filepath to save the data.

    Returns:
    --------
    None
    """
    filename = TRAINED_MODELS_FILEPATH / filename

    logger.info("Saving Model ...")
    with open(filename, "wb") as file:
        joblib.dump(pipe, file)


def load_model(*, filename: tp.Union[str, Path]) -> Estimator:
    """This is used to load the trained model."""
    filename = TRAINED_MODELS_FILEPATH / filename
    logger.info("Loading Model ...")
    with open(filename, "rb") as file:
        trained_model = joblib.load(filename=file)
    return trained_model


def remove_old_pipelines(*, files_to_remove: tp.Optional[tp.List[str]] = None) -> None:
    """
    This is used to remove trained models.
    """
    if files_to_remove is None:
        files_to_remove = [config.path_config.TEST_MODEL_PATH]
    for model_file in TRAINED_MODELS_FILEPATH.iterdir():
        if model_file.name in files_to_remove:
            logger.info("Model deleted ...")
            model_file.unlink()


def load_version() -> str:
    """This is used to load the model verson."""
    filename = SRC_ROOT / "VERSION"
    with open(filename, "r") as file:
        __version__ = file.read().strip()
    return __version__
