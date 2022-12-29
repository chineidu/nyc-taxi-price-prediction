import datetime
import pandas as pd
import pytest
from pprint import pprint as pp


def get_birth_year(df: pd.DataFrame):
    """
     This function is used to calculate birth year and create a new column
    called birth_year in dataframe.

     parameters:
     df: dataframe having Age column

     returns:
     dataframe with birth_year column.
    """
    year = datetime.date.today().year
    replace_boolean_values = [True, False]
    if "Age" in df.columns:
        df["Age"] = df["Age"].replace(replace_boolean_values, 0)
        df["Birth_year"] = year - df["Age"]
    else:
        raise NotImplementedError("unsupported dataframe")
    return df


def test_get_birth_year_unsupported_excpetion():
    # Given
    data = [["krish", 1], ["jack", 50], ["elon", 100]]

    # When
    df_input = pd.DataFrame(data, columns=["Name", "Amount"])
    with pytest.raises(NotImplementedError) as exc_info:
        df_actual_output = get_birth_year(df_input)

    # Then
    assert exc_info.type is NotImplementedError
    assert exc_info.value.args[0] == "unsupported dataframe"

