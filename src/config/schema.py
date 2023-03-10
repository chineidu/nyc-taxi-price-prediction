"""
This module is used to validate the data.

author: Chinedu Ezeofor
"""
import typing as tp

# Built-in
import datetime

# Standard imports
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from sklearn.pipeline import Pipeline


class TrainingSchema(BaseModel):
    """
    All training data variables.
    """

    airport_fee: tp.Optional[float]
    congestion_surcharge: tp.Optional[float]
    day_of_week: tp.Optional[int]
    DOLocationID: tp.Optional[int]
    extra: tp.Optional[float]
    fare_amount: tp.Optional[float]
    hour_of_day: tp.Optional[int]
    improvement_surcharge: tp.Optional[float]
    mta_tax: tp.Optional[float]
    passenger_count: tp.Optional[float]
    payment_type: tp.Optional[int]
    RatecodeID: tp.Optional[float]
    PULocationID: tp.Optional[int]
    store_and_fwd_flag: str
    tip_amount: tp.Optional[float]
    tolls_amount: tp.Optional[float]
    total_amount: tp.Optional[float]
    tpep_dropoff_datetime: tp.Optional[datetime.datetime]
    tpep_pickup_datetime: tp.Optional[datetime.datetime]
    trip_distance: tp.Optional[float]
    VendorID: tp.Optional[int]


class InputSchema(BaseModel):
    """
    Config object for input data variables.
    """

    DOLocationID: tp.Optional[int]
    payment_type: tp.Optional[int]
    PULocationID: tp.Optional[int]
    RatecodeID: tp.Optional[float]
    total_amount: tp.Optional[float]
    tpep_pickup_datetime: tp.Optional[datetime.datetime]
    trip_distance: tp.Optional[float]
    VendorID: tp.Optional[int]


class ValidateTrainingData(BaseModel):
    """
    Config object for training data variables validation.
    """

    inputs: tp.List[TrainingSchema]


class ValidateInputSchema(BaseModel):
    """
    Config object for input data variables.
    """

    inputs: tp.List[InputSchema]


class ModelConfig(BaseModel):
    """
    Config object for model training and feature engineering.
    """

    RANDOM_STATE: int
    TEST_SIZE: float
    N_ESTIMATORS: int
    MAX_DEPTH: int
    TARGET: str
    NUMERICAL_VARS: tp.List[str]
    INPUT_FEATURES: tp.List[str]
    CATEGORICAL_VARS: tp.List[str]
    NUM_VARS_WF_NA: tp.List[str]
    IMPORTANT_FEATURES: tp.List[str]
    VARS_TO_DROP: tp.List[str]
    VARS_TO_LOG_TRANSFORM: tp.List[str]
    TEMPORAL_VAR: str


class PathConfig(BaseModel):
    """
    Config object for filepaths
    """

    TRAIN_DATA: str
    TEST_DATA: str
    MODEL_PATH: str
    TEST_MODEL_PATH: str
    TEST_DATA_WF_NO_TARGET: str


class ConfigVars(BaseModel):
    """
    Main configuration object.
    """

    model_config: ModelConfig
    path_config: PathConfig


class ValidateSklearnPipe(BaseModel):
    """
    Custom object for Scikit-learn Pipeline validation.
    """

    pipe: Pipeline

    class Config:
        arbitrary_types_allowed = True
