# src/dynamic_sarimax/selection.py
from __future__ import annotations
from typing import Sequence, Tuple
import pandas as pd
from .config import SarimaxConfig, ExogLagSpec
from .features import ExogLagTransformer
from .model import DynamicSarimax


def select_delay_by_aic(
    y_train: pd.Series,
    X_train: pd.Series | pd.DataFrame,
    delays: Sequence[int],
    cfg: SarimaxConfig,
    min_train: int = 30,
) -> Tuple[int, float]:
    """
    Select the exogenous lag `delay` that minimizes AIC on the training set.

    For each candidate delay `b`, this routine:
      1) Constructs an `ExogLagTransformer(b, scale=True)`.
      2) Fits a `DynamicSarimax` model on `y_train` with lagged/scaled `X_train`.
      3) Skips candidates whose effective sample size after lag trimming is < `min_train`.
      4) Tracks the (delay, AIC) pair with the smallest AIC.

    This procedure uses in-sample AIC as a lightweight model selection heuristic. It does
    not peek at future exogenous values and only considers effective observations that remain
    after applying the lag.

    Args:
      y_train: Training target series with a monotone-increasing, duplicate-free index.
      X_train: Training exogenous features aligned to `y_train`. Series or DataFrame.
      delays: Iterable of non-negative integer candidate lags to evaluate.
      cfg: SARIMAX configuration (orders, trend, enforcement flags).
      min_train: Minimum effective sample size (post-lag) required to keep a candidate.

    Returns:
      Tuple `(best_delay, best_aic)` where:
        - best_delay: The delay with the lowest AIC among evaluated candidates.
        - best_aic: The corresponding AIC value as a float.

    Raises:
      RuntimeError: If no candidate meets `min_train` after lag trimming.

    Example:
      >>> best_b, best_aic = select_delay_by_aic(
      ...     y_train, X_train, delays=range(0, 8), cfg=cfg, min_train=50
      ... )
    """
    best: Tuple[int | None, float] = (None, float("inf"))
    for b in delays:
        lagger = ExogLagTransformer(ExogLagSpec(delay=b, scale=True))
        model = DynamicSarimax(cfg=cfg, lagger=lagger)
        model.fit(y_train, X_train)  # trims via lagger
        nobs = model._fit_res.nobs
        if nobs < min_train:
            continue
        aic = model.aic()
        if aic < best[1]:
            best = (b, aic)

    if best[0] is None:
        raise RuntimeError(
            "AIC selection failed - not enough effective training data for given delays"
        )

    return best  # (best_delay, best_aic)
