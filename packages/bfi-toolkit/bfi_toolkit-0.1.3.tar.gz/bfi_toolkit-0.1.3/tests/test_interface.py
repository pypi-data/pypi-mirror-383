import numpy as np
import pandas as pd
from bfi_toolkit import compute_bfi

def test_compute_bfi_with_list():
    data = [5, 5, 5, 6, 7, 6, 5.8, 5.6, 5.4, 5.2, 5, 4.9, 4.8]
    res = compute_bfi(data, day_after_peak=3, start_date="2020-01-01")
    assert "bfi" in res and "k" in res and "baseflow" in res

def test_compute_bfi_with_numpy():
    arr = np.array([5, 5, 5, 6, 7, 6, 5.8, 5.6, 5.4, 5.2, 5, 4.9, 4.8])
    res = compute_bfi(arr, day_after_peak=3, start_date="2020-01-01")
    assert len(res["baseflow"]) == len(arr)

def test_compute_bfi_with_dataframe():
    df = pd.DataFrame({"Date": pd.date_range("2020-01-01", periods=20, freq="D"),
                       "QQ": np.linspace(10, 5, 20)})
    res = compute_bfi(df, day_after_peak=3)
    assert 0 <= res["bfi"] <= 1 or np.isnan(res["bfi"])

