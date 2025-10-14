"""
QuantJourney Technical-Indicators - Utils
=========================================
Utility helpers shared across the library for data validation, divergence/crossover
analysis, plotting, and memory optimization.

Author: Jakub Polec <jakub@quantjourney.pro>
License: MIT
"""
from __future__ import annotations

from typing import Dict, Tuple, List, Union
import numpy as np
import pandas as pd

from ._errors import InvalidInputError

import logging
import logging.handlers
from queue import Queue
import threading

logger = logging.getLogger(__name__)
queue = Queue()
queue_handler = logging.handlers.QueueHandler(queue)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
queue_handler.setFormatter(formatter)
logger.addHandler(queue_handler)
logger.setLevel(logging.INFO)

def process_queue():
    while True:
        record = queue.get()
        if record is None:
            break
        stream_handler.handle(record)

# Only start thread if not already running
if not any(t.name == 'quantjourney_queue_processor' for t in threading.enumerate()):
    queue_thread = threading.Thread(target=process_queue, daemon=True, name='quantjourney_queue_processor')
    queue_thread.start()

# Basic validators and helpers ---------------------------------------------------

# Helper for numeric index detection (avoid deprecated Index.is_numeric)
from pandas.api.types import is_numeric_dtype

def _is_numeric_index(idx: pd.Index) -> bool:
    try:
        return is_numeric_dtype(idx.dtype)
    except Exception:
        return False

def validate_data(
    data: Union[pd.DataFrame, pd.Series], 
    required_columns: List[str] | None = None,
    allow_gaps: bool = True,
    min_data_points: int = 2
) -> bool:
    """
    Validate input data with hedge fund friendly gap handling.

    Args:
        data: Input DataFrame or Series.
        required_columns: List of required column names (for DataFrame).
        allow_gaps: Allow non-monotonic data (for market holidays/gaps).
        min_data_points: Minimum required data points.

    Raises:
        InvalidInputError: If validation fails due to critical issues.

    Returns:
        bool: True if validation passes.
    """
    if data.empty:
        raise InvalidInputError(
            message="Input data is empty",
            context={"data_type": type(data).__name__}
        )
    
    if required_columns:
        if not isinstance(data, pd.DataFrame):
            raise InvalidInputError(
                message=f"Data must be a DataFrame with columns: {required_columns}",
                context={"required_columns": required_columns}
            )
        missing = [c for c in required_columns if c not in data.columns]
        if missing:
            raise InvalidInputError(
                message=f"Missing required columns: {missing}",
                context={"missing_columns": missing}
            )
        for col in required_columns:
            try:
                sel = data[col]
            except Exception:
                raise InvalidInputError(
                    message=f"Missing required column '{col}'",
                    context={"available_columns": list(data.columns)}
                )
            if isinstance(sel, pd.DataFrame):
                # MultiIndex column selection yields a sub-DataFrame (e.g., single ticker); ensure all numeric
                non_numeric = [str(dt) for dt in sel.dtypes.values if not np.issubdtype(dt, np.number)]
                if non_numeric:
                    raise InvalidInputError(
                        message=f"Column '{col}' must contain numeric data",
                        context={"column": col, "dtypes": non_numeric}
                    )
            else:
                if not np.issubdtype(sel.dtype, np.number):
                    raise InvalidInputError(
                        message=f"Column '{col}' must contain numeric data",
                        context={"column": col, "dtype": str(sel.dtype)}
                    )
    
    if len(data) < min_data_points:
        raise InvalidInputError(
            message=f"Data must contain at least {min_data_points} rows",
            context={"data_length": len(data), "required": min_data_points}
        )
    
    # Enhanced index validation for market data
    if not (isinstance(data.index, (pd.DatetimeIndex, pd.RangeIndex)) or _is_numeric_index(data.index)):
        raise InvalidInputError(
            message="Index must be datetime or numeric",
            context={"index_type": type(data.index).__name__}
        )
    
    # Relaxed monotonic check for market data
    if not allow_gaps and not data.index.is_monotonic_increasing:
        raise InvalidInputError(
            message="Index must be monotonically increasing (set allow_gaps=True for market data)",
            context={"index_head": str(data.index[:5])}
        )
    elif allow_gaps and isinstance(data.index, pd.DatetimeIndex):
        # Check for reasonable time ordering (allow some gaps)
        if len(data) > 1:
            time_diffs = data.index[1:] - data.index[:-1]
            negative_diffs = time_diffs < pd.Timedelta(0)
            if negative_diffs.sum() > len(data) * 0.1:  # Allow up to 10% out-of-order
                logger.warning(f"Found {negative_diffs.sum()} out-of-order timestamps")
    
    # Handle duplicates more gracefully
    if data.index.has_duplicates:
        dup_count = data.index.duplicated().sum()
        if dup_count > len(data) * 0.05:  # More than 5% duplicates is concerning
            raise InvalidInputError(
                message=f"Too many duplicate indices: {dup_count}",
                context={"duplicate_count": dup_count, "total_rows": len(data)}
            )
        else:
            logger.warning(f"Found {dup_count} duplicate indices - will be handled in calculations")
    
    # Enhanced NaN handling
    if data.isnull().any().any():
        if isinstance(data, pd.DataFrame):
            nan_cols = data.columns[data.isnull().any()].tolist()
            nan_pct = (data.isnull().sum() / len(data) * 100).round(2)
            logger.warning(f"Data contains NaN values in columns {nan_cols}: {nan_pct.to_dict()}%")
        else:
            nan_pct = data.isnull().sum() / len(data) * 100
            logger.warning(f"Data contains {nan_pct:.2f}% NaN values")
    
    return True

def validate_and_get_prices(
    data: Union[pd.Series, pd.DataFrame], price_col: str = "adj_close"
) -> pd.Series:
    """
    Return price series, falling back to 'close' column if needed, with index validation.

    Args:
        data: Input Series or DataFrame.
        price_col: Column name to extract (default: 'adj_close').

    Raises:
        InvalidInputError: If price column is missing, non-numeric, index is invalid, or data is empty.
        TypeError: If input is neither Series nor DataFrame.

    Returns:
        pandas.Series: Price data as a Series.
    """
    if isinstance(data, (pd.Series, pd.DataFrame)) and data.empty:
        raise InvalidInputError(
            message="Input data is empty",
            context={"data_type": type(data).__name__}
        )
    if isinstance(data, pd.Series):
        if not np.issubdtype(data.dtype, np.number):
            raise InvalidInputError(
                message="Series must contain numeric data",
                context={"dtype": str(data.dtype)}
            )
        if not (isinstance(data.index, pd.DatetimeIndex) or _is_numeric_index(data.index)):
            raise InvalidInputError(
                message="Index must be datetime or numeric",
                context={"index_type": type(data.index).__name__}
            )
        if not data.index.is_monotonic_increasing:
            raise InvalidInputError(
                message="Index must be monotonically increasing",
                context={"index_head": str(data.index[:5])}
            )
        if data.index.has_duplicates:
            raise InvalidInputError(
                message="Index contains duplicate values",
                context={"duplicate_indices": str(data.index[data.index.duplicated()])}
            )
        if data.isnull().any():
            logger.warning("Series contains NaN values; they will be handled in calculations")
        return data
    elif isinstance(data, pd.DataFrame):
        if price_col not in data.columns:
            if "close" in data.columns:
                price_col = "close"
            else:
                # If this is a single-column DataFrame (e.g., yfinance close selection
                # with MultiIndex reduced to one ticker), treat that column as prices.
                if data.shape[1] == 1 and np.issubdtype(data.iloc[:, 0].dtype, np.number):
                    series = data.iloc[:, 0]
                    # Validate index constraints for the series
                    if not (isinstance(series.index, pd.DatetimeIndex) or _is_numeric_index(series.index)):
                        raise InvalidInputError(
                            message="Index must be datetime or numeric",
                            context={"index_type": type(series.index).__name__}
                        )
                    if not series.index.is_monotonic_increasing:
                        raise InvalidInputError(
                            message="Index must be monotonically increasing",
                            context={"index_head": str(series.index[:5])}
                        )
                    if series.index.has_duplicates:
                        raise InvalidInputError(
                            message="Index contains duplicate values",
                            context={"duplicate_indices": str(series.index[series.index.duplicated()])}
                        )
                    if series.isnull().any():
                        logger.warning("Series contains NaN values; they will be handled in calculations")
                    return series
                raise InvalidInputError(
                    message=f"Neither '{price_col}' nor 'close' found in DataFrame",
                    context={"available_columns": list(data.columns)}
                )
        if not np.issubdtype(data[price_col].dtype, np.number):
            raise InvalidInputError(
                message=f"Column '{price_col}' must contain numeric data",
                context={"column": price_col, "dtype": str(data[price_col].dtype)}
            )
        if not (isinstance(data.index, pd.DatetimeIndex) or _is_numeric_index(data.index)):
            raise InvalidInputError(
                message="Index must be datetime or numeric",
                context={"index_type": type(data.index).__name__}
            )
        if not data.index.is_monotonic_increasing:
            raise InvalidInputError(
                message="Index must be monotonically increasing",
                context={"index_head": str(data.index[:5])}
            )
        if data.index.has_duplicates:
            raise InvalidInputError(
                message="Index contains duplicate values",
                context={"duplicate_indices": str(data.index[data.index.duplicated()])}
            )
        if data[price_col].isnull().any():
            logger.warning(f"Column '{price_col}' contains NaN values; they will be handled in calculations")
        return data[price_col]
    else:
        raise TypeError(
            f"Input must be pandas Series or DataFrame, got {type(data).__name__}"
        )

def validate_window(data_length: int, window: int, min_window: int = 2) -> bool:
    """
    Validate the window size for rolling calculations.

    Args:
        data_length: Length of the input data.
        window: Size of the rolling window.
        min_window: Minimum allowed window size (default: 2).

    Raises:
        InvalidInputError: If window size is too small or exceeds data length.

    Returns:
        bool: True if validation passes.
    """
    if window < min_window:
        raise InvalidInputError(
            message=f"Window size must be at least {min_window}",
            context={"window": window, "min_window": min_window}
        )
    if window >= data_length:
        raise InvalidInputError(
            message=f"Window size ({window}) must be less than data length ({data_length})",
            context={"window": window, "data_length": data_length}
        )
    return True

def detect_divergence(
    price: pd.Series, indicator: pd.Series, window: int = 20
) -> pd.DataFrame:
    """
    Detect bullish and bearish divergences between price and an indicator.

    Args:
        price: Price series.
        indicator: Indicator series.
        window: Lookback period for detecting divergences (default: 20).

    Raises:
        InvalidInputError: If price and indicator have different lengths or window is invalid.

    Returns:
        pandas.DataFrame: DataFrame with 'bullish' and 'bearish' columns indicating divergences (1 for detected, 0 otherwise).
    """
    if len(price) != len(indicator):
        raise InvalidInputError(
            message="Price and indicator must have the same length",
            context={"price_length": len(price), "indicator_length": len(indicator)}
        )
    if len(price) < window:
        raise InvalidInputError(
            message=f"Window size ({window}) must be less than data length ({len(price)})",
            context={"window": window, "data_length": len(price)}
        )
    validate_data(price)
    validate_data(indicator)
    out = pd.DataFrame(index=price.index).assign(bullish=0, bearish=0)
    for i in range(window, len(price)):
        price_win = price[i - window : i]
        ind_win = indicator[i - window : i]
        if price.iloc[i] < price_win.min() and indicator.iloc[i] > ind_win.min():
            out.iat[i, 0] = 1  # bullish
        if price.iloc[i] > price_win.max() and indicator.iloc[i] < ind_win.max():
            out.iat[i, 1] = 1  # bearish
    return out

def detect_crossovers(series1: pd.Series, series2: pd.Series) -> pd.DataFrame:
    """
    Detect bullish and bearish crossovers between two series.

    Args:
        series1: First series (e.g., fast moving average).
        series2: Second series (e.g., slow moving average).

    Raises:
        InvalidInputError: If series have different lengths.

    Returns:
        pandas.DataFrame: DataFrame with 'bullish' and 'bearish' columns indicating crossovers (1 for detected, 0 otherwise).
    """
    if len(series1) != len(series2):
        raise InvalidInputError(
            message="Series must be same length",
            context={"series1_length": len(series1), "series2_length": len(series2)}
        )
    validate_data(series1)
    validate_data(series2)
    diff = series1 - series2
    prev = diff.shift(1)
    # Bullish when diff crosses up through zero on current bar
    bullish = ((prev <= 0) & (diff > 0)).astype(int)
    bearish = ((prev >= 0) & (diff < 0)).astype(int)
    return pd.DataFrame({"bullish": bullish, "bearish": bearish}, index=series1.index)

# Plotting helper ------------------------------------------------------------

def plot_indicators(
    data: pd.DataFrame,
    indicators: Dict[str, pd.Series],
    title: str = "Technical Analysis",
    figsize: Tuple[int, int] = (15, 10),
    overlay: bool = False,
    price_col: str = "close",
    save_path: str | None = None 
) -> None:
    """
    Plot price data and indicators, either overlaid or in separate subplots.

    Args:
        data: DataFrame containing price data with a 'close' column (or specified price_col).
        indicators: Dictionary mapping indicator names to their Series.
        title: Plot title (default: "Technical Analysis").
        figsize: Figure size as (width, height) in inches (default: (15, 10)).
        overlay: If True, plot all indicators on the same axis as price; else use subplots (default: False).
        price_col: Column name for price data (default: 'close').
        save_path: Path to save the plot (default: None).

    Raises:
        InvalidInputError: If price column is missing or data/indicators are invalid.

    Returns:
        None: Displays the plot using Matplotlib.
    """
    validate_data(data, required_columns=[price_col])
    for name, series in indicators.items():
        validate_data(series)
        if not series.index.equals(data.index):
            raise InvalidInputError(
                message=f"Indicator '{name}' index must match data index",
                context={"indicator_name": name}
            )
    try:
        import matplotlib.pyplot as plt  # Optional heavy import
    except ImportError:
        logger.warning("Matplotlib is required for plotting")
        return

    if overlay:
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(data.index, data[price_col], label="Price", color="black")
        for name, series in indicators.items():
            ax.plot(data.index, series, label=name, alpha=0.7)
        ax.set_title(title)
        ax.grid(True)
        ax.legend()
    else:
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=figsize, height_ratios=[2, 1], sharex=True
        )
        ax1.plot(data.index, data[price_col], label="Price", color="black")
        for name, series in indicators.items():
            if "overlay" in name.lower():
                ax1.plot(data.index, series, label=name, alpha=0.7)
            else:
                ax2.plot(data.index, series, label=name, alpha=0.7)
        ax1.set_title(title)
        ax1.grid(True)
        ax1.legend()
        ax2.grid(True)
        ax2.legend()
    plt.tight_layout()
    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
        logger.info(f"Saved plot to {save_path}")
    else:
        plt.show()

def optimize_memory(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage by downcasting numeric columns.

    Args:
        df: Input DataFrame.

    Raises:
        InvalidInputError: If input is not a DataFrame.

    Returns:
        pandas.DataFrame: Optimized DataFrame with reduced memory usage.
    """
    if not isinstance(df, pd.DataFrame):
        raise InvalidInputError(
            message=f"Input must be a DataFrame, got {type(df).__name__}",
            context={"input_type": type(df).__name__}
        )
    numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    for col in df.select_dtypes(include=numerics).columns:
        kind = df[col].dtype.name
        if kind.startswith("int"):
            c_min, c_max = df[col].min(), df[col].max()
            if c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                df[col] = df[col].astype(np.int32)
        elif kind.startswith("float"):
            c_min, c_max = df[col].min(), df[col].max()
            if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                df[col] = df[col].astype(np.float32)
    return df

__all__ = [
    "validate_data",
    "validate_and_get_prices",
    "validate_window",
    "detect_divergence",
    "detect_crossovers",
    "plot_indicators",
    "optimize_memory",
]
