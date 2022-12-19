# Standard imports
import numpy as np
import pandas as pd
from pydantic import BaseModel, ValidationError
import yaml

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

# Built-in library
import itertools
import re
import json
import typing as tp

import warnings

warnings.filterwarnings("error")

# for saving the pipeline
import joblib

# from Scikit-learn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Binarizer
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics

# from feature-engine
from feature_engine.imputation import (
    AddMissingIndicator,
    MeanMedianImputer,
    CategoricalImputer,
)


from feature_engine.transformation import (
    LogTransformer,
    YeoJohnsonTransformer,
)

from feature_engine.discretisation import EqualFrequencyDiscretiser

from feature_engine.selection import DropFeatures
from feature_engine.wrappers import SklearnTransformerWrapper

# Custom Imports
from processing.data_manager import load_data, validate_input
import processing.feat_engineering as fe
from config.schema import (
    TrainingSchema,
    ValidateTrainingData,
    ModelConfig,
    MLFlowConfig,
    ConfigVars,
)


# Load Data
train_data = load_data("data/yellow_tripdata_2022-01.parquet")
test_data = load_data("data/yellow_tripdata_2022-02.parquet")

