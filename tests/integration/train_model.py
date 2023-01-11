"""
This module is used to train the model.
This was done to prevent the model from depending on 
the custom package `src`

author: Chinedu Ezeofor
"""
import typing as tp
import warnings
import logging
import joblib
from pprint import pprint as pp
import uuid

# from feature-engine
from feature_engine.imputation import AddMissingIndicator, MeanMedianImputer
from feature_engine.selection import DropFeatures
from feature_engine.transformation import YeoJohnsonTransformer
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings("error")

# Standard imports
import numpy as np
import pandas as pd

# From Scikit-learn
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import feat_engineering as fe


def _set_up_logger(delim: str = "::") -> tp.Any:
    """This is used to create a basic logger."""
    format_ = f"%(levelname)s {delim} %(asctime)s {delim} %(message)s"
    logging.basicConfig(level=logging.INFO, format=format_)
    logger = logging.getLogger(__name__)
    return logger


def get_unique_IDs(feat: str) -> str:
    """This returns a universally unique generated ID."""
    if feat is not None:
        return str(uuid.uuid4())


def load_data(*, filename: str, uri: bool = False) -> pd.DataFrame:
    """This returns the data as a Pandas DF.

    Params:
    -------
    filename (Path): The input filepath.
    uri (bool, default=False): True if the filename is an S3 URI else False

    Returns:
    --------
    data (Pandas DF): The loaded DF.
    """
    if not uri:
        filename = f"data/{filename}"
    logger.info("Loading Data ... ")
    try:
        data = (
            pd.read_csv(filename)
            if filename.endswith("csv")
            else pd.read_parquet(filename)
        )
    except Exception as err:
        logger.info(err)

    TRIP_DUR_THRESH = 60  # trip_duration
    TRIP_DIST_THRESH = 30  # trip_distance
    TOTAL_AMT_THRESH = 100  # total_amount
    MIN_THRESH = 0

    if filename.endswith("parquet"):

        def calculate_trip_duration(data: pd.DataFrame) -> pd.DataFrame:
            """This returns a DF containing the calculated trip_duration in minutes."""
            data = data.copy()
            # Convert to minutes
            MINS = 60
            trip_duration = data["tpep_dropoff_datetime"] - data["tpep_pickup_datetime"]
            trip_duration = round(trip_duration.dt.total_seconds() / MINS, 2)
            return trip_duration

        data["id"] = data["VendorID"].apply(get_unique_IDs)  # Generate IDs
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


logger = _set_up_logger()

# Constants
TARGET = "trip_duration"
TEST_SIZE = 0.1
RANDOM_STATE = 123

INPUT_FEATURES = [
    "DOLocationID",
    "payment_type",
    "PULocationID",
    "RatecodeID",
    "total_amount",
    "tpep_pickup_datetime",
    "trip_distance",
    "VendorID",
]
NUM_VARS_WF_NA = ["RatecodeID"]
TEMPORAL_VAR = "tpep_pickup_datetime"
IMPORTANT_FEATURES = [
    "day_of_week",
    "DOLocationID",
    "hour_of_day",
    "payment_type",
    "PULocationID",
    "RatecodeID",
    "RatecodeID_na",
    "total_amount",
    "tpep_pickup_datetime",
    "trip_distance",
    "VendorID",
]
VARS_TO_DROP = ["tpep_pickup_datetime"]
VARS_TO_LOG_TRANSFORM = ["trip_distance", "total_amount"]

params = {
    "n_estimators": 10,
    "max_depth": 10,
    "random_state": 123,
}


# Build Train Pipeline
rf_pipe = Pipeline(
    steps=[
        # ===== Select input features =====
        (
            "input vars",
            fe.SelectFeatures(features=INPUT_FEATURES),
        ),
        # ===== Add NaN flags =====
        (
            "add na_flag",
            AddMissingIndicator(missing_only=True, variables=NUM_VARS_WF_NA),
        ),
        # ===== Impute NaNs =====
        (
            "impute num_vars",
            MeanMedianImputer(imputation_method="median", variables=NUM_VARS_WF_NA),
        ),
        # ===== Create new features =====
        (
            "cal day_of_week",
            fe.CalculateDayOfWeek(feature=TEMPORAL_VAR),
        ),
        (
            "cal hour_of_day",
            fe.CalculateHourOfDay(feature=TEMPORAL_VAR),
        ),
        # ===== Select features =====
        (
            "important vars",
            fe.SelectFeatures(features=IMPORTANT_FEATURES),
        ),
        # ===== Drop features =====
        (
            "drop features",
            DropFeatures(features_to_drop=VARS_TO_DROP),
        ),
        # ===== Transform features =====
        (
            "YeoJohnson transformation",
            YeoJohnsonTransformer(variables=VARS_TO_LOG_TRANSFORM),
        ),
        # ===== Scale features =====
        ("scale data", StandardScaler()),
        # ===== Random Forest model =====
        (
            "RF model",
            RandomForestRegressor(**params),
        ),
    ]
)


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

    target = target = TARGET
    test_size = TEST_SIZE
    random_state = RANDOM_STATE

    # Split the data
    X_train, X_validate, y_train, y_validate = split_train_data(
        data=train_data,
        target=target,
        test_size=test_size,
        random_state=random_state,
    )

    # Train Model
    logger.info("Training model ...")
    rf_pipe.fit(X_train, y_train)

    # Predictions using validation data
    logger.info("Making Predictions ...")
    y_pred = rf_pipe.predict(X_validate)
    logger.info("Done ...")
    return rf_pipe, y_validate, y_pred


if __name__ == "__main__":  # pragma: no cover
    # Load Data
    fp = "yellow_tripdata_2022-01.parquet"
    train_data = load_data(filename=fp)

    # Train model
    pipe, y_validate, y_pred = train_model(train_data=train_data)
    pp(y_pred[:10])

    # Save model
    model_fp = "trained_models/model.pkl"
    with open(model_fp, "wb") as file:
        joblib.dump(pipe, file)
    logger.info("Saving Done ...")

    logger.info("Making predictions on unseen data ...")
    new_data = {
        "DOLocationID": [82, 72],
        "payment_type": [1, 2],
        "PULocationID": [5, 99],
        "RatecodeID": [np.nan, 2],
        "tpep_pickup_datetime": ["2022-12-16 14:33:43", "2022-12-18 09:18:03"],
        "trip_distance": [5.5, 3.1],
        "VendorID": [2, 1],
        "total_amount": [12, 9.5],
    }

    df = pd.DataFrame(new_data)
    # Conevrt to datetime
    df["tpep_pickup_datetime"] = pd.to_datetime(
        df["tpep_pickup_datetime"], errors="coerce"
    )

    # Load model
    logger.info("Loading model ...")
    model_fp = "trained_models/model.pkl"
    with open(model_fp, "rb") as file:
        estimator = joblib.load(file)

    logger.info("Getting predictions ...")
    pp(estimator.predict(df))
