import numpy as np
import pandas as pd
import pytest
from bfi_toolkit.utils.data_utils import to_dataframe, detect_input_type

def test_detect_types():
    assert detect_input_type(pd.DataFrame({"QQ":[1,2]})) == "dataframe"
    assert detect_input_type(np.array([1,2,3])) == "numpy"
    assert detect_input_type([1,2,3]) == "list"

def test_to_dataframe_from_list():
    df = to_dataframe([1,2,3], start_date="2020-01-01")
    assert list(df.columns) == ["QQ"]
    assert len(df) == 3
    assert str(df.index[0].date()) == "2020-01-01"

