# src/dynamic_sarimax/metrics.py
from __future__ import annotations
import numpy as np


def mse(y_true, y_pred) -> float:
    """
    Mean Squared Error (MSE).

    Computes:
        MSE = mean((y_true - y_pred) ** 2)

    Args:
        y_true: Iterable of true target values.
        y_pred: Iterable of predicted values.

    Returns:
        Mean squared error as a float. Returns NaN if inputs contain no finite values.
    """
    y = np.asarray(y_true, dtype=float)
    yhat = np.asarray(y_pred, dtype=float)
    return float(np.mean((y - yhat) ** 2))


def smape(y_true, y_pred) -> float:
    """
    Symmetric Mean Absolute Percentage Error (sMAPE).

    Implements the strict R-equivalent formulation:
        sMAPE = mean(200 * |y_t - ŷ_t| / (|y_t| + |ŷ_t|))

    - Excludes pairs where (|y_t| + |ŷ_t|) == 0.
    - Returns NaN if no valid pairs remain.

    Args:
        y_true: Iterable of true target values.
        y_pred: Iterable of predicted values.

    Returns:
        Symmetric mean absolute percentage error (percentage units).
    """
    y = np.asarray(y_true, dtype=float)
    yhat = np.asarray(y_pred, dtype=float)

    num = 200.0 * np.abs(y - yhat)
    denom = np.abs(y) + np.abs(yhat)

    # Valid pairs: finite values with nonzero denominator
    mask = np.isfinite(num) & np.isfinite(denom) & (denom > 0)
    if not np.any(mask):
        return np.nan

    return float(np.mean(num[mask] / denom[mask]))
