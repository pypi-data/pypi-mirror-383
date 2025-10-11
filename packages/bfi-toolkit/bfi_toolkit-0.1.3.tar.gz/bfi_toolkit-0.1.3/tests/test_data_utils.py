import pandas as pd
import numpy as np
import pytest

from bfi_toolkit.utils.data_utils import to_dataframe

# Optional torch support
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def test_list_input_creates_dataframe():
    data = [1, 2, 3, 4]
    df = to_dataframe(data, start_date="2020-01-01")
    assert isinstance(df, pd.DataFrame)
    assert "QQ" in df.columns
    assert len(df) == 4
    assert isinstance(df.index, pd.DatetimeIndex)
    assert str(df.index[0].date()) == "2020-01-01"


def test_numpy_input_creates_dataframe():
    arr = np.array([0.5, 1.5, 2.5])
    df = to_dataframe(arr, start_date="2020-05-01")
    assert len(df) == 3
    assert df.iloc[1, 0] == 1.5
    assert df.index.freqstr == "D"


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not installed")
def test_torch_input_creates_dataframe():
    t = torch.tensor([1.0, 2.0, 3.0])
    df = to_dataframe(t, start_date="2021-01-01")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 1)
    assert df.index[0] == pd.Timestamp("2021-01-01")


def test_series_input_without_dates():
    s = pd.Series([1, 2, 3], name="QQ")
    df = to_dataframe(s, start_date="2022-01-01")
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index[0] == pd.Timestamp("2022-01-01")


def test_dataframe_with_datetime_index():
    dates = pd.date_range("2019-01-01", periods=3, freq="D")
    df_in = pd.DataFrame({"QQ": [1, 2, 3]}, index=dates)
    df_out = to_dataframe(df_in)
    assert (df_out.index == dates).all()


def test_dataframe_without_datetime_index():
    df_in = pd.DataFrame({"QQ": [1, 2, 3]})
    df_out = to_dataframe(df_in, start_date="2018-01-01")
    assert isinstance(df_out.index, pd.DatetimeIndex)
    assert df_out.index[0] == pd.Timestamp("2018-01-01")


def test_dataframe_missing_QQ_column_raises():
    df_in = pd.DataFrame({"flow": [1, 2, 3]})
    with pytest.raises(ValueError):
        to_dataframe(df_in)


def test_invalid_type_raises():
    invalid_data = {"a": 1, "b": 2}
    with pytest.raises(TypeError):
        to_dataframe(invalid_data)
