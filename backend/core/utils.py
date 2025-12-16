"""Utility functions for QuantStream RTQAE."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np


def timestamp_to_iso(timestamp_ms: int) -> str:
    """Convert millisecond timestamp to ISO 8601 string."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return dt.isoformat()


def iso_to_timestamp(iso_string: str) -> int:
    """Convert ISO 8601 string to millisecond timestamp."""
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    return int(dt.timestamp() * 1000)


def current_timestamp_iso() -> str:
    """Get current timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def current_timestamp_ms() -> int:
    """Get current timestamp in milliseconds."""
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def validate_symbol(symbol: str) -> bool:
    """Validate cryptocurrency symbol format."""
    if not symbol or not isinstance(symbol, str):
        return False
    return symbol.isalnum() and 6 <= len(symbol) <= 12


def normalize_symbol(symbol: str) -> str:
    """Normalize symbol to uppercase."""
    return symbol.upper().strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def calculate_returns(prices: List[float]) -> List[float]:
    """Calculate percentage returns from price series."""
    if len(prices) < 2:
        return []
    prices_array = np.array(prices)
    returns = np.diff(prices_array) / prices_array[:-1] * 100
    return returns.tolist()


def calculate_vwap(prices: List[float], volumes: List[float]) -> Optional[float]:
    """Calculate Volume Weighted Average Price."""
    if not prices or not volumes or len(prices) != len(volumes):
        return None
    try:
        prices_array = np.array(prices)
        volumes_array = np.array(volumes)
        if volumes_array.sum() == 0:
            return None
        vwap = np.sum(prices_array * volumes_array) / np.sum(volumes_array)
        return float(vwap)
    except Exception:
        return None


def ticks_to_dataframe(ticks: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert list of tick dictionaries to pandas DataFrame."""
    if not ticks:
        return pd.DataFrame(columns=['symbol', 'timestamp', 'price', 'size'])
    df = pd.DataFrame(ticks)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def resample_to_ohlcv(
    df: pd.DataFrame,
    timeframe: str = '1min',
    price_col: str = 'price',
    volume_col: str = 'size'
) -> pd.DataFrame:
    """Resample tick data to OHLCV candlesticks."""
    if df.empty or 'timestamp' not in df.columns:
        return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_copy = df.copy()
    df_copy.set_index('timestamp', inplace=True)
    ohlcv = df_copy[price_col].resample(timeframe).ohlc()
    ohlcv['volume'] = df_copy[volume_col].resample(timeframe).sum()
    ohlcv.reset_index(inplace=True)
    ohlcv.dropna(inplace=True)
    return ohlcv


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with thousand separators."""
    return f"{value:,.{decimals}f}"
