from __future__ import annotations
import logging
import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)

def estimate_forward_baseflow(q: pd.Series, k: float) -> pd.Series:
    bf = pd.Series(index=q.index, dtype=float)
    bf.iloc[0] = q.iloc[0]
    for i in range(1, len(q)):
        if q.iloc[i-1] == 0:
            bf.iloc[i] = 0.0
        else:
            bf.iloc[i] = np.exp(-k) * q.iloc[i-1]
    return bf

def estimate_backward_baseflow(q: pd.Series, k: float) -> pd.Series:
    bf = pd.Series(index=q.index, dtype=float)
    bf.iloc[-1] = q.iloc[-1]
    for i in range(len(q) - 2, -1, -1):
        bf.iloc[i] = np.exp(k) * q.iloc[i+1]
    return bf

def apply_decision_tree(q: pd.Series, bf_f: pd.Series, bf_b: pd.Series) -> pd.Series:
    logger.info("applying decision tree to combine forward/backward baseflow")
    bf = pd.Series(index=q.index, dtype=float)
    for i in range(1, len(q)-1):
        if q.iloc[i] < q.iloc[i-1]:  # recession
            if bf_b.iloc[i] <= q.iloc[i]:
                bf.iloc[i] = bf_b.iloc[i]
            elif bf_f.iloc[i] < q.iloc[i]:
                bf.iloc[i] = bf_f.iloc[i]
            else:
                bf.iloc[i] = q.iloc[i]
        else:  # ascension
            if min(bf_b.iloc[i], bf_f.iloc[i]) > q.iloc[i]:
                bf.iloc[i] = q.iloc[i]
            elif bf_b.iloc[i] > bf_f.iloc[i]:
                bf.iloc[i] = bf_f.iloc[i]
            else:
                bf.iloc[i] = bf_b.iloc[i]
    bf.iloc[0] = q.iloc[0]
    bf.iloc[-1] = q.iloc[-1]
    return bf

