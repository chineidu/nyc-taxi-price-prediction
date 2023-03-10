"""
This module is used to build the training pipeline.

author: Chinedu Ezeofor
"""
# Built-in library
import warnings

from sklearn.ensemble import RandomForestRegressor

# from Scikit-learn
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from feature_engine.selection import DropFeatures

# from feature-engine
from feature_engine.imputation import MeanMedianImputer, AddMissingIndicator
from feature_engine.transformation import YeoJohnsonTransformer

# Custom Imports
import src.processing.feat_engineering as fe
from src.config.core import config

warnings.filterwarnings("error")


params = {
    "n_estimators": config.model_config.N_ESTIMATORS,
    "max_depth": config.model_config.MAX_DEPTH,
    "random_state": config.model_config.RANDOM_STATE,
}


# Build Train Pipeline
rf_pipe = Pipeline(
    steps=[
        # ===== Select input features =====
        (
            "input vars",
            fe.SelectFeatures(features=config.model_config.INPUT_FEATURES),
        ),
        # ===== Add NaN flags =====
        (
            "add na_flag",
            AddMissingIndicator(missing_only=True, variables=config.model_config.NUM_VARS_WF_NA),
        ),
        # ===== Impute NaNs =====
        (
            "impute num_vars",
            MeanMedianImputer(
                imputation_method="median", variables=config.model_config.NUM_VARS_WF_NA
            ),
        ),
        # ===== Create new features =====
        (
            "cal day_of_week",
            fe.CalculateDayOfWeek(feature=config.model_config.TEMPORAL_VAR),
        ),
        (
            "cal hour_of_day",
            fe.CalculateHourOfDay(feature=config.model_config.TEMPORAL_VAR),
        ),
        # ===== Select features =====
        (
            "important vars",
            fe.SelectFeatures(features=config.model_config.IMPORTANT_FEATURES),
        ),
        # ===== Drop features =====
        (
            "drop features",
            DropFeatures(features_to_drop=config.model_config.VARS_TO_DROP),
        ),
        # ===== Transform features =====
        (
            "YeoJohnson transformation",
            YeoJohnsonTransformer(variables=config.model_config.VARS_TO_LOG_TRANSFORM),
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
