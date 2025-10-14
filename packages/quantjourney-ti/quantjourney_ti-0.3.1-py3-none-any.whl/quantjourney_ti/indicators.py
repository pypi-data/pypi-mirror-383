"""
QuantJourney Technical-Indicators - Indicators
==============================================
This module provides the *public* API class ``TechnicalIndicators`` while
delegating:

• numerically heavy kernels   →   :pymod:`quantjourney_ti._indicator_kernels`
• data-validation / plotting   →   :pymod:`quantjourney_ti._utils`
• decorators                  →   :pymod:`quantjourney_ti._decorators`

The separation keeps each concern isolated yet retains full backward
compatibility: all indicator methods (`SMA`, `RSI`, `MACD`, …) behave exactly
as they did in the original monolithic implementation, only faster and with a
cleaner internal structure.

Originally developed as part of the
`QuantJourney project <https://quantjourney.substack.com>`_ by
`Jakub Polec <https://www.linkedin.com/in/jakubpolec/>`_, the code is now
released under the MIT License as part of the **Quantitative Infrastructure**
initiative—free for anyone to use, fork and extend.

Example usage
-------------
Flat helpers (quick one-liners):::

    import quantjourney_ti as ti
    df["sma"] = ti.sma(df["close"], 20)

Full flexibility via the class::

    from quantjourney_ti import TechnicalIndicators
    ti = TechnicalIndicators()
    df["atr"] = ti.ATR(ohlc_df, 14)

Power-user shortcut (shared singleton)::

    import quantjourney_ti.indicators as ind
    ind._TI_INSTANCE.ATR(ohlc_df, 14)  # same object, no extra compile

Author: Jakub Polec  <jakub@quantjourney.pro>
License: MIT
"""

from __future__ import annotations

from typing import List, Dict, Union, Optional, Any
import numpy as np
import pandas as pd
from importlib import import_module
from types import ModuleType
from collections import OrderedDict
import threading

import logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Default to a simple stream handler; opt-in queue logging via start_logging_queue()
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)

def start_logging_queue() -> None:
    """Optionally enable thread-safe queue logging to stdout.

    This avoids starting background threads at import time. Call this only if your
    application benefits from a QueueHandler.
    """
    import logging.handlers
    from queue import Queue
    import threading

    if any(t.name == 'quantjourney_indicators_processor' for t in threading.enumerate()):
        return

    queue = Queue()
    qh = logging.handlers.QueueHandler(queue)
    sh = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    qh.setFormatter(fmt)
    sh.setFormatter(fmt)
    # Switch to queue-based logging: remove existing non-queue handlers first
    for h in list(logger.handlers):
        if not isinstance(h, logging.handlers.QueueHandler):
            logger.removeHandler(h)
    logger.addHandler(qh)

    def _process():
        while True:
            rec = queue.get()
            if rec is None:
                break
            sh.handle(rec)

    th = threading.Thread(target=_process, daemon=True, name='quantjourney_indicators_processor')
    th.start()

from ._utils import *
from ._decorators import numba_fallback
from ._risk_metrics import calculate_risk_metrics
from ._performance import cached_indicator, profile_performance
from ._streaming import StreamingIndicators

# Kernels are attached dynamically at the end from _indicator_kernels


class TechnicalIndicators:
    """
    High-performance technical indicators implementation with Numba optimization.

    Provides methods for:
    - Supportive utilities (data validation, price extraction, plotting)
    - Private calculation methods (optimized with Numba)
    - Public indicator methods (e.g., SMA, EMA, RSI)

    Many methods use Numba for performance but fall back to pandas or numpy if Numba fails,
    with warnings logged for debugging.
    """

    def __init__(self, warmup: bool = False):
        """
        Initialize the TechnicalIndicators class.

        Ensures Numba kernels are JIT-compiled by calling them with dummy data.
        """
        if warmup:
            self.warmup()

    def warmup(self) -> None:
        """Compile a representative subset of kernels eagerly."""
        dummy_array = np.ones(10, dtype=np.float64)
        self._calculate_sma_numba(dummy_array, 5)
        self._calculate_ema_numba(dummy_array, 5)
        self._calculate_rsi_numba(dummy_array, 5)
        self._calculate_macd_numba(dummy_array, 5, 5, 5)
        self._calculate_bollinger_bands_numba(dummy_array, 5, 5)
        self._calculate_roc_numba(dummy_array, 5)

    def _sma_fallback(self, data: Union[pd.Series, pd.DataFrame], period: int = 20) -> pd.Series:
        """Fallback calculation for SMA using numpy."""
        prices = self._validate_and_get_prices(data)
        prices_np = prices.values
        sma = np.full_like(prices_np, np.nan)
        for i in range(period - 1, len(prices_np)):
            if not np.any(np.isnan(prices_np[i - period + 1:i + 1])):
                sma[i] = np.mean(prices_np[i - period + 1:i + 1])
        return pd.Series(sma, index=prices.index, name=f"SMA_{period}")

    @cached_indicator(ttl_seconds=3600)
    @numba_fallback(_sma_fallback)
    def SMA(self, data: Union[pd.Series, pd.DataFrame], period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average.

        Uses Numba for performance but falls back to numpy if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for the moving average (default: 20).

        Returns:
            pandas Series with SMA values.
        """
        prices = self._validate_and_get_prices(data)
        prices_np = np.ascontiguousarray(prices.values, dtype=np.float64)
        sma = self._calculate_sma_numba(prices_np, period)
        return pd.Series(sma, index=prices.index, name=f"SMA_{period}")

    def _ema_fallback(self, data: Union[pd.Series, pd.DataFrame], period: int = 20) -> pd.Series:
        """Fallback calculation for EMA using pandas."""
        prices = self._validate_and_get_prices(data)
        return prices.ewm(span=period, adjust=False).mean().rename(f"EMA_{period}")

    @numba_fallback(_ema_fallback)
    def EMA(self, data: Union[pd.Series, pd.DataFrame], period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for the moving average (default: 20).

        Returns:
            pandas Series with EMA values.
        """
        prices = self._validate_and_get_prices(data)
        prices_np = np.ascontiguousarray(prices.values, dtype=np.float64)
        ema = self._calculate_ema_numba(prices_np, period)
        return pd.Series(ema, index=prices.index, name=f"EMA_{period}")

    def _rsi_fallback(self, data: pd.Series, period: int = 14) -> pd.Series:
        """Fallback calculation for RSI using pandas."""
        prices = self._validate_and_get_prices(data)
        deltas = prices.diff()
        gain = deltas.where(deltas > 0, 0).rolling(window=period).mean()
        loss = (-deltas.where(deltas < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.rename(f"RSI_{period}")

    @numba_fallback(_rsi_fallback)
    def RSI(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for RSI calculation (default: 14).

        Returns:
            pandas Series with RSI values.
        """
        prices = self._validate_and_get_prices(data)
        prices_np = np.ascontiguousarray(prices.values, dtype=np.float64)
        rsi = self._calculate_rsi_numba(prices_np, period)
        return pd.Series(rsi, index=prices.index, name=f"RSI_{period}")

    def _macd_fallback(
        self,
        data: Union[pd.Series, pd.DataFrame],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> pd.DataFrame:
        """Fallback calculation for MACD using pandas."""
        prices = self._validate_and_get_prices(data)
        fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
        slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal
        return pd.DataFrame(
            {
                "MACD": macd,
                "Signal": signal,
                "Histogram": histogram,
            },
            index=prices.index,
        )

    @numba_fallback(_macd_fallback)
    def MACD(
        self,
        data: Union[pd.Series, pd.DataFrame],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> pd.DataFrame:
        """
        Calculate MACD, Signal Line, and Histogram.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            fast_period: Period for fast EMA (default: 12).
            slow_period: Period for slow EMA (default: 26).
            signal_period: Period for signal line (default: 9).

        Returns:
            pandas DataFrame with MACD, Signal, and Histogram columns.
        """
        prices = self._validate_and_get_prices(data)
        prices_np = np.ascontiguousarray(prices.values, dtype=np.float64)
        macd_line, signal_line, histogram = self._calculate_macd_numba(
            prices_np, fast_period, slow_period, signal_period
        )
        macd_series = pd.Series(macd_line, index=prices.index, name="MACD")
        signal_series = pd.Series(signal_line, index=prices.index, name="Signal")
        histogram_series = pd.Series(histogram, index=prices.index, name="Histogram")
        return pd.DataFrame(
            {
                "MACD": macd_series,
                "Signal": signal_series,
                "Histogram": histogram_series,
            }
        )

    def _bb_fallback(
        self,
        data: Union[pd.Series, pd.DataFrame],
        period: int = 20,
        num_std: float = 2.0,
    ) -> pd.DataFrame:
        """Fallback calculation for Bollinger Bands using pandas."""
        prices = self._validate_and_get_prices(data)
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + num_std * std
        lower = middle - num_std * std
        return pd.DataFrame(
            {
                "BB_Upper": upper,
                "BB_Middle": middle,
                "BB_Lower": lower,
            },
            index=prices.index,
        )

    @numba_fallback(_bb_fallback)
    def BB(
        self,
        data: Union[pd.Series, pd.DataFrame],
        period: int = 20,
        num_std: float = 2.0,
    ) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for the moving average (default: 20).
            num_std: Number of standard deviations for bands (default: 2.0).

        Returns:
            pandas DataFrame with BB_Upper, BB_Middle, and BB_Lower columns.
        """
        prices = self._validate_and_get_prices(data)
        prices_np = np.ascontiguousarray(prices.values, dtype=np.float64)
        upper, middle, lower = self._calculate_bollinger_bands_numba(
            prices_np, period, num_std
        )
        upper_series = pd.Series(upper, index=prices.index, name="BB_Upper")
        middle_series = pd.Series(middle, index=prices.index, name="BB_Middle")
        lower_series = pd.Series(lower, index=prices.index, name="BB_Lower")
        return pd.DataFrame(
            {
                "BB_Upper": upper_series,
                "BB_Middle": middle_series,
                "BB_Lower": lower_series,
            }
        )

    def _atr_fallback(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Fallback calculation for ATR using pandas."""
        self._validate_data(data, ["high", "low", "close"])
        tr = pd.DataFrame(index=data.index)
        tr["hl"] = data["high"] - data["low"]
        tr["hc"] = (data["high"] - data["close"].shift(1)).abs()
        tr["lc"] = (data["low"] - data["close"].shift(1)).abs()
        tr = tr.max(axis=1)
        return tr.rolling(window=period).mean().rename(f"ATR_{period}")

    @numba_fallback(_atr_fallback)
    def ATR(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            period: Number of periods for ATR calculation (default: 14).

        Returns:
            pandas Series with ATR values.
        """
        self._validate_data(data, ["high", "low", "close"])
        high_np = np.ascontiguousarray(data["high"].values, dtype=np.float64)
        low_np = np.ascontiguousarray(data["low"].values, dtype=np.float64)
        close_np = np.ascontiguousarray(data["close"].values, dtype=np.float64)
        atr = self._calculate_atr_numba(high_np, low_np, close_np, period)
        return pd.Series(atr, index=data.index, name=f"ATR_{period}")

    def _stoch_fallback(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """Fallback calculation for Stochastic Oscillator using Pandas."""
        self._validate_data(data, ["high", "low", "close"])
        high_roll = data["high"].rolling(window=k_period).max()
        low_roll = data["low"].rolling(window=k_period).min()
        k_line = ((data["close"] - low_roll) / (high_roll - low_roll).replace(0, np.nan)) * 100
        d_line = k_line.rolling(window=d_period).mean()
        k_line.iloc[:k_period - 1] = np.nan
        d_line.iloc[:k_period + d_period - 2] = np.nan
        return pd.DataFrame({"K": k_line, "D": d_line}, index=data.index)

    @numba_fallback(_stoch_fallback)
    def STOCH(
        self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3
    ) -> pd.DataFrame:
        """
        Calculate Stochastic Oscillator.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            k_period: Period for %K calculation (default: 14).
            d_period: Period for %D calculation (default: 3).

        Returns:
            pandas DataFrame with K and D columns.
        """
        self._validate_data(data, ["high", "low", "close"])
        k_line, d_line = self._calculate_stochastic_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            k_period,
            d_period,
        )
        k_line[: k_period - 1] = np.nan
        d_line[: k_period + d_period - 2] = np.nan
        return pd.DataFrame({"K": k_line, "D": d_line}, index=data.index)

    def _adx_fallback(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Fallback calculation for ADX using Pandas."""
        self._validate_data(data, ["high", "low", "close"])
        tr = pd.DataFrame(index=data.index)
        tr["hl"] = data["high"] - data["low"]
        tr["hc"] = (data["high"] - data["close"].shift(1)).abs()
        tr["lc"] = (data["low"] - data["close"].shift(1)).abs()
        tr = tr.max(axis=1)
        plus_dm = (data["high"] - data["high"].shift(1)).where(
            (data["high"] - data["high"].shift(1)) > (data["low"].shift(1) - data["low"]), 0
        )
        minus_dm = (data["low"].shift(1) - data["low"]).where(
            (data["low"].shift(1) - data["low"]) > (data["high"] - data["high"].shift(1)), 0
        )
        smoothed_tr = tr.rolling(window=period).mean()
        smoothed_plus_dm = plus_dm.rolling(window=period).mean()
        smoothed_minus_dm = minus_dm.rolling(window=period).mean()
        plus_di = (smoothed_plus_dm / smoothed_tr) * 100
        minus_di = (smoothed_minus_dm / smoothed_tr) * 100
        dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
        adx = dx.rolling(window=period).mean()
        adx.iloc[:2 * period - 1] = np.nan
        plus_di.iloc[:period] = np.nan
        minus_di.iloc[:period] = np.nan
        return pd.DataFrame({"ADX": adx, "+DI": plus_di, "-DI": minus_di}, index=data.index)

    @numba_fallback(_adx_fallback)
    def ADX(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Average Directional Index.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            period: Number of periods for ADX calculation (default: 14).

        Returns:
            pandas DataFrame with ADX, +DI, and -DI columns.
        """
        self._validate_data(data, ["high", "low", "close"])
        adx, plus_di, minus_di = self._calculate_adx_numba(
            data["high"].values, data["low"].values, data["close"].values, period
        )
        adx[: 2 * period - 1] = np.nan
        plus_di[:period] = np.nan
        minus_di[:period] = np.nan
        return pd.DataFrame(
            {"ADX": adx, "+DI": plus_di, "-DI": minus_di}, index=data.index
        )

    @numba_fallback(lambda self, data, tenkan_period, kijun_period, senkou_span_b_period, displacement: pd.DataFrame(
        {"Tenkan-sen": np.nan, "Kijun-sen": np.nan, "Senkou Span A": np.nan, "Senkou Span B": np.nan, "Chikou Span": np.nan}, index=data.index))
    def ICHIMOKU(
        self,
        data: pd.DataFrame,
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_span_b_period: int = 52,
        displacement: int = 26,
    ) -> pd.DataFrame:
        """
        Calculate Ichimoku Cloud components.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        The Ichimoku Cloud consists of five lines:
        - Tenkan-sen: Short-term trend indicator (9-period high/low average).
        - Kijun-sen: Medium-term trend indicator (26-period high/low average).
        - Senkou Span A: Leading span (average of Tenkan and Kijun, shifted forward).
        - Senkou Span B: Long-term trend indicator (52-period high/low average, shifted forward).
        - Chikou Span: Lagging span (close price shifted backward).

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            tenkan_period: Period for Tenkan-sen (default: 9).
            kijun_period: Period for Kijun-sen (default: 26).
            senkou_span_b_period: Period for Senkou Span B (default: 52).
            displacement: Forward shift for Senkou Spans (default: 26).

        Returns:
            pandas.DataFrame: DataFrame with columns 'Tenkan-sen', 'Kijun-sen', 
                            'Senkou Span A', 'Senkou Span B', and 'Chikou Span'.
        """
        self._validate_data(data, ["high", "low", "close"])
        tenkan, kijun, senkou_a, senkou_b = self._calculate_ichimoku_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            tenkan_period,
            kijun_period,
            senkou_span_b_period,
        )
        tenkan[: tenkan_period - 1] = np.nan
        kijun[: kijun_period - 1] = np.nan
        senkou_a[: kijun_period - 1] = np.nan
        senkou_b[: senkou_span_b_period - 1] = np.nan
        senkou_a = pd.Series(senkou_a, index=data.index).shift(displacement)
        senkou_b = pd.Series(senkou_b, index=data.index).shift(displacement)
        chikou_span = data["close"].shift(-displacement)
        chikou_span.iloc[-displacement:] = np.nan
        return pd.DataFrame(
            {
                "Tenkan-sen": tenkan,
                "Kijun-sen": kijun,
                "Senkou Span A": senkou_a,
                "Senkou Span B": senkou_b,
                "Chikou Span": chikou_span,
            },
            index=data.index,
        )

    @numba_fallback(lambda self, data, ema_period, atr_period, multiplier: pd.DataFrame(
        {"KC_Upper": np.nan, "KC_Middle": np.nan, "KC_Lower": np.nan}, index=data.index))
    def KELTNER(
        self,
        data: pd.DataFrame,
        ema_period: int = 20,
        atr_period: int = 10,
        multiplier: float = 2.0,
    ) -> pd.DataFrame:
        """
        Calculate Keltner Channels.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            ema_period: Period for EMA (default: 20).
            atr_period: Period for ATR (default: 10).
            multiplier: Multiplier for ATR (default: 2.0).

        Returns:
            pandas DataFrame with KC_Upper, KC_Middle, and KC_Lower columns.
        """
        self._validate_data(data, ["high", "low", "close"])
        upper, middle, lower = self._calculate_keltner_channels_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            ema_period,
            atr_period,
            multiplier,
        )
        upper[: ema_period - 1] = np.nan
        middle[: ema_period - 1] = np.nan
        lower[: ema_period - 1] = np.nan
        return pd.DataFrame(
            {"KC_Upper": upper, "KC_Middle": middle, "KC_Lower": lower},
            index=data.index,
        )

    def _mfi_fallback(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Fallback calculation for MFI using Pandas."""
        self._validate_data(data, ["high", "low", "close", "volume"])
        typical_price = (data["high"] + data["low"] + data["close"]) / 3
        money_flow = typical_price * data["volume"]
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        positive_sum = positive_flow.rolling(window=period).sum()
        negative_sum = negative_flow.rolling(window=period).sum()
        money_ratio = positive_sum / negative_sum.replace(0, np.nan)
        mfi = 100 - (100 / (1 + money_ratio))
        mfi.iloc[:period - 1] = np.nan
        return mfi.rename(f"MFI_{period}")
    
    @numba_fallback(_mfi_fallback)
    def MFI(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Money Flow Index.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close', 'volume' columns.
            period: Number of periods for MFI calculation (default: 14).

        Returns:
            pandas Series with MFI values.
        """
        self._validate_data(data, ["high", "low", "close", "volume"])
        mfi = self._calculate_mfi_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            data["volume"].values,
            period,
        )
        mfi[: period - 1] = np.nan
        return pd.Series(mfi, index=data.index, name=f"MFI_{period}")

    def _trix_fallback(self, data: Union[pd.Series, pd.DataFrame], period: int = 15) -> pd.Series:
        """Fallback calculation for TRIX using pandas."""
        prices = self._validate_and_get_prices(data)
        ema1 = prices.ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        ema3 = ema2.ewm(span=period, adjust=False).mean()
        trix = ema3.pct_change() * 100
        return trix.rename(f"TRIX_{period}")

    @numba_fallback(_trix_fallback)
    def TRIX(self, data: Union[pd.Series, pd.DataFrame], period: int = 15) -> pd.Series:
        """
        Calculate TRIX indicator.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for TRIX calculation (default: 15).

        Returns:
            pandas Series with TRIX values.
        """
        prices = self._validate_and_get_prices(data)
        trix = self._calculate_trix_numba(prices.values, period)
        trix[: period - 1] = np.nan
        return pd.Series(trix, index=prices.index, name=f"TRIX_{period}")

    def _cci_fallback(self, data: pd.DataFrame, period: int = 20, constant: float = 0.015) -> pd.Series:
        """Fallback calculation for CCI using Pandas."""
        self._validate_data(data, ["high", "low", "close"])
        typical_price = (data["high"] + data["low"] + data["close"]) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mean_deviation = typical_price.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
        )
        cci = (typical_price - sma_tp) / (constant * mean_deviation.replace(0, np.nan))
        cci.iloc[:period - 1] = np.nan
        return cci.rename(f"CCI_{period}")

    @numba_fallback(_cci_fallback)
    def CCI(
        self, data: pd.DataFrame, period: int = 20, constant: float = 0.015
    ) -> pd.Series:
        """
        Calculate Commodity Channel Index.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            period: Number of periods for CCI calculation (default: 20).
            constant: Scaling constant (default: 0.015).

        Returns:
            pandas Series with CCI values.
        """
        self._validate_data(data, ["high", "low", "close"])
        high_np = np.ascontiguousarray(data["high"].values, dtype=np.float64)
        low_np = np.ascontiguousarray(data["low"].values, dtype=np.float64)
        close_np = np.ascontiguousarray(data["close"].values, dtype=np.float64)
        cci = self._calculate_cci_numba(high_np, low_np, close_np, period, constant)
        cci[: period - 1] = np.nan
        return pd.Series(cci, index=data.index, name=f"CCI_{period}")

    def _roc_fallback(self, data: Union[pd.Series, pd.DataFrame], period: int = 12) -> pd.Series:
        """Fallback calculation for ROC using pandas."""
        prices = self._validate_and_get_prices(data)
        roc = prices.pct_change(periods=period) * 100
        return roc.rename(f"ROC_{period}")

    @numba_fallback(_roc_fallback)
    def ROC(self, data: Union[pd.Series, pd.DataFrame], period: int = 12) -> pd.Series:
        """
        Calculate Rate of Change.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for ROC calculation (default: 12).

        Returns:
            pandas Series with ROC values.
        """
        prices = self._validate_and_get_prices(data)
        roc = self._calculate_roc_numba(prices.values, period)
        roc[:period] = np.nan
        return pd.Series(roc, index=prices.index, name=f"ROC_{period}")

    def _willr_fallback(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Fallback calculation for Williams %R using Pandas."""
        self._validate_data(data, ["high", "low", "close"])
        high_roll = data["high"].rolling(window=period).max()
        low_roll = data["low"].rolling(window=period).min()
        willr = ((high_roll - data["close"]) / (high_roll - low_roll).replace(0, np.nan)) * -100
        willr.iloc[:period - 1] = np.nan
        return willr.rename(f"WILLR_{period}")
    
    @numba_fallback(_willr_fallback)
    def WILLR(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Williams %R.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            period: Number of periods for Williams %R calculation (default: 14).

        Returns:
            pandas Series with Williams %R values.
        """
        self._validate_data(data, ["high", "low", "close"])
        high_np = np.ascontiguousarray(data["high"].values, dtype=np.float64)
        low_np = np.ascontiguousarray(data["low"].values, dtype=np.float64)
        close_np = np.ascontiguousarray(data["close"].values, dtype=np.float64)
        willr = self._calculate_willr_numba(high_np, low_np, close_np, period)
        willr[: period - 1] = np.nan
        return pd.Series(willr, index=data.index, name=f"WILLR_{period}")

    def _dema_fallback(self, data: Union[pd.Series, pd.DataFrame], period: int = 20) -> pd.Series:
        """Fallback calculation for DEMA using pandas."""
        prices = self._validate_and_get_prices(data)
        ema1 = prices.ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        dema = 2 * ema1 - ema2
        return dema.rename(f"DEMA_{period}")

    @numba_fallback(_dema_fallback)
    def DEMA(self, data: Union[pd.Series, pd.DataFrame], period: int = 20) -> pd.Series:
        """
        Calculate Double Exponential Moving Average.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for DEMA calculation (default: 20).

        Returns:
            pandas Series with DEMA values.
        """
        prices = self._validate_and_get_prices(data)
        dema = self._calculate_dema_numba(prices.values, period)
        dema[: period - 1] = np.nan
        return pd.Series(dema, index=prices.index, name=f"DEMA_{period}")

    # Hedge Fund Specific Methods ===============================================
    
    @cached_indicator(ttl_seconds=1800)  # 30 minute cache
    def RISK_METRICS(
        self, 
        data: Union[pd.Series, pd.DataFrame],
        benchmark: Optional[pd.Series] = None,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252,
        confidence_level: float = 0.05
    ) -> pd.Series:
        """
        Calculate comprehensive risk metrics for hedge fund analysis.
        
        Args:
            data: Price or return series
            benchmark: Benchmark series for relative metrics
            risk_free_rate: Annual risk-free rate (default: 2%)
            periods_per_year: Trading periods per year (default: 252)
            confidence_level: Confidence level for VaR/CVaR (default: 5%)
        
        Returns:
            Series with calculated risk metrics including Sharpe, Sortino, VaR, etc.
        """
        return calculate_risk_metrics(
            data=data,
            benchmark=benchmark,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
            confidence_level=confidence_level
        )
    
    def create_streaming_indicators(self, max_buffer_size: int = 1000) -> StreamingIndicators:
        """
        Create a streaming indicators instance for real-time processing.
        
        Args:
            max_buffer_size: Maximum number of historical values to keep
            
        Returns:
            StreamingIndicators instance
        """
        return StreamingIndicators(max_buffer_size=max_buffer_size)
    
    @profile_performance(include_memory=True)
    def batch_calculate(
        self, 
        data_dict: Dict[str, pd.DataFrame], 
        indicator_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate indicators for multiple symbols efficiently.
        
        Args:
            data_dict: Dictionary of symbol -> DataFrame
            indicator_name: Name of indicator method to call
            **kwargs: Arguments for indicator function
            
        Returns:
            Dictionary of symbol -> indicator results
        """
        from ._performance import BatchProcessor
        
        processor = BatchProcessor()
        indicator_func = getattr(self, indicator_name.upper())
        
        return processor.process_symbols(data_dict, indicator_func, **kwargs)
    
    def validate_market_data(
        self, 
        data: Union[pd.DataFrame, pd.Series],
        allow_gaps: bool = True,
        fix_common_issues: bool = True
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Validate and optionally fix common market data issues.
        
        Args:
            data: Market data to validate
            allow_gaps: Allow gaps in data (holidays, etc.)
            fix_common_issues: Attempt to fix common data issues
            
        Returns:
            Validated (and optionally fixed) data
        """
        # Use enhanced validation
        validate_data(data, allow_gaps=allow_gaps)
        
        if not fix_common_issues:
            return data
        
        # Fix common issues
        fixed_data = data.copy()
        
        if isinstance(fixed_data, pd.DataFrame):
            # Handle zero volume (treat zeros as missing, then forward-fill)
            if 'volume' in fixed_data.columns:
                fixed_data['volume'] = fixed_data['volume'].replace(0, np.nan).ffill()
            
            # Forward fill small gaps (limit to 3 consecutive NaNs) for numeric columns
            from pandas.api.types import is_any_real_numeric_dtype
            for col in fixed_data.columns:
                if is_any_real_numeric_dtype(fixed_data[col]):
                    fixed_data[col] = fixed_data[col].ffill(limit=3)

        return fixed_data

    def _kama_fallback(
        self,
        data: Union[pd.Series, pd.DataFrame],
        er_period: int = 10,
        fast_period: int = 2,
        slow_period: int = 30,
    ) -> pd.Series:
        """Fallback calculation for KAMA using pandas."""
        prices = self._validate_and_get_prices(data)
        if len(prices) == 0:
            return pd.Series([], dtype=float, name=f"KAMA_{er_period}")
        # If insufficient data for er_period, return all-NaN series
        if len(prices) <= er_period:
            return pd.Series(np.full(len(prices), np.nan), index=prices.index, name=f"KAMA_{er_period}")

        change = prices.diff(er_period).abs()
        volatility = prices.diff().abs().rolling(window=er_period).sum()
        er = change / volatility
        er = er.replace([np.inf, -np.inf], 0.0).fillna(0.0)
        fast_alpha = 2.0 / (fast_period + 1)
        slow_alpha = 2.0 / (slow_period + 1)
        sc = (er * (fast_alpha - slow_alpha) + slow_alpha) ** 2
        kama = np.full(len(prices), np.nan)
        kama[er_period] = prices.iloc[er_period] if not pd.isna(prices.iloc[er_period]) else np.nan
        for i in range(er_period + 1, len(prices)):
                # update only when prior KAMA and current price/sc are valid
            if not pd.isna(prices.iloc[i]) and not np.isnan(kama[i - 1]) and not pd.isna(sc.iloc[i]):
                kama[i] = kama[i - 1] + sc.iloc[i] * (prices.iloc[i] - kama[i - 1])
        return pd.Series(kama, index=prices.index, name=f"KAMA_{er_period}")

    @numba_fallback(_kama_fallback)
    def KAMA(
        self,
        data: Union[pd.Series, pd.DataFrame],
        er_period: int = 10,
        fast_period: int = 2,
        slow_period: int = 30,
    ) -> pd.Series:
        """
        Calculate Kaufman Adaptive Moving Average.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            er_period: Period for efficiency ratio (default: 10).
            fast_period: Period for fast EMA (default: 2).
            slow_period: Period for slow EMA (default: 30).

        Returns:
            pandas Series with KAMA values.
        """
        prices = self._validate_and_get_prices(data)
        kama = self._calculate_kama_numba(
            prices.values, er_period, fast_period, slow_period
        )
        kama[: er_period - 1] = np.nan
        return pd.Series(kama, index=prices.index, name=f"KAMA_{er_period}")

    def _donchian_fallback(self, data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Fallback calculation for Donchian Channels using Pandas."""
        self._validate_data(data, ["high", "low"])
        upper = data["high"].rolling(window=period).max()
        lower = data["low"].rolling(window=period).min()
        middle = (upper + lower) / 2
        upper.iloc[:period - 1] = np.nan
        middle.iloc[:period - 1] = np.nan
        lower.iloc[:period - 1] = np.nan
        return pd.DataFrame({"DC_Upper": upper, "DC_Middle": middle, "DC_Lower": lower}, index=data.index)
    
    @numba_fallback(_donchian_fallback)
    def DONCHIAN(self, data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calculate Donchian Channels.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low' columns.
            period: Number of periods for Donchian Channels (default: 20).

        Returns:
            pandas DataFrame with DC_Upper, DC_Middle, and DC_Lower columns.
        """
        self._validate_data(data, ["high", "low"])
        upper, middle, lower = self._calculate_donchian_channels_numba(
            data["high"].values, data["low"].values, period
        )
        upper[: period - 1] = np.nan
        middle[: period - 1] = np.nan
        lower[: period - 1] = np.nan
        return pd.DataFrame(
            {"DC_Upper": upper, "DC_Middle": middle, "DC_Lower": lower},
            index=data.index,
        )

    @numba_fallback(lambda self, data, period: pd.DataFrame(
        {"AROON_UP": np.nan, "AROON_DOWN": np.nan, "AROON_OSC": np.nan}, index=data.index))
    def AROON(self, data: pd.DataFrame, period: int = 25) -> pd.DataFrame:
        """
        Calculate Aroon Indicator.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low' columns.
            period: Number of periods for Aroon calculation (default: 25).

        Returns:
            pandas DataFrame with AROON_UP, AROON_DOWN, and AROON_OSC columns.
        """
        self._validate_data(data, ["high", "low"])
        aroon_up, aroon_down = self._calculate_aroon_numba(
            data["high"].values, data["low"].values, period
        )
        aroon_up[: period - 1] = np.nan
        aroon_down[: period - 1] = np.nan
        aroon_osc = aroon_up - aroon_down
        return pd.DataFrame(
            {"AROON_UP": aroon_up, "AROON_DOWN": aroon_down, "AROON_OSC": aroon_osc},
            index=data.index,
        )

    @numba_fallback(lambda self, data, short_period, long_period: pd.Series(np.nan, index=data.index, name="AO"))
    def AO(
        self, data: pd.DataFrame, short_period: int = 5, long_period: int = 34
    ) -> pd.Series:
        """
        Calculate Awesome Oscillator.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low' columns.
            short_period: Period for short SMA (default: 5).
            long_period: Period for long SMA (default: 34).

        Returns:
            pandas Series with AO values.
        """
        self._validate_data(data, ["high", "low"])
        ao = self._calculate_awesome_oscillator_numba(
            data["high"].values, data["low"].values, short_period, long_period
        )
        ao[: long_period - 1] = np.nan
        return pd.Series(ao, index=data.index, name="AO")

    @numba_fallback(lambda self, data, period1, period2, period3, weight1, weight2, weight3: pd.Series(np.nan, index=data.index, name="UO"))
    def ULTIMATE_OSCILLATOR(
        self,
        data: pd.DataFrame,
        period1: int = 7,
        period2: int = 14,
        period3: int = 28,
        weight1: float = 4.0,
        weight2: float = 2.0,
        weight3: float = 1.0,
    ) -> pd.Series:
        """
        Calculate Ultimate Oscillator.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            period1: First period (default: 7).
            period2: Second period (default: 14).
            period3: Third period (default: 28).
            weight1: Weight for period1 (default: 4.0).
            weight2: Weight for period2 (default: 2.0).
            weight3: Weight for period3 (default: 1.0).

        Returns:
            pandas Series with UO values.
        """
        self._validate_data(data, ["high", "low", "close"])
        uo = self._calculate_ultimate_oscillator_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            period1,
            period2,
            period3,
            weight1,
            weight2,
            weight3,
        )
        uo[: max(period1, period2, period3) - 1] = np.nan
        return pd.Series(uo, index=data.index, name="UO")

    def _cmo_fallback(self, data: Union[pd.Series, pd.DataFrame], period: int = 14) -> pd.Series:
        """Fallback calculation for CMO using pandas."""
        prices = self._validate_and_get_prices(data)
        deltas = prices.diff()
        gains = deltas.where(deltas > 0, 0).rolling(window=period).sum()
        losses = (-deltas.where(deltas < 0, 0)).rolling(window=period).sum()
        cmo = 100 * (gains - losses) / (gains + losses).replace(0, np.nan)
        return cmo.rename(f"CMO_{period}")

    @numba_fallback(_cmo_fallback)
    def CMO(self, data: Union[pd.Series, pd.DataFrame], period: int = 14) -> pd.Series:
        """
        Calculate Chande Momentum Oscillator.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for CMO calculation (default: 14).

        Returns:
            pandas Series with CMO values.
        """
        prices = self._validate_and_get_prices(data)
        cmo = self._calculate_chande_momentum_numba(prices.values, period)
        cmo[: period - 1] = np.nan
        return pd.Series(cmo, index=prices.index, name=f"CMO_{period}")

    def _dpo_fallback(self, data: Union[pd.Series, pd.DataFrame], period: int = 20) -> pd.Series:
        """Fallback calculation for DPO using pandas."""
        prices = self._validate_and_get_prices(data)
        sma = prices.rolling(window=period).mean()
        shift = period // 2 + 1
        dpo = prices.shift(-shift) - sma
        return dpo.rename(f"DPO_{period}")

    @numba_fallback(_dpo_fallback)
    def DPO(self, data: Union[pd.Series, pd.DataFrame], period: int = 20) -> pd.Series:
        """
        Calculate Detrended Price Oscillator.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for DPO calculation (default: 20).

        Returns:
            pandas Series with DPO values.
        """
        prices = self._validate_and_get_prices(data)
        dpo = self._calculate_dpo_numba(prices.values, period)
        dpo[: period - 1] = np.nan
        return pd.Series(dpo, index=prices.index, name=f"DPO_{period}")

    @numba_fallback(lambda self, data, ema_period, sum_period: pd.Series(np.nan, index=data.index, name=f"MI_{ema_period}_{sum_period}"))
    def MASS_INDEX(
        self, data: pd.DataFrame, ema_period: int = 9, sum_period: int = 25
    ) -> pd.Series:
        """
        Calculate Mass Index.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low' columns.
            ema_period: Period for EMA (default: 9).
            sum_period: Period for summation (default: 25).

        Returns:
            pandas Series with MI values.
        """
        self._validate_data(data, ["high", "low"])
        mi = self._calculate_mass_index_numba(
            data["high"].values, data["low"].values, ema_period, sum_period
        )
        mi[: sum_period - 1] = np.nan
        return pd.Series(mi, index=data.index, name=f"MI_{ema_period}_{sum_period}")

    def _vwap_fallback(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Fallback calculation for VWAP using Pandas."""
        self._validate_data(data, ["high", "low", "close", "volume"])
        typical_price = (data["high"] + data["low"] + data["close"]) / 3
        price_volume = typical_price * data["volume"]
        vwap = price_volume.rolling(window=period).sum() / data["volume"].rolling(window=period).sum()
        vwap.iloc[:period - 1] = np.nan
        return vwap.rename(f"VWAP_{period}")
    
    @numba_fallback(_vwap_fallback)
    def VWAP(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Volume Weighted Average Price.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close', 'volume' columns.
            period: Number of periods for VWAP calculation (default: 14).

        Returns:
            pandas Series with VWAP values.
        """
        self._validate_data(data, ["high", "low", "close", "volume"])
        vwap = self._calculate_vwap_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            data["volume"].values,
            period,
        )
        vwap[: period - 1] = np.nan
        return pd.Series(vwap, index=data.index, name=f"VWAP_{period}")

    def _supertrend_fallback(self, data: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        """Fallback calculation for Supertrend using Pandas."""
        self._validate_data(data, ["high", "low", "close"])
        tr = pd.DataFrame(index=data.index)
        tr["hl"] = data["high"] - data["low"]
        tr["hc"] = (data["high"] - data["close"].shift(1)).abs()
        tr["lc"] = (data["low"] - data["close"].shift(1)).abs()
        tr = tr.max(axis=1)
        atr = tr.rolling(window=period).mean()
        mid = (data["high"] + data["low"]) / 2
        upper_band = mid + (multiplier * atr)
        lower_band = mid - (multiplier * atr)
        supertrend = pd.Series(np.nan, index=data.index)
        direction = pd.Series(np.nan, index=data.index)
        supertrend.iloc[period] = lower_band.iloc[period]
        direction.iloc[period] = 1
        for i in range(period + 1, len(data)):
            prev_close = data["close"].iloc[i - 1]
            prev_supertrend = supertrend.iloc[i - 1]
            prev_direction = direction.iloc[i - 1]
            if not pd.isna(prev_close) and not pd.isna(prev_supertrend) and not pd.isna(prev_direction):
                upper_band.iloc[i] = min(upper_band.iloc[i], upper_band.iloc[i - 1]) if prev_direction == 1 else upper_band.iloc[i]
                lower_band.iloc[i] = max(lower_band.iloc[i], lower_band.iloc[i - 1]) if prev_direction == -1 else lower_band.iloc[i]
                if prev_direction == 1:
                    supertrend.iloc[i] = lower_band.iloc[i] if prev_close > prev_supertrend else upper_band.iloc[i]
                    direction.iloc[i] = 1 if prev_close > prev_supertrend else -1
                else:
                    supertrend.iloc[i] = upper_band.iloc[i] if prev_close < prev_supertrend else lower_band.iloc[i]
                    direction.iloc[i] = -1 if prev_close < prev_supertrend else 1
        supertrend.iloc[:period - 1] = np.nan
        direction.iloc[:period - 1] = np.nan
        return pd.DataFrame({"Supertrend": supertrend, "Direction": direction}, index=data.index)

    @numba_fallback(_supertrend_fallback)
    def SUPERTREND(
        self, data: pd.DataFrame, period: int = 10, multiplier: float = 3.0
    ) -> pd.DataFrame:
        """
        Calculate Supertrend indicator.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            period: Number of periods for Supertrend calculation (default: 10).
            multiplier: Multiplier for ATR (default: 3.0).

        Returns:
            pandas DataFrame with Supertrend and Direction columns.
        """
        self._validate_data(data, ["high", "low", "close"])
        supertrend, direction = self._calculate_supertrend_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            period,
            multiplier,
        )
        supertrend[: period - 1] = np.nan
        direction[: period - 1] = np.nan
        return pd.DataFrame(
            {"Supertrend": supertrend, "Direction": direction}, index=data.index
        )

    def _pvo_fallback(self, data: pd.DataFrame, short_period: int = 12, long_period: int = 26) -> pd.DataFrame:
        """Fallback calculation for Percentage Volume Oscillator using Pandas."""
        self._validate_data(data, ["volume"])
        short_ema = data["volume"].ewm(span=short_period, adjust=False).mean()
        long_ema = data["volume"].ewm(span=long_period, adjust=False).mean()
        pvo = ((short_ema - long_ema) / long_ema.replace(0, np.nan)) * 100
        signal = pvo.ewm(span=9, adjust=False).mean()
        histogram = pvo - signal
        pvo.iloc[:long_period - 1] = np.nan
        signal.iloc[:long_period - 1] = np.nan
        histogram.iloc[:long_period - 1] = np.nan
        return pd.DataFrame({"PVO": pvo, "Signal": signal, "Histogram": histogram}, index=data.index)

    @numba_fallback(_pvo_fallback)
    def PVO(
        self, data: pd.DataFrame, short_period: int = 12, long_period: int = 26
    ) -> pd.DataFrame:
        """
        Calculate Percentage Volume Oscillator.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'volume' column.
            short_period: Period for short EMA (default: 12).
            long_period: Period for long EMA (default: 26).

        Returns:
            pandas DataFrame with PVO, Signal, and Histogram columns.
        """
        self._validate_data(data, ["volume"])
        pvo, signal = self._calculate_pvo_numba(
            data["volume"].values, short_period, long_period
        )
        pvo[: long_period - 1] = np.nan
        signal[: long_period - 1] = np.nan
        histogram = pvo - signal
        return pd.DataFrame(
            {"PVO": pvo, "Signal": signal, "Histogram": histogram}, index=data.index
        )

    def _historical_volatility_fallback(
        self,
        data: Union[pd.Series, pd.DataFrame],
        period: int = 20,
        trading_days: int = 252,
    ) -> pd.Series:
        """Fallback calculation for Historical Volatility using pandas."""
        prices = self._validate_and_get_prices(data)
        returns = np.log(prices / prices.shift(1))
        hv = returns.rolling(window=period).std() * np.sqrt(trading_days) * 100
        return hv.rename(f"HV_{period}")

    @numba_fallback(_historical_volatility_fallback)
    def HISTORICAL_VOLATILITY(
        self,
        data: Union[pd.Series, pd.DataFrame],
        period: int = 20,
        trading_days: int = 252,
    ) -> pd.Series:
        """
        Calculate Historical Volatility.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for volatility calculation (default: 20).
            trading_days: Number of trading days in a year (default: 252).

        Returns:
            pandas Series with HV values.
        """
        prices = self._validate_and_get_prices(data)
        hv = self._calculate_historical_volatility_numba(
            prices.values, period, trading_days
        )
        hv[:period] = np.nan
        return pd.Series(hv, index=prices.index, name=f"HV_{period}")

    @numba_fallback(lambda self, data, ema_period, roc_period: pd.Series(np.nan, index=data.index, name=f"CV_{ema_period}_{roc_period}"))
    def CHAIKIN_VOLATILITY(
        self, data: pd.DataFrame, ema_period: int = 10, roc_period: int = 10
    ) -> pd.Series:
        """
        Calculate Chaikin Volatility.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low' columns.
            ema_period: Period for EMA (default: 10).
            roc_period: Period for ROC (default: 10).

        Returns:
            pandas Series with CV values.
        """
        self._validate_data(data, ["high", "low"])
        cv = self._calculate_chaikin_volatility_numba(
            data["high"].values, data["low"].values, ema_period, roc_period
        )
        cv[: ema_period + roc_period - 2] = np.nan
        return pd.Series(cv, index=data.index, name=f"CV_{ema_period}_{roc_period}")

    @numba_fallback(lambda self, data, period, deviations: pd.DataFrame(
        {"LRC_Upper": np.nan, "LRC_Middle": np.nan, "LRC_Lower": np.nan}, index=data.index))
    def LINEAR_REGRESSION_CHANNEL(
        self,
        data: Union[pd.Series, pd.DataFrame],
        period: int = 20,
        deviations: float = 2.0,
    ) -> pd.DataFrame:
        """
        Calculate Linear Regression Channel.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for regression (default: 20).
            deviations: Number of standard deviations for channels (default: 2.0).

        Returns:
            pandas DataFrame with LRC_Upper, LRC_Middle, and LRC_Lower columns.
        """
        prices = self._validate_and_get_prices(data)
        upper, middle, lower = self._calculate_linear_regression_channel_numba(
            prices.values, period, deviations
        )
        upper[: period - 1] = np.nan
        middle[: period - 1] = np.nan
        lower[: period - 1] = np.nan
        return pd.DataFrame(
            {"LRC_Upper": upper, "LRC_Middle": middle, "LRC_Lower": lower},
            index=prices.index,
        )

    @numba_fallback(lambda self, data, period: pd.DataFrame(
        {"MomentumIndex": np.nan, "NegativeIndex": np.nan}, index=data.index))
    def MOMENTUM_INDEX(self, data: pd.Series, period: int = 10) -> pd.DataFrame:
        """
        Calculate Momentum Index and Negative Index.
        Args:
            data: Price series or DataFrame with 'close' column.
            period: Number of periods for calculation (default: 10).
        Returns:
            pandas DataFrame with MomentumIndex and NegativeIndex columns.
        """
        prices = self._validate_and_get_prices(data)
        momentum_index, negative_index = self._calculate_momentum_index_numba(
            prices.values, period
        )
        momentum_index[:period - 1] = np.nan
        negative_index[:period - 1] = np.nan
        return pd.DataFrame(
            {
                "MomentumIndex": pd.Series(momentum_index, index=prices.index, name=f"MomentumIndex_{period}"),
                "NegativeIndex": pd.Series(negative_index, index=prices.index, name=f"NegativeIndex_{period}"),
            }
        )

    @numba_fallback(lambda self, data, period: pd.Series(np.nan, index=data.index, name=f"RVI_{period}"))
    def RVI(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Vigor Index.
        Args:
            data: DataFrame with 'open', 'high', 'low', 'close' columns.
            period: Number of periods for calculation (default: 14).
        Returns:
            pandas Series with RVI values.
        """
        self._validate_data(data, ["open", "high", "low", "close"])
        rvi = self._calculate_rvi_numba(
            data["open"].values,
            data["high"].values,
            data["low"].values,
            data["close"].values,
            period
        )
        rvi[:period - 1] = np.nan
        return pd.Series(rvi, index=data.index, name=f"RVI_{period}")
    
    @numba_fallback(lambda self, data: pd.Series(np.nan, index=data.index, name="AD"))
    def AD(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate Accumulation/Distribution Line.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close', 'volume' columns.

        Returns:
            pandas Series with AD values.
        """
        self._validate_data(data, ["high", "low", "close", "volume"])
        ad = self._calculate_ad_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            data["volume"].values,
        )
        return pd.Series(ad, index=data.index, name="AD")

    def _alma_fallback(
        self,
        data: Union[pd.Series, pd.DataFrame],
        period: int = 9,
        sigma: float = 6.0,
        offset: float = 0.85,
    ) -> pd.Series:
        """Fallback calculation for ALMA using pandas."""
        prices = self._validate_and_get_prices(data)
        m = offset * (period - 1)
        s = period / sigma
        weights = np.exp(-((np.arange(period) - m) ** 2) / (2 * s * s))
        weights /= weights.sum()
        alma = prices.rolling(window=period).apply(
            lambda x: np.sum(x * weights) if len(x) == period and not np.any(np.isnan(x)) else np.nan,
            raw=True
        )
        return alma.rename(f"ALMA_{period}")

    @numba_fallback(_alma_fallback)
    def ALMA(
        self,
        data: Union[pd.Series, pd.DataFrame],
        period: int = 9,
        sigma: float = 6.0,
        offset: float = 0.85,
    ) -> pd.Series:
        """
        Calculate Arnaud Legoux Moving Average.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for ALMA (default: 9).
            sigma: Gaussian distribution parameter (default: 6.0).
            offset: Offset for weighting (default: 0.85).

        Returns:
            pandas Series with ALMA values.
        """
        prices = self._validate_and_get_prices(data)
        alma = self._calculate_alma_numba(prices.values, period, sigma, offset)
        alma[: period - 1] = np.nan
        return pd.Series(alma, index=prices.index, name=f"ALMA_{period}")

    def _kdj_fallback(self, data: pd.DataFrame, k_period: int = 9, d_period: int = 3) -> pd.DataFrame:
        """Fallback calculation for KDJ using Pandas."""
        self._validate_data(data, ["high", "low", "close"])
        high_roll = data["high"].rolling(window=k_period).max()
        low_roll = data["low"].rolling(window=k_period).min()
        rsv = ((data["close"] - low_roll) / (high_roll - low_roll).replace(0, np.nan)) * 100
        k = pd.Series(np.nan, index=data.index)
        k.iloc[k_period - 1] = rsv.iloc[k_period - 1] if not pd.isna(rsv.iloc[k_period - 1]) else np.nan
        for i in range(k_period, len(data)):
            if not pd.isna(rsv.iloc[i]) and not pd.isna(k.iloc[i - 1]):
                k.iloc[i] = (2/3) * k.iloc[i - 1] + (1/3) * rsv.iloc[i]
        d = k.rolling(window=d_period).mean()
        j = 3 * k - 2 * d
        k.iloc[:k_period - 1] = np.nan
        d.iloc[:k_period + d_period - 2] = np.nan
        j.iloc[:k_period + d_period - 2] = np.nan
        return pd.DataFrame({"K": k, "D": d, "J": j}, index=data.index)

    @numba_fallback(_kdj_fallback)
    def KDJ(
        self, data: pd.DataFrame, k_period: int = 9, d_period: int = 3
    ) -> pd.DataFrame:
        """
        Calculate KDJ indicator.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            k_period: Period for %K calculation (default: 9).
            d_period: Period for %D calculation (default: 3).

        Returns:
            pandas DataFrame with K, D, and J columns.
        """
        self._validate_data(data, ["high", "low", "close"])
        k, d, j = self._calculate_kdj_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            k_period,
            d_period,
        )
        k[: k_period - 1] = np.nan
        d[: k_period + d_period - 2] = np.nan
        j[: k_period + d_period - 2] = np.nan
        return pd.DataFrame({"K": k, "D": d, "J": j}, index=data.index)

    def _heiken_ashi_fallback(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fallback calculation for Heiken Ashi using Pandas."""
        self._validate_data(data, ["open", "high", "low", "close"])
        ha_close = (data["open"] + data["high"] + data["low"] + data["close"]) / 4
        ha_open = pd.Series(np.nan, index=data.index)
        ha_open.iloc[0] = (data["open"].iloc[0] + data["close"].iloc[0]) / 2
        for i in range(1, len(data)):
            ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2
        ha_high = pd.concat([data["high"], ha_open, ha_close], axis=1).max(axis=1)
        ha_low = pd.concat([data["low"], ha_open, ha_close], axis=1).min(axis=1)
        return pd.DataFrame({
            "HA_Open": ha_open,
            "HA_High": ha_high,
            "HA_Low": ha_low,
            "HA_Close": ha_close
        }, index=data.index)

    @numba_fallback(_heiken_ashi_fallback)
    def HEIKEN_ASHI(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Heiken Ashi candles.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'open', 'high', 'low', 'close' columns.

        Returns:
            pandas DataFrame with HA_Open, HA_High, HA_Low, and HA_Close columns.
        """
        self._validate_data(data, ["open", "high", "low", "close"])
        ha_open, ha_high, ha_low, ha_close = self._calculate_heiken_ashi_numba(
            data["open"].values,
            data["high"].values,
            data["low"].values,
            data["close"].values,
        )
        return pd.DataFrame(
            {
                "HA_Open": ha_open,
                "HA_High": ha_high,
                "HA_Low": ha_low,
                "HA_Close": ha_close,
            },
            index=data.index,
        )



    @numba_fallback(lambda self, data: pd.Series(np.nan, index=data.index, name="OBV"))
    def OBV(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate On-Balance Volume.

        Args:
            data: DataFrame with 'close', 'volume' columns.

        Returns:
            pandas Series with OBV values.
        """
        self._validate_data(data, ["close", "volume"])
        obv = self._calculate_obv_numba(data["close"].values, data["volume"].values)
        return pd.Series(obv, index=data.index, name="OBV")

    def _beta_fallback(self, data: pd.Series, market_data: pd.Series, period: int = 252) -> pd.Series:
        """Fallback calculation for Beta using Pandas."""
        if not data.index.equals(market_data.index):
            raise ValueError("Indices of data and market_data must be aligned")
        if data.pct_change().std() < 0.1:
            returns = data.pct_change().fillna(0)
            market_returns = market_data.pct_change().fillna(0)
        else:
            returns = data
            market_returns = market_data
        cov = returns.rolling(window=period).cov(market_returns)
        var = market_returns.rolling(window=period).var()
        beta = cov / var.replace(0, np.nan)
        beta.iloc[:period] = np.nan
        return beta.rename(f"BETA_{period}")
    
    @numba_fallback(_beta_fallback)
    def BETA(
        self, data: pd.Series, market_data: pd.Series, period: int = 252
    ) -> pd.Series:
        """
        Calculate Rolling Beta.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series for the asset.
            market_data: Price series for the market benchmark.
            period: Number of periods for beta calculation (default: 252).

        Returns:
            pandas Series with BETA values.
        """
        if data.pct_change().std() < 0.1:
            returns = data.pct_change().fillna(0)
            market_returns = market_data.pct_change().fillna(0)
        else:
            returns = data
            market_returns = market_data
        beta = self._calculate_beta_numba(returns.values, market_returns.values, period)
        beta[:period] = np.nan
        return pd.Series(beta, index=data.index, name=f"BETA_{period}")

    @numba_fallback(lambda self, data, period: pd.DataFrame({"+DI": np.nan, "-DI": np.nan}, index=data.index))
    def DI(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Directional Indicator (+DI and -DI).

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            period: Number of periods for DI calculation (default: 14).

        Returns:
            pandas DataFrame with +DI and -DI columns.
        """
        self._validate_data(data, ["high", "low", "close"])
        plus_di, minus_di = self._calculate_di_numba(
            data["high"].values, data["low"].values, data["close"].values, period
        )
        return pd.DataFrame({"+DI": plus_di, "-DI": minus_di}, index=data.index)

    @numba_fallback(lambda self, data, period: pd.DataFrame(
        {"BullPower": np.nan, "BearPower": np.nan}, index=data.index))
    def ELDER_RAY(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Elder Ray Index (Bull Power and Bear Power).

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.
            period: Number of periods for EMA calculation (default: 14).

        Returns:
            pandas DataFrame with BullPower and BearPower columns.
        """
        self._validate_data(data, ["high", "low", "close"])
        bull_power, bear_power = self._calculate_elder_ray_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            period
        )
        bull_power[:period - 1] = np.nan
        bear_power[:period - 1] = np.nan
        return pd.DataFrame(
            {
                "BullPower": pd.Series(bull_power, index=data.index, name=f"BullPower_{period}"),
                "BearPower": pd.Series(bear_power, index=data.index, name=f"BearPower_{period}"),
            }
        )

    @numba_fallback(lambda self, data, fast_period, slow_period: pd.Series(np.nan, index=data.index, name=f"ADOSC_{fast_period}_{slow_period}"))
    def ADOSC(
        self, data: pd.DataFrame, fast_period: int = 3, slow_period: int = 10
    ) -> pd.Series:
        """
        Calculate Chaikin A/D Oscillator.

        Uses Numba for performance but falls back to a NaN Series if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close', 'volume' columns.
            fast_period: Period for fast EMA (default: 3).
            slow_period: Period for slow EMA (default: 10).

        Returns:
            pandas Series with ADOSC values.
        """
        self._validate_data(data, ["high", "low", "close", "volume"])
        adosc = self._calculate_adosc_numba(
            data["high"].values,
            data["low"].values,
            data["close"].values,
            data["volume"].values,
            fast_period,
            slow_period,
        )
        adosc[: slow_period - 1] = np.nan
        return pd.Series(
            adosc, index=data.index, name=f"ADOSC_{fast_period}_{slow_period}"
        )

    @numba_fallback(lambda self, data, period: pd.DataFrame(
        {"Volume_SMA": np.nan, "Force_Index": np.nan, "VPT": np.nan}, index=data.index))
    def VOLUME_INDICATORS(self, data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calculate various volume-based indicators.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'close', 'volume' columns.
            period: Number of periods for calculations (default: 20).

        Returns:
            pandas DataFrame with Volume_SMA, Force_Index, and VPT columns.
        """
        self._validate_data(data, ["close", "volume"])
        vol_sma, force_index, vpt = self._calculate_volume_indicators_numba(
            data["close"].values, data["volume"].values, period
        )
        vol_sma[: period - 1] = np.nan
        force_index[0] = np.nan
        return pd.DataFrame(
            {"Volume_SMA": vol_sma, "Force_Index": force_index, "VPT": vpt},
            index=data.index,
        )

    def _hull_ma_fallback(
        self, data: Union[pd.Series, pd.DataFrame], period: int = 10
    ) -> pd.Series:
        """Fallback calculation for Hull MA using pandas."""
        prices = self._validate_and_get_prices(data)
        half_period = period // 2
        wma1 = prices.rolling(half_period).apply(
            lambda x: np.sum(x * np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)),
            raw=True
        )
        wma2 = prices.rolling(period).apply(
            lambda x: np.sum(x * np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)),
            raw=True
        )
        raw = 2 * wma1 - wma2
        sqrt_period = int(np.sqrt(period))
        hull = raw.rolling(sqrt_period).apply(
            lambda x: np.sum(x * np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)),
            raw=True
        )
        return hull.rename(f"HULL_{period}")

    @numba_fallback(_hull_ma_fallback)
    def HULL_MA(
        self, data: Union[pd.Series, pd.DataFrame], period: int = 10
    ) -> pd.Series:
        """
        Calculate Hull Moving Average.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            period: Number of periods for HMA calculation (default: 10).

        Returns:
            pandas Series with HULL values.
        """
        prices = self._validate_and_get_prices(data)
        hull = self._calculate_hull_ma_numba(prices.values, period)
        hull[: period - 1] = np.nan
        return pd.Series(hull, index=prices.index, name=f"HULL_{period}")

    @numba_fallback(lambda self, data: pd.DataFrame(
        {"PP": np.nan, "R1": np.nan, "R2": np.nan, "S1": np.nan, "S2": np.nan}, index=data.index))
    def PIVOT_POINTS(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Classic Pivot Points.

        Uses Numba for performance but falls back to an empty DataFrame if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: DataFrame with 'high', 'low', 'close' columns.

        Returns:
            pandas DataFrame with PP, R1, R2, S1, and S2 columns.
        """
        self._validate_data(data, ["high", "low", "close"])
        pp, r1, r2, s1, s2 = self._calculate_pivot_points_numba(
            data["high"].values, data["low"].values, data["close"].values
        )
        return pd.DataFrame(
            {"PP": pp, "R1": r1, "R2": r2, "S1": s1, "S2": s2},
            index=data.index,
        )

    def _rainbow_fallback(
        self, data: Union[pd.Series, pd.DataFrame], periods: List[int] = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    ) -> pd.DataFrame:
        """Fallback calculation for Rainbow using pandas."""
        prices = self._validate_and_get_prices(data)
        rainbow = pd.DataFrame(index=prices.index)
        for period in periods:
            rainbow[f"SMA_{period}"] = prices.rolling(window=period).mean()
        return rainbow

    @numba_fallback(_rainbow_fallback)
    def RAINBOW(
        self, data: Union[pd.Series, pd.DataFrame], periods: List[int] = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    ) -> pd.DataFrame:
        """
        Calculate Rainbow Oscillator.

        Uses Numba for performance but falls back to pandas if Numba fails.
        Logs a warning if fallback is used.

        Args:
            data: Price series or DataFrame with 'adj_close' or 'close' column.
            periods: List of periods for SMA calculations (default: [2, 3, 4, 5, 6, 7, 8, 9, 10]).

        Returns:
            pandas DataFrame with SMA columns for each period.
        """
        prices = self._validate_and_get_prices(data)
        periods_np = np.array(periods, dtype=np.int64)
        sma_lines = self._calculate_rainbow_numba(prices.values, periods_np)
        rainbow = pd.DataFrame(index=prices.index)
        for idx, period in enumerate(periods):
            rainbow[f"SMA_{period}"] = sma_lines[idx]
        return rainbow

    def calculate_multiple_indicators(
        self,
        data: pd.DataFrame,
        indicators: List[Dict],
        symbol: str = None,
        n_jobs: int = -1,
        use_cache: bool = True,
        cache_size: int = 100,
    ) -> Dict[str, pd.Series]:
        """
        Calculate multiple indicators in parallel.

        Args:
            data: DataFrame with required columns for indicators.
            indicators: List of dictionaries specifying indicator names and parameters.
            symbol: Optional symbol for logging (default: None).
            n_jobs: Number of parallel jobs (-1 for all CPUs, default: -1).
            use_cache: Whether to cache results (default: True).
            cache_size: Maximum number of cached results (default: 100).

        Returns:
            Dictionary mapping indicator names to their results.
        """
        from concurrent.futures import ThreadPoolExecutor
        import multiprocessing
        import time
        import hashlib

        if n_jobs == -1:
            n_jobs = multiprocessing.cpu_count()
        results = {}
        calculation_times = {}

        # Initialize cache if not already present
        if not hasattr(self, '_cache'):
            self._cache = OrderedDict()
        if not hasattr(self, '_cache_lock'):
            self._cache_lock = threading.Lock()

        def calculate_single(indicator):
            name = indicator["name"]
            params = indicator.get("params", {})
            columns = indicator.get("columns", None)
            
            # Create a cache key based on indicator details and data hash
            if use_cache:
                params_tuple = tuple(sorted(params.items()))
                columns_tuple = tuple(sorted(columns)) if columns else ()
                df_for_hash = data[columns] if columns else data
                # Robust, content-based hash (values + index)
                try:
                    hv = pd.util.hash_pandas_object(df_for_hash, index=True).values
                    data_hash = hashlib.md5(hv.tobytes()).hexdigest()
                except Exception:
                    # Fallback to string rep only if hashing fails
                    data_hash = hashlib.md5(df_for_hash.to_csv(None).encode()).hexdigest()
                cache_key = (name, params_tuple, columns_tuple, data_hash)
                
                with self._cache_lock:
                    if cache_key in self._cache:
                        return (name, self._cache[cache_key], 0.0)

            start_time = time.time()
            try:
                func = getattr(self, name)
                indicator_data = data[columns] if columns else data
                if columns and not indicator_data.index.equals(data.index):
                    raise ValueError("Subset DataFrame index must match input DataFrame index")
                result = func(indicator_data, **params)
                if use_cache:
                    with self._cache_lock:
                        self._cache[cache_key] = result
                        if len(self._cache) > cache_size:
                            self._cache.popitem(last=False)
                calculation_time = time.time() - start_time
                return (name, result, calculation_time)
            except Exception as e:
                logger.error(f"Indicator calculation failed: {name}, symbol={symbol}, error={e}")
                return (name, None, time.time() - start_time)

        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            futures = [executor.submit(calculate_single, ind) for ind in indicators]
            for future in futures:
                name, result, calc_time = future.result()
                if result is not None:
                    results[name] = result
                    calculation_times[name] = calc_time
        logger.info(f"Indicator calculation completed: symbol={symbol}, times={calculation_times}")
        return results


# --- Attach util helper functions -------------------------------------------

TechnicalIndicators._validate_data = staticmethod(validate_data)
TechnicalIndicators._validate_and_get_prices = staticmethod(validate_and_get_prices)
TechnicalIndicators.validate_window = staticmethod(validate_window)
TechnicalIndicators.detect_divergence = staticmethod(detect_divergence)
TechnicalIndicators.detect_crossovers = staticmethod(detect_crossovers)
TechnicalIndicators.plot_indicators = staticmethod(plot_indicators)
TechnicalIndicators._optimize_memory = staticmethod(optimize_memory)

# --- Attach numba kernels as staticmethods -----------------------------------
_kernels: ModuleType = import_module("quantjourney_ti._indicator_kernels")
for _name in dir(_kernels):
    if _name.startswith("_calculate_") and _name.endswith("_numba"):
        setattr(TechnicalIndicators, _name, staticmethod(getattr(_kernels, _name)))

del _kernels, _name

# Create shared singleton so power users can access kernels quickly
_TI_INSTANCE = TechnicalIndicators()

__all__ = ["TechnicalIndicators", "_TI_INSTANCE"]

# --- Auto-normalize DataFrame inputs to include 'close' alias ---------------
def _normalize_close_df(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        return df
    out = df
    # If MultiIndex columns with single ticker, collapse ticker level
    try:
        if isinstance(out.columns, pd.MultiIndex) and out.columns.nlevels >= 2:
            lvl0 = [str(v).lower() for v in out.columns.get_level_values(0)]
            lvl1 = [str(v).lower() for v in out.columns.get_level_values(1)]
            fields_level = None
            tick_level = None
            common_fields = {"open", "high", "low", "close", "adj close", "adj_close", "volume"}
            if any(v in common_fields for v in lvl0):
                fields_level, tick_level = 0, 1
            elif any(v in common_fields for v in lvl1):
                fields_level, tick_level = 1, 0
            if fields_level is not None:
                # If only a single ticker present, drop that level
                ticks = list(out.columns.get_level_values(tick_level))
                unique_ticks = sorted(set(ticks), key=lambda x: str(x))
                if len(unique_ticks) == 1:
                    out = out.droplevel(tick_level, axis=1)
    except Exception:
        pass
    # Add 'close' alias if missing but 'adj_close' present
    if ('close' not in out.columns) and ('adj_close' in out.columns):
        out = out.copy()
        out['close'] = out['adj_close']
    return out

def _auto_normalize_close(method):
    from functools import wraps as _wraps
    @_wraps(method)
    def _wrapped(self, *args, **kwargs):
        if args:
            first = args[0]
            if isinstance(first, pd.DataFrame):
                first = _normalize_close_df(first)
                args = (first,) + args[1:]
        return method(self, *args, **kwargs)
    return _wrapped

# Wrap public methods to normalize 'close' alias for DataFrame inputs
for _n, _attr in list(TechnicalIndicators.__dict__.items()):
    if _n.startswith('_'):
        continue
    if _n == 'plot_indicators':
        # Avoid wrapping plotting helper to preserve its call signature
        continue
    if callable(_attr):
        setattr(TechnicalIndicators, _n, _auto_normalize_close(_attr))
