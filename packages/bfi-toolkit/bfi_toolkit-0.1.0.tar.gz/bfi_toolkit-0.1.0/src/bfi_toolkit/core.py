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

def _build_pairs(df: pd.DataFrame, day_after_peak: int) -> pd.DataFrame:
    """
    Build Q-Q* pairs excluding windows after days with increases (rising limbs).
    Returns DataFrame with ['QQ','QQ_*'] indexed by the 'current' day (Q).
    """
    ser = df["QQ"].copy()
    ser = ser[ser != 0].dropna()

    # days with rising limb
    dif = ser.diff()
    start_inc = ser[dif > 0]
    days_to_remove = set()
    for day in start_inc.index:
        days_to_remove.update(pd.date_range(start=day, periods=day_after_peak, freq="D"))

    filtered = ser[~ser.index.isin(days_to_remove)].copy()

    Q_vals, Qs_vals, dates = [], [], []
    for i in range(1, len(filtered)):
        t = filtered.index[i]
        t_prev = t - pd.Timedelta(days=1)
        if t_prev in filtered.index:
            Q_vals.append(filtered.loc[t])
            Qs_vals.append(filtered.loc[t_prev])
            dates.append(t)

    return pd.DataFrame({"QQ": Q_vals, "QQ_*": Qs_vals}, index=dates)

def compute_bfi(
    data: Any,
    day_after_peak: int = 5,
    start_date: str = "2000-01-01",
) -> Dict[str, Any]:
    """
    Compute Baseflow Index (BFI) and baseflow series.

    Parameters
    ----------
    data : DataFrame | numpy.ndarray | list | torch.Tensor
        Streamflow time series. If DataFrame, must contain column 'QQ'.
        Index should be daily; if not, a daily index starting at `start_date` is assigned.
    day_after_peak : int
        Number of days after a detected increase to exclude when forming Q–Q* pairs.
    start_date : str
        Start date used when constructing a daily index for array/list inputs.

    Returns
    -------
    dict with keys:
        - 'baseflow' : pd.Series (same index as input)
        - 'k'        : float (optimized decay parameter)
        - 'bfi'      : float
        - 'error'    : float (objective at optimum)
    """
    logger.info("Starting BFI computation")

    df = to_dataframe(data, start_date=start_date)
    pairs = _build_pairs(df, day_after_peak=day_after_peak)
    validate_pairs_length(len(pairs), min_length=10)

    Q      = pairs["QQ"].values
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

