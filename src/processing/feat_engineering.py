"""
This module is used to perform feature engineering.

author: Chinedu Ezeofor
"""

# Standard imports
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

import typing as tp
from collections.abc import Callable


class CalculateDayOfWeek(BaseEstimator, TransformerMixin):
    """Custom Transformer used to calculate the DayOfWeek. It allows the Class
    to work in Scikit-learn Pipelines."""

    def __init__(self, feature: str):
        self.feature = feature

    def fit(
        self, X: tp.Union[pd.DataFrame, np.ndarray], y: tp.Optional[np.ndarray] = None
    ):
        return self

    def transform(
        self, X: tp.Union[pd.DataFrame, np.ndarray], y: tp.Optional[np.ndarray] = None
    ) -> pd.DataFrame:
        X = X.copy()
        X["day_of_week"] = X[self.feature].dt.dayofweek
        return X


class CalculateHourOfDay(BaseEstimator, TransformerMixin):
    """Custom Transformer used to calculate the HourOfDay. It allows the Class
    to work in Scikit-learn Pipelines."""

    def __init__(self, feature: str):
        self.feature = feature

    def fit(
        self, X: tp.Union[pd.DataFrame, np.ndarray], y: tp.Optional[np.ndarray] = None
    ):
        return self

    def transform(
        self, X: tp.Union[pd.DataFrame, np.ndarray], y: tp.Optional[np.ndarray] = None
    ) -> pd.DataFrame:
        X = X.copy()
        X["hour_of_day"] = X[self.feature].dt.dayofweek
        return X


class SelectFeatures(BaseEstimator, TransformerMixin):
    """Custom Transformer used to select the features. It allows
    the Class to work in Scikit-learn Pipelines."""

    def __init__(self, features: tp.List[str]):
        self.features = features

    def fit(
        self, X: tp.Union[pd.DataFrame, np.ndarray], y: tp.Optional[np.ndarray] = None
    ):
        return self

    def transform(
        self, X: tp.Union[pd.DataFrame, np.ndarray], y: tp.Optional[np.ndarray] = None
    ) -> pd.DataFrame:
        X = X.copy()
        X = X[self.features]
        return X


# Not Pickable so I had to use create individual classes
# as seen above
class TransformerWrapper(BaseEstimator, TransformerMixin):
    """Custom Wrapper for Transformers. It allows the decorated
    functions to work in Scikit-learn Pipelines."""

    def __init__(self, func: Callable):
        self.func = func

    def fit(self, *args, **kwargs):
        return self

    def transform(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """This allows you to call the function"""
        return self.transform(*args, **kwargs)


@TransformerWrapper
def calculate_day_of_week(data: pd.DataFrame) -> pd.DataFrame:
    """This returns a DF containing the calculated day_of_week."""
    data = data.copy()
    data["day_of_week"] = data["tpep_pickup_datetime"].dt.dayofweek
    return data


@TransformerWrapper
def calculate_hour_of_day(data: pd.DataFrame) -> pd.DataFrame:
    """This returns a DF containing the calculated hour_of_day."""
    data = data.copy()
    data["hour_of_day"] = data["tpep_pickup_datetime"].dt.hour
    return data