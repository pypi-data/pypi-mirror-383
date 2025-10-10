# src/dynamic_sarimax/features.py
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from .config import ExogLagSpec
from .utils import ensure_dataframe, check_monotone_index, safe_shift, finite_mask_df


@dataclass
class _Scaler:
    """
    Simple standardizer that fits mean and std on a Series and applies z-scoring.

    Attributes:
        mean_: Fitted mean from training data.
        std_: Fitted standard deviation from training data. Falls back to 1.0 if
              the sample std is zero or non-finite to avoid division errors.
    """

    mean_: float | None = None
    std_: float | None = None

    def fit(self, s: pd.Series) -> None:
        """
        Fit mean and std on the provided Series.

        Args:
            s: Series to compute mean and std from. NaNs are ignored in statistics.
        """
        self.mean_ = float(np.nanmean(s.values))
        sd = float(np.nanstd(s.values, ddof=1))
        self.std_ = 1.0 if (not np.isfinite(sd) or sd == 0.0) else sd

    def transform(self, s: pd.Series) -> pd.Series:
        """
        Apply z-score transform using fitted mean and std.

        Args:
            s: Series to standardize.

        Returns:
            Standardized Series.

        Raises:
            RuntimeError: If called before `fit`.
        """
        if self.mean_ is None or self.std_ is None:
            raise RuntimeError("Scaler not fit")
        return (s - self.mean_) / self.std_


class ExogLagTransformer:
    """
    Exogenous lagging and train-only scaling with strict alignment guarantees.

    This transformer:
      - Shifts each exogenous column by `delay` steps to align causal usage.
      - Fits per-column scalers on the training portion only.
      - Applies the same scalers during transform and future block extraction.
      - Tracks a boolean mask indicating rows that remain valid after lagging.

    Notes:
      - `delay` must be non-negative. A delay of b means the model at time t uses X[t-b].
      - All inputs must have a monotone-increasing, duplicate-free index.
      - Column names are locked at fit time and enforced on transform.

    Args:
      spec: ExogLagSpec with `delay` and `scale` options.
    """

    def __init__(self, spec: ExogLagSpec):
        if spec.delay < 0:
            raise ValueError("delay must be >= 0")
        self.spec = spec
        self._scalers: dict[str, _Scaler] = {}
        self._mask: pd.Series | None = None
        self._columns: list[str] | None = None
        self._fitted_index: pd.Index | None = None

    def _lag_all(self, Xdf: pd.DataFrame) -> pd.DataFrame:
        """
        Shift all columns by `delay`.

        Args:
            Xdf: Exogenous features as a DataFrame.

        Returns:
            Lagged DataFrame with the same index and columns.
        """
        return pd.DataFrame(
            {col: safe_shift(Xdf[col], self.spec.delay) for col in Xdf.columns},
            index=Xdf.index,
        )

    def fit(self, X: pd.Series | pd.DataFrame, y: pd.Series) -> "ExogLagTransformer":
        """
        Fit lagging metadata and optional scalers on the training alignment.

        - Validates indices for X and y.
        - Intersects indices if they differ.
        - Builds lagged X and computes a finite-row mask.
        - Optionally fits per-column scalers on mask-restricted rows.

        Args:
            X: Exogenous features aligned to y. Series or DataFrame.
            y: Target series used only for alignment and masking.

        Returns:
            self

        Raises:
            ValueError: If X is missing or indices are invalid.
        """
        Xdf = ensure_dataframe(X, name="X")
        if Xdf is None:
            raise ValueError("Exogenous X required for ExogLagTransformer.fit")
        check_monotone_index(Xdf, "X")
        check_monotone_index(y, "y")
        if not Xdf.index.equals(y.index):
            common = Xdf.index.intersection(y.index)
            Xdf = Xdf.loc[common]
            y = y.loc[common]

        Xlag = self._lag_all(Xdf)
        mask = finite_mask_df(Xlag)

        self._mask = mask
        self._columns = list(Xdf.columns)
        self._fitted_index = Xdf.index

        if self.spec.scale:
            for col in Xlag.columns:
                sc = _Scaler()
                sc.fit(Xlag.loc[mask, col])
                self._scalers[col] = sc
        return self

    def transform(self, X: pd.Series | pd.DataFrame) -> pd.DataFrame:
        """
        Transform exogenous data by applying lag and optional scaling.

        Column names must match those observed at fit time. If a Series is passed,
        it is converted to a single-column DataFrame.

        Args:
            X: Exogenous features to transform.

        Returns:
            Lagged (and optionally standardized) DataFrame.

        Raises:
            RuntimeError: If called before `fit`.
            TypeError: If input type is unsupported.
            ValueError: If column names do not match fit-time columns.
        """
        if self._columns is None or self._mask is None:
            raise RuntimeError("Transformer not fit")

        Xdf = ensure_dataframe(X, name="X")
        if list(Xdf.columns) != self._columns:
            Xdf = Xdf.copy()
            Xdf.columns = self._columns

        Xlag = self._lag_all(Xdf)
        if self.spec.scale:
            for col, sc in self._scalers.items():
                Xlag[col] = sc.transform(Xlag[col])
        return Xlag

    def mask(self) -> pd.Series:
        """
        Return a copy of the boolean mask for rows valid after lagging.

        Returns:
            Boolean Series aligned to the fitted index where True marks rows
            with finite lagged exogenous values.

        Raises:
            RuntimeError: If called before `fit`.
        """
        if self._mask is None:
            raise RuntimeError("Transformer not fit")
        return self._mask.copy()

    def trim_target(self, y: pd.Series) -> pd.Series:
        """
        Trim the target to rows valid after lagging.

        Args:
            y: Target series aligned to the fitted index.

        Returns:
            Target restricted to rows where lagged exogenous values are finite.

        Raises:
            RuntimeError: If called before `fit`.
        """
        if self._mask is None:
            raise RuntimeError("Transformer not fit")
        return y.loc[self._mask]

    def future_block(
        self, X_full: pd.DataFrame, start_idx: int, steps: int
    ) -> pd.DataFrame:
        """
        Build the lagged+scaled exogenous design matrix for a forecast window.

        The returned block corresponds to positions [start_idx, start_idx + steps - 1]
        in the same positional alignment space used during training. The method will
        ensure there are enough rows to extract this window by **self-padding** with
        NaN rows if necessary before lagging. This enables no-peek evaluation when
        `steps <= delay`: all required lagged values resolve to historical raw X.

        Args:
            X_full: Exogenous DataFrame containing at least the historical portion and
                    optionally caller-provided future rows. Column names must match
                    those observed at fit time (order-insensitive; will be aligned).
            start_idx: Positional index of the first forecasted row.
            steps: Number of forecast steps.

        Returns:
            Lagged and scaled exogenous block of shape [steps, n_features].

        Raises:
            RuntimeError: If called before `fit`.
            ValueError: If column count or names do not match fit-time columns, or if
                        the requested block contains NaN/Inf due to insufficient history.
        """
        if self._columns is None:
            raise RuntimeError("Transformer not fit")

        Xdf = ensure_dataframe(X_full, name="X_full")
        if Xdf.shape[1] != len(self._columns):
            raise ValueError(
                f"Future exogenous column count mismatch. Expected {len(self._columns)}, got {Xdf.shape[1]}"
            )
        if list(Xdf.columns) != self._columns:
            Xdf = Xdf.copy()
            Xdf.columns = self._columns

        # Work in positional space; labels are irrelevant for forecasting exog blocks.
        Xpos = Xdf.reset_index(drop=True)

        needed_len = start_idx + steps
        if len(Xpos) < needed_len:
            pad_rows = needed_len - len(Xpos)
            pad = pd.DataFrame(np.nan, index=range(pad_rows), columns=Xpos.columns)
            Xpos = pd.concat([Xpos, pad], axis=0, ignore_index=True)

        # Lag after padding so positions [start_idx : start_idx+steps) exist.
        Xlag = self._lag_all(Xpos)

        if self.spec.scale:
            for col, sc in self._scalers.items():
                Xlag[col] = sc.transform(Xlag[col])

        block = Xlag.iloc[start_idx : start_idx + steps]

        # All values in the requested lagged block must be finite.
        if not np.all(np.isfinite(block.values)):
            raise ValueError(
                "future_block contains NaN/Inf - not enough history for lagged exog at these horizons"
            )
        return block
