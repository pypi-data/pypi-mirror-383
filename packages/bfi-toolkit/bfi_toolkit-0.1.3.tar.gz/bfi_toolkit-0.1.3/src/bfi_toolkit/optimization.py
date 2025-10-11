from __future__ import annotations
import numpy as np
from scipy.optimize import minimize

def _objective(k: float, Q: np.ndarray, Q_star: np.ndarray) -> float:
    Q_est = np.exp(-k) * Q_star
    return float(np.mean(np.abs((Q_est / Q) - 1)))

def optimize_k(Q: np.ndarray, Q_star: np.ndarray) -> tuple[float, float]:
    """
    Multi-start Nelder-Mead to find k minimizing mean relative error.
    Returns (k, error).
    """
    bounds = [(0.001, 0.8)]
    inits = np.linspace(0.001, 0.6, 20)
    best_k, best_err = None, np.inf

    for g in inits:
        res = minimize(_objective, x0=g, args=(Q, Q_star), method="Nelder-Mead", bounds=bounds)
        if res.fun < best_err:
            best_err = float(res.fun)
            best_k = float(res.x[0])

    return best_k, best_err

