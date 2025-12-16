"""Linear regression calculator for QuantStream RTQAE."""

from typing import Dict, Any, Optional
from collections import deque
import numpy as np
from scipy import stats

from core.logger import get_logger
from core.config import get_config

logger = get_logger("analytics.regression")


class RegressionCalculator:
    """Calculates linear regression for pairs trading."""

    def __init__(self, window_size: int = None):
        config = get_config().analytics
        self.window_size = window_size or config.default_window_size
        self.min_periods = config.regression_min_periods
        self.price_windows: Dict[str, deque] = {}
        logger.info(f"Regression calculator initialized (window: {self.window_size})")

    def update_price(self, symbol: str, price: float):
        if symbol not in self.price_windows:
            self.price_windows[symbol] = deque(maxlen=self.window_size)
        self.price_windows[symbol].append(price)

    def calculate_regression(self, symbol_x: str, symbol_y: str) -> Optional[Dict[str, Any]]:
        if symbol_x not in self.price_windows or symbol_y not in self.price_windows:
            return None

        prices_x = list(self.price_windows[symbol_x])
        prices_y = list(self.price_windows[symbol_y])
        min_len = min(len(prices_x), len(prices_y))

        if min_len < self.min_periods:
            return None

        x = np.array(prices_x[-min_len:])
        y = np.array(prices_y[-min_len:])

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        predictions = slope * x + intercept
        residuals = y - predictions

        return {
            'symbol_x': symbol_x,
            'symbol_y': symbol_y,
            'beta': float(slope),
            'alpha': float(intercept),
            'r_squared': float(r_value ** 2),
            'r_value': float(r_value),
            'p_value': float(p_value),
            'std_err': float(std_err),
            'residual_mean': float(np.mean(residuals)),
            'residual_std': float(np.std(residuals)),
            'sample_size': min_len
        }

    def get_hedge_ratio(self, symbol_x: str, symbol_y: str) -> Optional[float]:
        result = self.calculate_regression(symbol_x, symbol_y)
        if result:
            return result['beta']
        return None

    def clear(self, symbol: str = None):
        if symbol and symbol in self.price_windows:
            del self.price_windows[symbol]
        elif not symbol:
            self.price_windows.clear()
