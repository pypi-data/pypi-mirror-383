# src/dynamic_sarimax/evaluation.py
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Optional, Literal
from .config import SarimaxConfig, ExogLagSpec
from .features import ExogLagTransformer
from .model import DynamicSarimax
from .metrics import mse, smape


def _normalize_exog(X: Optional[pd.Series | pd.DataFrame]) -> Optional[pd.DataFrame]:
    if X is None:
        return None
    if isinstance(X, pd.DataFrame):
        return X
    return X.to_frame(name=getattr(X, "name", "exog"))


def rolling_evaluate(
    y: pd.Series,
    X: Optional[pd.Series | pd.DataFrame],
    cfg: SarimaxConfig,
    delay: Optional[int],
    horizons: int,
    train_frac: float = 0.8,
    min_train: int = 30,
    *,
    # Exogenous usage policy
    allow_future_exog: bool = False,
    X_future_manual: Optional[pd.DataFrame] = None,
    # Rolling strategy knobs
    strategy: Literal["expanding", "sliding"] = "expanding",
    window: Optional[int] = None,
    refit_every: int = 1,
    # Output control
    return_details: bool = False,
):
    """
    Rolling-origin evaluation for SARIMAX with configurable windowing, refit cadence,
    and strict control over future exogenous usage.

    By default, this performs expanding-window rolling evaluation with refitting at
    every origin and no peeking at future exogenous values.

    Windowing strategies:
      - strategy="expanding": train on [0..o-1] for origin o.
      - strategy="sliding":   train on last `window` observations [o-window .. o-1].
                              `window` must be provided and >= min_train.

    Refit cadence:
      - refit_every = 1 (default): refit parameters at *every* origin.
      - refit_every = k > 1: refit every k origins; in between, reuse the last
        fitted model to forecast from later origins with parameters held fixed.

    Exogenous policy:
      - If delay is None → univariate SARIMAX; forecasts full `horizons`.
      - If delay is not None and allow_future_exog is False:
          evaluate at most `steps_eff = min(horizons, delay)` per origin
          (prevents leakage; no future X allowed).
      - If delay is not None and allow_future_exog is True:
          caller must pass `X_future_manual` containing raw future exogenous rows
          (same columns as X). These are concatenated to historical X so lagging
          and scaling are consistent.

    Args:
      y: Target series with a monotone-increasing, duplicate-free index.
      X: Optional exogenous features aligned to `y` (Series or DataFrame).
      cfg: SARIMAX configuration.
      delay: Non-negative exogenous lag (b) or None to disable exogenous usage.
      horizons: Number of steps to forecast per origin.
      train_frac: Fraction used to determine initial training cutoff.
      min_train: Minimum effective nobs (post-lag trimming) required to keep a model.
      allow_future_exog: If True, authorize use of true future X; requires `X_future_manual`.
      X_future_manual: Future exogenous rows (same columns as X) to enable full horizons
                       when `allow_future_exog=True`.
      strategy: "expanding" (default) or "sliding".
      window: Training window size for "sliding" (required, >= min_train). Ignored otherwise.
      refit_every: Refit cadence (1 = refit at every origin).
      return_details: If True, also return the per-(origin,h) rows in addition to the
                      per-horizon aggregate.

    Returns:
      If return_details is False (default):
        - agg: DataFrame with columns ["h", "n_origins", "MSE", "sMAPE"], attrs contain
               {"macro_MSE": float, "macro_sMAPE": float}.
      If return_details is True:
        - (agg, details), where details has columns:
            ["origin", "h", "y_true", "y_hat"].

    Raises:
      ValueError: On invalid strategy parameters, missing/column-mismatched future X when
                  allow_future_exog=True, or horizons too large for series length.
      RuntimeError: If no evaluations are produced (e.g., all origins skipped).

    Notes:
      - No-peek behavior for exogenous strictly limits horizons to min(horizons, delay).
      - This function re-estimates parameters per `refit_every`; it does not (yet)
        perform state reconditioning between refits (planned for a future release).
    """
    if horizons <= 0:
        raise ValueError("horizons must be positive")
    if not (0.0 < train_frac < 1.0):
        raise ValueError("train_frac must be in (0, 1)")
    if refit_every < 1:
        raise ValueError("refit_every must be >= 1")

    N = len(y)
    train_end0 = int(np.floor(train_frac * N))
    test_start = train_end0
    last_origin = N - horizons
    if last_origin < test_start:
        raise ValueError("horizons too large relative to series length")

    if strategy not in ("expanding", "sliding"):
        raise ValueError('strategy must be "expanding" or "sliding"')
    if strategy == "sliding":
        if window is None:
            raise ValueError('window must be provided when strategy="sliding"')
        if window < min_train:
            raise ValueError("window must be >= min_train")

    Xdf = _normalize_exog(X)

    details_rows = []
    current_model: Optional[DynamicSarimax] = None

    origins = list(range(test_start, last_origin + 1))
    for i, o in enumerate(origins):
        # Training bounds per strategy
        start = 0 if strategy == "expanding" else max(0, o - window)

        need_refit = (current_model is None) or ((i % refit_every) == 0)

        if need_refit:
            y_tr = y.iloc[start:o]
            X_tr = None if Xdf is None else Xdf.iloc[start:o]

            if delay is None:
                current_model = DynamicSarimax(cfg=cfg, lagger=None)
                current_model.fit(y_tr, None)
            else:
                lagger = ExogLagTransformer(ExogLagSpec(delay=delay, scale=True))
                current_model = DynamicSarimax(cfg=cfg, lagger=lagger)
                current_model.fit(y_tr, X_tr)
                if current_model._fit_res.nobs < min_train:
                    current_model = None
                    continue  # skip this origin

        if current_model is None:
            continue  # no usable model at this origin

        # Determine legal steps
        if delay is None:
            steps_eff = horizons
        else:
            if not allow_future_exog:
                steps_eff = min(horizons, delay)
                if steps_eff <= 0:
                    continue
            else:
                steps_eff = horizons
                if Xdf is None:
                    raise ValueError("allow_future_exog=True requires historical X.")
                if X_future_manual is None:
                    raise ValueError(
                        "allow_future_exog=True but X_future_manual was not provided."
                    )
                hist_cols = list(Xdf.columns)
                fut_cols = list(X_future_manual.columns)
                if hist_cols != fut_cols:
                    raise ValueError(
                        f"Exogenous columns mismatch. Expected {hist_cols}, got {fut_cols}"
                    )

        # Forecast
        if delay is None:
            yhat = current_model.forecast(steps=steps_eff)
        else:
            if not allow_future_exog:
                # Historical X only; future_block will self-pad; no leakage since steps_eff <= delay
                X_hist = Xdf.iloc[:o]
                yhat = current_model.forecast(
                    steps=steps_eff, X_future=X_hist, start_idx=o
                )
            else:
                X_full_ext = pd.concat([Xdf, X_future_manual], axis=0)
                yhat = current_model.forecast(
                    steps=steps_eff, X_future=X_full_ext, start_idx=o
                )

        ytrue = y.iloc[o : o + steps_eff].reset_index(drop=True)
        for h in range(steps_eff):
            details_rows.append(
                {
                    "origin": o,
                    "h": h + 1,
                    "y_true": float(ytrue.iloc[h]),
                    "y_hat": float(yhat.iloc[h]),
                }
            )

    # Aggregate per-horizon
    details = pd.DataFrame(details_rows)
    if details.empty:
        raise RuntimeError("No evaluations produced - check inputs, delay, and flags")

    agg = (
        details.groupby("h", as_index=False)
        .apply(
            lambda g: pd.Series(
                {
                    "n_origins": len(g),
                    "MSE": mse(g["y_true"].values, g["y_hat"].values),
                    "sMAPE": smape(g["y_true"].values, g["y_hat"].values),
                }
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )

    macro_MSE = float(agg["MSE"].mean())
    macro_sMAPE = float(agg["sMAPE"].mean())
    agg.attrs["macro_MSE"] = macro_MSE
    agg.attrs["macro_sMAPE"] = macro_sMAPE

    if return_details:
        return agg, details
    return agg
