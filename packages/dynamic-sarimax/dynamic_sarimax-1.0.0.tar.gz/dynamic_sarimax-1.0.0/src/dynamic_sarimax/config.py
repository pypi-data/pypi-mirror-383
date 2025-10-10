# src/dynamic_sarimax/config.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class SarimaxConfig:
    """
    Immutable configuration for SARIMAX model parameters.

    Attributes:
        order: Non-seasonal (p, d, q) order tuple.
        seasonal_order: Seasonal (P, D, Q, s) order tuple.
        trend: Trend specification.
               - "auto": selects "c" if d = D = 0, else "n".
               - "n": no trend term.
               - "c", "t", or "ct" as supported by statsmodels.
        enforce_stationarity: Whether to enforce stationarity in model estimation.
        enforce_invertibility: Whether to enforce invertibility in model estimation.

    Example:
        >>> cfg = SarimaxConfig(order=(1, 1, 1), seasonal_order=(0, 1, 1, 12))
        >>> cfg.materialize_trend()
        'n'
    """

    order: Tuple[int, int, int]
    seasonal_order: Tuple[int, int, int, int]
    trend: str | None = "auto"
    enforce_stationarity: bool = False
    enforce_invertibility: bool = False

    def materialize_trend(self) -> str:
        """
        Resolve the trend parameter to a concrete value.

        Returns:
            Resolved trend string according to:
              - "auto": returns "c" if d = D = 0, else "n".
              - None: returns "n".
              - Explicit value otherwise.

        Example:
            >>> SarimaxConfig((1, 0, 0), (0, 0, 0, 0)).materialize_trend()
            'c'
        """
        d = self.order[1]
        D = self.seasonal_order[1]
        # If automatic trend detection is enabled
        if self.trend == "auto":
            return "c" if (d == 0 and D == 0) else "n"
        # None explicitly disables trend
        return "n" if self.trend is None else self.trend


@dataclass(frozen=True)
class ExogLagSpec:
    """
    Specification for exogenous lagging behavior.

    Attributes:
        delay: Non-negative integer lag `b`. Defines how many steps the exogenous
               variable is shifted backward when aligning with the target series.
        scale: Whether to standardize exogenous values using training-period
               mean and standard deviation before fitting.

    Example:
        >>> ExogLagSpec(delay=1, scale=True)
        ExogLagSpec(delay=1, scale=True)
    """

    delay: int
    scale: bool = True
