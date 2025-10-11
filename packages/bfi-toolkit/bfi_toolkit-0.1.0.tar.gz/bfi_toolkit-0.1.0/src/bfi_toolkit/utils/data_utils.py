from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any

def detect_input_type(data: Any) -> str:
    if isinstance(data, pd.DataFrame):
        return "dataframe"
    if isinstance(data, np.ndarray):
        return "numpy"
    if isinstance(data, list):
        return "list"
    try:
        import torch
        if isinstance(data, torch.Tensor):
            return "torch"
    except Exception:
        pass
    raise TypeError(
        "Unsupported data type. Must be pandas.DataFrame, numpy.ndarray, list, or torch.Tensor."
    )

def to_dataframe(data: Any, start_date: str = "2000-01-01") -> pd.DataFrame:
    """
    Normalize user input to a DataFrame with a DatetimeIndex and column 'QQ'.
    Accepted types: DataFrame (must contain 'QQ'), numpy array, list, torch.Tensor.
    If index is not datetime, a daily index starting at `start_date` is assigned.
    """
    dtype = detect_input_type(data)

    if dtype == "dataframe":
        df = data.copy()
        if "QQ" not in df.columns:
            raise ValueError("DataFrame must contain a 'QQ' column.")
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.date_range(start=start_date, periods=len(df), freq="D")
        return df

    if dtype in {"numpy", "list"}:
        arr = np.asarray(data, dtype=float).ravel()
        df = pd.DataFrame({"QQ": arr})
        df.index = pd.date_range(start=start_date, periods=len(df), freq="D")
        return df

    if dtype == "torch":
        import torch
        arr = data.detach().cpu().numpy().ravel()
        df = pd.DataFrame({"QQ": arr})
        df.index = pd.date_range(start=start_date, periods=len(df), freq="D")
        return df

    # should not reach here
    raise TypeError(f"Unsupported data type: {type(data)}")

