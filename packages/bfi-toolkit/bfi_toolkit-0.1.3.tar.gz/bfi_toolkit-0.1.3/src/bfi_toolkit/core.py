from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any, Dict

from .utils.logger import get_logger
from .utils.data_utils import to_dataframe
from .utils.validation import validate_pairs_length
from .optimization import optimize_k
from .baseflow import (
    estimate_forward_baseflow,
    estimate_backward_baseflow,
    apply_decision_tree,
)

logger = get_logger()


def _build_pairs(
    df: pd.DataFrame,
    day_after_peak: int,
    min_events: int,
    min_pairs: int
) -> pd.DataFrame:
    """
    Build Q-Q* pairs excluding rising limb periods.

    Parameters
    ----------
    df : pd.DataFrame
        Streamflow data with column 'QQ'.
    day_after_peak : int
        Number of days to exclude after each detected runoff peak.
    min_events : int
        Minimum number of runoff events required.
    min_pairs : int
        Minimum number of Q–Q* pairs required.

    Returns
    -------
    pd.DataFrame with ['QQ', 'QQ_*'].
    """
    ser = df["QQ"].copy()
    ser = ser[ser != 0].dropna()

    # Identify rising limb
    diff = ser.diff()
    start_inc = ser[diff > 0]

    # --- Check runoff events ---
    if len(start_inc) < min_events:
        msg = (f"Runoff events ({len(start_inc)}) below threshold "
               f"({min_events}). Runoff Criteria not met.")
        logger.error(msg)
        raise ValueError(msg)

    # Exclude after peaks
    days_to_remove = set()
    for day in start_inc.index:
        days_to_remove.update(pd.date_range(start=day, periods=day_after_peak, freq="D"))

    filtered = ser[~ser.index.isin(days_to_remove)].copy()

    # --- Build Q-Q* pairs ---
    Q_vals, Qs_vals, dates = [], [], []
    for i in range(1, len(filtered)):
        t = filtered.index[i]
        t_prev = t - pd.Timedelta(days=1)
        if t_prev in filtered.index:
            Q_vals.append(filtered.loc[t])
            Qs_vals.append(filtered.loc[t_prev])
            dates.append(t)

    pairs = pd.DataFrame({"QQ": Q_vals, "QQ_*": Qs_vals}, index=dates)

    # --- Check data pairs ---
    if len(pairs) < min_pairs:
        msg = (f"Q–Q* data pairs ({len(pairs)}) below threshold "
               f"({min_pairs}). Data Pairs Criteria not met.")
        logger.error(msg)
        raise ValueError(msg)

    return pairs


def compute_bfi(
    data: Any,
    day_after_peak: int = 5,
    start_date: str | None = None,
    min_events: int = 50,
    min_pairs: int = 50,
) -> Dict[str, Any]:
    """
    Compute Baseflow Index (BFI) and baseflow series.

    Parameters
    ----------
    data : DataFrame | numpy.ndarray | list | torch.Tensor
        Streamflow time series. If DataFrame, must contain column 'QQ'.
        If index is not datetime, a daily index is assigned.
    day_after_peak : int
        Number of days after peak to exclude in pair building.
    start_date : str | None
        Start date for generated index if data has no datetime index.
        Default = None → auto-select '2000-01-01'.
    min_events : int
        Minimum number of runoff events required.
    min_pairs : int
        Minimum number of Q–Q* pairs required.

    Returns
    -------
    dict with keys:
        - 'baseflow' : pd.Series
        - 'k'        : float
        - 'bfi'      : float
        - 'error'    : float
    """
    logger.info("Starting BFI computation")

    df = to_dataframe(data, start_date=start_date)
    logger.debug(f"Input converted to DataFrame with shape {df.shape}")

    # Build valid Q-Q* pairs with criteria checks
    pairs = _build_pairs(df, day_after_peak, min_events, min_pairs)

    Q = pairs["QQ"].values
    Q_star = pairs["QQ_*"].values

    k, err = optimize_k(Q, Q_star)
    logger.info(f"Optimized k = {k:.4f}, objective = {err:.6f}")

    bf_f = estimate_forward_baseflow(df["QQ"], k)
    bf_b = estimate_backward_baseflow(df["QQ"], k)
    baseflow = apply_decision_tree(df["QQ"], bf_f, bf_b)

    total_q = float(df["QQ"].sum())
    bfi = float(baseflow.sum() / total_q) if total_q != 0 else np.nan
    logger.info(f"Computed BFI = {bfi:.4f}")

    return {"baseflow": baseflow, "k": float(k), "bfi": bfi, "error": float(err)}
