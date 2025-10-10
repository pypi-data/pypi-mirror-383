# src/dynamic_sarimax/model.py
from __future__ import annotations
from typing import Optional, Dict, Any
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from .config import SarimaxConfig
from .features import ExogLagTransformer
from .utils import check_monotone_index


class DynamicSarimax:
    """
    Thin SARIMAX wrapper that enforces safe exogenous alignment and lag usage.

    This class encapsulates:
      - Input validation for monotone, duplicate-free indices.
      - Exogenous lagging and train-only scaling via `ExogLagTransformer`.
      - A clear contract for forecasting with or without exogenous inputs.

    Notes:
      - If `lagger` is None, the model reduces to univariate SARIMAX on `y`.
      - If `lagger` is set, `fit` aligns `X` and `y`, applies lag/scale, and trims
        leading rows made invalid by lagging before fitting statsmodels.
      - `forecast` with a lagger requires both `X_future` and `start_idx`. The caller
        must provide an `X_future` that contains at least the historical portion needed
        to resolve lagged exogenous values for the requested forecast window. If the
        caller intends to use true future X, they must include those rows as well.

    Args:
      cfg: SARIMAX hyperparameters.
      lagger: Optional exogenous lag transformer specification.

    Attributes:
      cfg: Stored copy of configuration.
      lagger: Stored lag transformer or None.
      _fit_res: statsmodels fit result after calling `fit`.

    Raises:
      ValueError: On malformed inputs or missing required exogenous data.
      RuntimeError: If methods are called before fitting.
    """

    def __init__(self, cfg: SarimaxConfig, lagger: Optional[ExogLagTransformer] = None):
        self.cfg = cfg
        self.lagger = lagger
        self._fit_res = None

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> "DynamicSarimax":
        """
        Fit the SARIMAX model on `y` (and optionally lagged exogenous `X`).

        - Validates monotone, duplicate-free indices.
        - If using exogenous lag, aligns `X` with `y`, fits scalers on lagged `X`
          restricted to the train period, and trims rows invalidated by lagging.

        Args:
          y: Target series with monotone-increasing index.
          X: Optional exogenous features aligned to `y`. Required if `lagger` is set.

        Returns:
          self

        Raises:
          ValueError: If `lagger` is set and `X` is missing or indices are invalid.
        """
        check_monotone_index(y, "y")
        exog = None
        y_use = y
        if self.lagger is not None:
            if X is None:
                raise ValueError("Exogenous X required when lagger is set")
            check_monotone_index(X, "X")
            if not X.index.equals(y.index):
                common = X.index.intersection(y.index)
                X = X.loc[common]
                y_use = y.loc[common]
            self.lagger.fit(X, y_use)
            X_lag = self.lagger.transform(X)
            mask = self.lagger.mask()
            exog = X_lag.loc[mask]
            y_use = y_use.loc[mask]

        trend = self.cfg.materialize_trend()
        self._fit_res = SARIMAX(
            y_use.values,
            order=self.cfg.order,
            seasonal_order=self.cfg.seasonal_order,
            exog=None if exog is None else exog.values,
            trend=trend,
            enforce_stationarity=self.cfg.enforce_stationarity,
            enforce_invertibility=self.cfg.enforce_invertibility,
        ).fit(disp=False)
        return self

    def forecast(
        self,
        steps: int,
        X_future: Optional[pd.DataFrame] = None,
        start_idx: Optional[int] = None,
    ) -> pd.Series:
        """
        Forecast the endogenous series for `steps` ahead.

        Cases:
          - No lagger: returns univariate SARIMAX predictions; `X_future` ignored.
          - With lagger: requires `X_future` and `start_idx`. `X_future` must contain
            all rows needed to compute lagged exogenous values for indices
            `[start_idx, start_idx + steps - 1]`. If those lagged values cannot be
            resolved from the provided data (insufficient history or missing future),
            a ValueError is raised.

        Args:
          steps: Number of steps to forecast.
          X_future: Exogenous data (historical plus any caller-provided future rows)
                    with the same columns used at training time.
          start_idx: Integer positional index into the original alignment space defining
                     the first forecasted time index.

        Returns:
          Series of length `steps` with predicted means.

        Raises:
          RuntimeError: If called before `fit`.
          ValueError: If `lagger` is set and either `X_future` or `start_idx` is missing,
                      or if lagged exogenous values cannot be formed for the window.
        """
        if self._fit_res is None:
            raise RuntimeError("Model not fit")

        if self.lagger is None:
            pred = self._fit_res.get_forecast(steps=steps)
            return pd.Series(pred.predicted_mean)

        if X_future is None or start_idx is None:
            raise ValueError(
                "X_future and start_idx required when using exogenous lagger"
            )

        # Delegates alignment, scaling, and block extraction. Raises on invalid blocks.
        block = self.lagger.future_block(X_future, start_idx=start_idx, steps=steps)
        pred = self._fit_res.get_forecast(steps=steps, exog=block.values)
        return pd.Series(pred.predicted_mean)

    def aic(self) -> float:
        """
        Return the model AIC.

        Returns:
          Akaike Information Criterion as a float.

        Raises:
          RuntimeError: If called before `fit`.
        """
        if self._fit_res is None:
            raise RuntimeError("Model not fit")
        return float(self._fit_res.aic)

    def model_info(self) -> Dict[str, Any]:
        """
        Return basic model metadata for inspection and logging.

        Returns:
          Dict with keys:
            - order: non-seasonal (p, d, q)
            - seasonal_order: seasonal (P, D, Q, s)
            - aic: model AIC
            - nobs: effective observations used in fit

        Raises:
          RuntimeError: If called before `fit`.
        """
        if self._fit_res is None:
            raise RuntimeError("Model not fit")
        return {
            "order": self.cfg.order,
            "seasonal_order": self.cfg.seasonal_order,
            "aic": float(self._fit_res.aic),
            "nobs": int(self._fit_res.nobs),
        }
