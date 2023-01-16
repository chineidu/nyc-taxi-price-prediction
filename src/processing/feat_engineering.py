"""
This module is used to perform feature engineering.

author: Chinedu Ezeofor
"""

import typing as tp

# Standard imports
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CalculateDayOfWeek(BaseEstimator, TransformerMixin):
    """Custom Transformer used to calculate the DayOfWeek. It allows the Class
    to work in Scikit-learn Pipelines."""

    def __init__(self, feature: str):
        self.feature = feature

    def fit(self, X, y=None):  # pylint: disable=unused-argument
        return self

    def transform(self, X, y=None) -> pd.DataFrame:  # pylint: disable=unused-argument
        X = X.copy()
        X["day_of_week"] = X[self.feature].dt.dayofweek
        return X


class CalculateHourOfDay(BaseEstimator, TransformerMixin):
    """Custom Transformer used to calculate the HourOfDay. It allows the Class
    to work in Scikit-learn Pipelines."""

    def __init__(self, feature: str):
        self.feature = feature

    def fit(self, X, y=None):  # pylint: disable=unused-argument
        return self

    def transform(self, X, y=None) -> pd.DataFrame:  # pylint: disable=unused-argument
        X = X.copy()
        X["hour_of_day"] = X[self.feature].dt.hour
        return X


class SelectFeatures(BaseEstimator, TransformerMixin):
    """Custom Transformer used to select the features. It allows
    the Class to work in Scikit-learn Pipelines."""

    def __init__(self, features: tp.List[str]):
        self.features = features

    def fit(self, X, y=None):  # pylint: disable=unused-argument
        return self

    def transform(self, X, y=None) -> pd.DataFrame:  # pylint: disable=unused-argument
        X = X.copy()
        X = X[self.features]
        return X
