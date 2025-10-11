from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any
import logging

logger = logging.getLogger(__name__)

# Optional torch support
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def to_dataframe(data: Any, start_date: str | None = None) -> pd.DataFrame:
    """
    Convert various input types into a standardized DataFrame
    with column 'QQ' and a daily DatetimeIndex.

    Parameters
    ----------
    data : DataFrame | list | np.ndarray | torch.Tensor
        Input streamflow time series. If DataFrame, must contain column 'QQ'.
    start_date : str | None
        Start date to use if generating a DatetimeIndex.
        If None, defaults to "2000-01-01".

    Returns
    -------
    pd.DataFrame
        A DataFrame with one column 'QQ' and daily DatetimeIndex.
    """
    # --- Case 1: pandas DataFrame ---
    if isinstance(data, pd.DataFrame):
        logger.debug("Detected input type: pandas.DataFrame")
        if "QQ" not in data.columns:
            raise ValueError("DataFrame must contain a 'QQ' column.")
        df = data.copy()

        # If index is not datetime → create one
        if not isinstance(df.index, pd.DatetimeIndex):
            logger.warning("No DatetimeIndex detected, creating daily index.")
            n = len(df)
            sdate = pd.to_datetime(start_date or "2000-01-01")
            df.index = pd.date_range(start=sdate, periods=n, freq="D")

        return df

    # --- Case 2: pandas Series ---
    if isinstance(data, pd.Series):
        logger.debug("Detected input type: pandas.Series")
        df = data.to_frame(name="QQ")
        if not isinstance(df.index, pd.DatetimeIndex):
            logger.warning("No DatetimeIndex detected, creating daily index.")
            n = len(df)
            sdate = pd.to_datetime(start_date or "2000-01-01")
            df.index = pd.date_range(start=sdate, periods=n, freq="D")
        return df

    # --- Case 3: list or numpy array ---
    if isinstance(data, (list, np.ndarray)):
        logger.debug(f"Detected input type: {type(data).__name__}")
        arr = np.array(data).astype(float)
        sdate = pd.to_datetime(start_date or "2000-01-01")
        idx = pd.date_range(start=sdate, periods=len(arr), freq="D")
        return pd.DataFrame({"QQ": arr}, index=idx)

    # --- Case 4: torch.Tensor ---
    if TORCH_AVAILABLE and isinstance(data, torch.Tensor):
        logger.debug("Detected input type: torch.Tensor")
        arr = data.detach().cpu().numpy().astype(float)
        sdate = pd.to_datetime(start_date or "2000-01-01")
        idx = pd.date_range(start=sdate, periods=len(arr), freq="D")
        return pd.DataFrame({"QQ": arr}, index=idx)

    # --- Unsupported type ---
    raise TypeError(
        f"Unsupported input type: {type(data)}. "
        f"Expected DataFrame, Series, list, numpy array, or torch Tensor."
    )
