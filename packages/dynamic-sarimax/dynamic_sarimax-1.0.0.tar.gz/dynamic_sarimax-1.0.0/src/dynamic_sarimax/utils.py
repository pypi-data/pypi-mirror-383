# src/dynamic_sarimax/utils.py
from __future__ import annotations
import numpy as np
import pandas as pd


def ensure_series(
    x: pd.Series | pd.DataFrame | np.ndarray, name: str = "x"
) -> pd.Series:
    """
    Ensure the input is converted to a 1-D pandas Series.

    Args:
        x: Input array-like object (Series, single-column DataFrame, or 1-D ndarray).
        name: Variable name used in error messages.

    Returns:
        A pandas Series representation of the input.

    Raises:
        ValueError: If the input is multi-dimensional or has >1 column.
        TypeError: If the input type is unsupported.
    """
    if isinstance(x, pd.Series):
        return x
    if isinstance(x, pd.DataFrame):
        if x.shape[1] != 1:
            raise ValueError(f"{name} must be 1-D when passed here; got {x.shape}")
        return x.iloc[:, 0]
    if isinstance(x, np.ndarray):
        if x.ndim != 1:
            raise ValueError(f"{name} must be 1-D array; got shape {x.shape}")
        return pd.Series(x)
    raise TypeError(f"Unsupported type for {name}: {type(x)}")


def ensure_dataframe(
    X: pd.Series | pd.DataFrame | None, name: str = "X"
) -> pd.DataFrame | None:
    """
    Ensure the input is converted to a pandas DataFrame.

    Args:
        X: Input (Series, DataFrame, or None).
        name: Variable name used in error messages.

    Returns:
        DataFrame representation of X, or None if X is None.

    Raises:
        TypeError: If input type is unsupported.
    """
    if X is None:
        return None
    if isinstance(X, pd.DataFrame):
        return X
    if isinstance(X, pd.Series):
        col = X.name if (X.name is not None and X.name != 0) else "exog"
        return X.to_frame(name=col)
    raise TypeError(f"Unsupported type for {name}: {type(X)}")


def check_monotone_index(obj: pd.Series | pd.DataFrame, name: str) -> None:
    """
    Validate that the index of a Series or DataFrame is strictly monotone increasing
    and free of duplicates.

    Args:
        obj: Series or DataFrame to validate.
        name: Variable name used in error messages.

    Raises:
        ValueError: If index is non-monotonic or contains duplicates.
    """
    idx = obj.index
    if not idx.is_monotonic_increasing:
        raise ValueError(f"{name} index must be monotone increasing")
    if idx.has_duplicates:
        raise ValueError(f"{name} index has duplicates")


def safe_shift(s: pd.Series, b: int) -> pd.Series:
    """
    Safely shift a Series backward by a non-negative delay.

    Args:
        s: Input Series.
        b: Non-negative integer shift (delay).

    Returns:
        Shifted Series.

    Raises:
        ValueError: If b < 0.
    """
    if b < 0:
        raise ValueError("delay must be >= 0")
    return s.shift(b)


def finite_mask_df(df: pd.DataFrame) -> pd.Series:
    """
    Compute a boolean mask identifying rows with all finite (non-NaN, non-inf) values.

    Args:
        df: Input DataFrame.

    Returns:
        Boolean Series aligned to df.index, True where all entries are finite.
    """
    m = np.all(np.isfinite(df.values), axis=1)
    return pd.Series(m, index=df.index)
