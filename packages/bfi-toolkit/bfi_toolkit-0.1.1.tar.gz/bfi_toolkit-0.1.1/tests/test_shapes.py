import pandas as pd
import numpy as np
from bfi_toolkit.baseflow import estimate_forward_baseflow, estimate_backward_baseflow, apply_decision_tree

def test_baseflow_shapes():
    idx = pd.date_range("2000-01-01", periods=30, freq="D")
    q = pd.Series(10 + np.sin(np.linspace(0, 3, 30)), index=idx)
    bf_f = estimate_forward_baseflow(q, k=0.1)
    bf_b = estimate_backward_baseflow(q, k=0.1)
    bf = apply_decision_tree(q, bf_f, bf_b)
    assert len(q) == len(b

