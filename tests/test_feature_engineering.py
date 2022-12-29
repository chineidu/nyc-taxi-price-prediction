import pandas as pd

from feature_engine.transformation import YeoJohnsonTransformer


# Custom Imports
from src.config.core import config
from src.processing.feat_engineering import (
    CalculateDayOfWeek,
    CalculateHourOfDay,
    SelectFeatures,
)


def test_day_of_week_feature(test_data: pd.DataFrame) -> None:
    """This tests the day of the week feature."""
    # Given
    expected_output = [1, 0, 1, 1]
    day_of_wk = CalculateDayOfWeek(feature="tpep_pickup_datetime")
    selected_rows = [300, 600, 800, 1_800]

    # When
    trans_df = day_of_wk.fit_transform(test_data).iloc[selected_rows]
    result = trans_df["day_of_week"].to_list()

    # Then
    assert expected_output == result


def test_hour_of_day_feature(test_data: pd.DataFrame) -> None:
    """This tests the hour of the day."""
    # Given
    expected_output = [23, 0, 1, 2]
    day_of_wk = CalculateHourOfDay(feature="tpep_pickup_datetime")
    selected_rows = [600, 950, 1_300, 1_800]

    # When
    trans_df = day_of_wk.fit_transform(test_data).iloc[selected_rows]
    result = trans_df["hour_of_day"].to_list()

    # Then
    assert expected_output == result


def test_select_input_feature(test_data: pd.DataFrame) -> None:
    """This tests the selection of features."""
    # Given
    expected_output = [
        "DOLocationID",
        "payment_type",
        "PULocationID",
        "RatecodeID",
        "total_amount",
        "tpep_pickup_datetime",
        "trip_distance",
        "VendorID",
    ]
    input_feats = SelectFeatures(features=config.model_config.INPUT_FEATURES)

    # When
    trans_df = input_feats.fit_transform(test_data)
    result = list(trans_df.columns)

    # Then
    assert expected_output == result


def test_yeo_johnson_transformer(test_data: pd.DataFrame) -> None:
    """This tests the YeoJohnson transformation of features."""
    # Given
    expected_output = [
        [0.7669019283779493, 0.6459307021685727, 1.3564266688687754, 1.663641398396483],
        [1.4781449968399125, 1.489422779650168, 1.6588396503845306, 1.7219362902335753],
    ]

    selected_rows = [300, 600, 800, 1_800]

    # When
    yeo_tranf = YeoJohnsonTransformer(
        variables=config.model_config.VARS_TO_LOG_TRANSFORM
    )
    trans_df = yeo_tranf.fit_transform(test_data).iloc[selected_rows]
    result = [trans_df["trip_distance"].to_list(), trans_df["total_amount"].to_list()]

    # Then
    assert expected_output == result
