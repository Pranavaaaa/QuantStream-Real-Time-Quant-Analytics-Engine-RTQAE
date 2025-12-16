"""Correlation calculator for QuantStream RTQAE."""

from typing import Dict, Any, List, Optional, Tuple
from collections import deque
import numpy as np
from scipy import stats

from core.logger import get_logger
from core.config import get_config

logger = get_logger("analytics.correlation")


class CorrelationCalculator:
    """Calculates correlations between symbol pairs."""

    def __init__(self, window_size: int = None):
        config = get_config().analytics
        self.window_size = window_size or config.default_window_size
        self.min_periods = config.correlation_min_periods
        self.price_windows: Dict[str, deque] = {}
        logger.info(f"Correlation calculator initialized (window: {self.window_size})")

    def update_price(self, symbol: str, price: float):
        if symbol not in self.price_windows:
            self.price_windows[symbol] = deque(maxlen=self.window_size)
        self.price_windows[symbol].append(price)

    def calculate_pearson(self, symbol1: str, symbol2: str) -> Optional[Dict[str, Any]]:
        if symbol1 not in self.price_windows or symbol2 not in self.price_windows:
            return None

        prices1 = list(self.price_windows[symbol1])
        prices2 = list(self.price_windows[symbol2])
        min_len = min(len(prices1), len(prices2))

        if min_len < self.min_periods:
            return None

        arr1 = np.array(prices1[-min_len:])
        arr2 = np.array(prices2[-min_len:])

        corr, p_value = stats.pearsonr(arr1, arr2)

        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'correlation': float(corr),
            'p_value': float(p_value),
            'sample_size': min_len,
            'method': 'pearson'
        }

    def calculate_spearman(self, symbol1: str, symbol2: str) -> Optional[Dict[str, Any]]:
        if symbol1 not in self.price_windows or symbol2 not in self.price_windows:
            return None

        prices1 = list(self.price_windows[symbol1])
        prices2 = list(self.price_windows[symbol2])
        min_len = min(len(prices1), len(prices2))

        if min_len < self.min_periods:
            return None

        arr1 = np.array(prices1[-min_len:])
        arr2 = np.array(prices2[-min_len:])

        corr, p_value = stats.spearmanr(arr1, arr2)

        return {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'correlation': float(corr),
            'p_value': float(p_value),
            'sample_size': min_len,
            'method': 'spearman'
        }

    def calculate_all_pairs(self, method: str = 'pearson') -> List[Dict[str, Any]]:
        symbols = list(self.price_windows.keys())
        results = []

        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                if method == 'spearman':
                    corr = self.calculate_spearman(sym1, sym2)
                else:
                    corr = self.calculate_pearson(sym1, sym2)
                if corr:
                    results.append(corr)

        return results

    def get_correlation_matrix(self) -> Optional[np.ndarray]:
        symbols = list(self.price_windows.keys())
        if len(symbols) < 2:
            return None

        n = len(symbols)
        matrix = np.eye(n)

        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                if i < j:
                    corr = self.calculate_pearson(sym1, sym2)
                    if corr:
                        matrix[i, j] = corr['correlation']
                        matrix[j, i] = corr['correlation']

        return matrix

    def get_symbols(self) -> List[str]:
        return list(self.price_windows.keys())

    def clear(self, symbol: str = None):
        if symbol and symbol in self.price_windows:
            del self.price_windows[symbol]
        elif not symbol:
            self.price_windows.clear()
