"""ADF test for stationarity in QuantStream RTQAE."""

from typing import Dict, Any, Optional
from collections import deque
import numpy as np
from statsmodels.tsa.stattools import adfuller

from core.logger import get_logger
from core.config import get_config

logger = get_logger("analytics.adf_test")


class ADFTest:
    """Augmented Dickey-Fuller test for stationarity."""

    def __init__(self, window_size: int = None):
        config = get_config().analytics
        self.window_size = window_size or config.default_window_size
        self.max_lag = config.adf_max_lag
        self.price_windows: Dict[str, deque] = {}
        self.spread_windows: Dict[str, deque] = {}
        logger.info(f"ADF test initialized (window: {self.window_size})")

    def update_price(self, symbol: str, price: float):
        if symbol not in self.price_windows:
            self.price_windows[symbol] = deque(maxlen=self.window_size)
        self.price_windows[symbol].append(price)

    def update_spread(self, pair_name: str, spread_value: float):
        if pair_name not in self.spread_windows:
            self.spread_windows[pair_name] = deque(maxlen=self.window_size)
        self.spread_windows[pair_name].append(spread_value)

    def test_price_series(self, symbol: str) -> Optional[Dict[str, Any]]:
        if symbol not in self.price_windows or len(self.price_windows[symbol]) < 30:
            return None

        prices = np.array(self.price_windows[symbol])
        return self._run_adf_test(symbol, prices)

    def test_spread_series(self, pair_name: str) -> Optional[Dict[str, Any]]:
        if pair_name not in self.spread_windows or len(self.spread_windows[pair_name]) < 30:
            return None

        spreads = np.array(self.spread_windows[pair_name])
        return self._run_adf_test(pair_name, spreads)

    def _run_adf_test(self, name: str, series: np.ndarray) -> Dict[str, Any]:
        try:
            result = adfuller(series, maxlag=self.max_lag, autolag='AIC')

            adf_stat = result[0]
            p_value = result[1]
            used_lag = result[2]
            nobs = result[3]
            critical_values = result[4]

            is_stationary = bool(p_value < 0.05)  # Convert numpy.bool to Python bool

            return {
                'series_name': name,
                'adf_statistic': float(adf_stat),
                'p_value': float(p_value),
                'is_stationary': is_stationary,
                'used_lag': int(used_lag),
                'num_observations': int(nobs),
                'critical_1pct': float(critical_values['1%']),
                'critical_5pct': float(critical_values['5%']),
                'critical_10pct': float(critical_values['10%']),
                'sample_size': len(series)
            }

        except Exception as e:
            logger.error(f"ADF test error for {name}: {e}")
            return None

    def clear(self, symbol: str = None):
        if symbol:
            if symbol in self.price_windows:
                del self.price_windows[symbol]
            if symbol in self.spread_windows:
                del self.spread_windows[symbol]
        else:
            self.price_windows.clear()
            self.spread_windows.clear()
