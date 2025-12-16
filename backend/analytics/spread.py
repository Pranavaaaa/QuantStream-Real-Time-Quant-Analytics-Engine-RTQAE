"""Spread calculator for QuantStream RTQAE."""

from typing import Dict, Any, Optional
from collections import deque
import numpy as np

from core.logger import get_logger
from core.config import get_config

logger = get_logger("analytics.spread")


class SpreadCalculator:
    """Calculates spreads for pairs trading."""

    def __init__(self, window_size: int = None):
        config = get_config().analytics
        self.window_size = window_size or config.default_window_size
        self.price_windows: Dict[str, deque] = {}
        self.spread_windows: Dict[str, deque] = {}
        logger.info(f"Spread calculator initialized (window: {self.window_size})")

    def update_price(self, symbol: str, price: float):
        if symbol not in self.price_windows:
            self.price_windows[symbol] = deque(maxlen=self.window_size)
        self.price_windows[symbol].append(price)

    def calculate_spread(self, symbol1: str, symbol2: str, hedge_ratio: float = 1.0) -> Optional[Dict[str, Any]]:
        if symbol1 not in self.price_windows or symbol2 not in self.price_windows:
            return None

        prices1 = list(self.price_windows[symbol1])
        prices2 = list(self.price_windows[symbol2])
        min_len = min(len(prices1), len(prices2))

        if min_len < 10:
            return None

        arr1 = np.array(prices1[-min_len:])
        arr2 = np.array(prices2[-min_len:])
        spread = arr1 - hedge_ratio * arr2

        current_spread = spread[-1]
        spread_mean = np.mean(spread)
        spread_std = np.std(spread)
        spread_zscore = (current_spread - spread_mean) / spread_std if spread_std > 0 else 0

        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'hedge_ratio': hedge_ratio,
            'current_spread': float(current_spread),
            'spread_mean': float(spread_mean),
            'spread_std': float(spread_std),
            'spread_zscore': float(spread_zscore),
            'sample_size': min_len
        }

    def calculate_normalized_spread(self, symbol1: str, symbol2: str) -> Optional[Dict[str, Any]]:
        if symbol1 not in self.price_windows or symbol2 not in self.price_windows:
            return None

        prices1 = list(self.price_windows[symbol1])
        prices2 = list(self.price_windows[symbol2])
        min_len = min(len(prices1), len(prices2))

        if min_len < 10:
            return None

        arr1 = np.array(prices1[-min_len:])
        arr2 = np.array(prices2[-min_len:])
        ratio = arr1 / arr2

        current_ratio = ratio[-1]
        ratio_mean = np.mean(ratio)
        ratio_std = np.std(ratio)
        ratio_zscore = (current_ratio - ratio_mean) / ratio_std if ratio_std > 0 else 0

        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'current_ratio': float(current_ratio),
            'ratio_mean': float(ratio_mean),
            'ratio_std': float(ratio_std),
            'ratio_zscore': float(ratio_zscore),
            'sample_size': min_len
        }

    def clear(self, symbol: str = None):
        if symbol and symbol in self.price_windows:
            del self.price_windows[symbol]
        elif not symbol:
            self.price_windows.clear()
            self.spread_windows.clear()
