"""Main analytics engine coordinator for QuantStream RTQAE."""

from typing import Dict, List, Optional, Any
from threading import Lock

from analytics.price_stats import PriceStatsCalculator
from analytics.zscore import ZScoreCalculator
from analytics.correlation import CorrelationCalculator
from analytics.spread import SpreadCalculator
from analytics.regression import RegressionCalculator
from analytics.adf_test import ADFTest
from storage.models import Tick
from core.logger import get_logger
from core.config import get_config

logger = get_logger("analytics.engine")


class AnalyticsEngine:
    """Main analytics engine coordinating all analytics modules."""

    def __init__(self, window_size: Optional[int] = None):
        config = get_config().analytics
        self.window_size = window_size or config.default_window_size

        self.price_stats = PriceStatsCalculator(self.window_size)
        self.zscore_calc = ZScoreCalculator(self.window_size)
        self.correlation_calc = CorrelationCalculator(self.window_size)
        self.spread_calc = SpreadCalculator(self.window_size)
        self.regression_calc = RegressionCalculator(self.window_size)
        self.adf_test = ADFTest(self.window_size)

        self.latest_stats: Dict[str, Dict[str, Any]] = {}
        self.latest_zscores: Dict[str, Dict[str, Any]] = {}

        self.lock = Lock()
        logger.info(f"Analytics engine initialized (window size: {self.window_size})")

    def update(self, tick: Tick):
        with self.lock:
            symbol = tick.symbol
            price = tick.price

            stats = self.price_stats.update(tick)
            self.latest_stats[symbol] = stats

            if stats:
                zscore_result = self.zscore_calc.calculate_from_stats(stats)
                self.latest_zscores[symbol] = zscore_result

            self.correlation_calc.update_price(symbol, price)
            self.spread_calc.update_price(symbol, price)
            self.regression_calc.update_price(symbol, price)
            self.adf_test.update_price(symbol, price)

    def get_stats(self, symbol: str) -> Dict[str, Any]:
        with self.lock:
            return self.latest_stats.get(symbol, {})

    def get_zscore(self, symbol: str) -> Dict[str, Any]:
        with self.lock:
            return self.latest_zscores.get(symbol, {})

    def get_correlation(self, symbol1: str, symbol2: str, corr_type: str = 'pearson') -> Optional[Dict[str, Any]]:
        with self.lock:
            if corr_type == 'spearman':
                return self.correlation_calc.calculate_spearman(symbol1, symbol2)
            return self.correlation_calc.calculate_pearson(symbol1, symbol2)

    def get_all_correlations(self, corr_type: str = 'pearson') -> List[Dict[str, Any]]:
        with self.lock:
            return self.correlation_calc.calculate_all_pairs(corr_type)

    def get_correlation_matrix(self) -> Optional[Any]:
        with self.lock:
            return self.correlation_calc.get_correlation_matrix()

    def get_spread(self, symbol1: str, symbol2: str, hedge_ratio: float = 1.0) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.spread_calc.calculate_spread(symbol1, symbol2, hedge_ratio)

    def get_normalized_spread(self, symbol1: str, symbol2: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.spread_calc.calculate_normalized_spread(symbol1, symbol2)

    def get_regression(self, symbol_x: str, symbol_y: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.regression_calc.calculate_regression(symbol_x, symbol_y)

    def get_hedge_ratio(self, symbol_x: str, symbol_y: str) -> Optional[float]:
        with self.lock:
            return self.regression_calc.get_hedge_ratio(symbol_x, symbol_y)

    def get_adf_test(self, symbol: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.adf_test.test_price_series(symbol)

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        with self.lock:
            return self.latest_stats.copy()

    def get_all_zscores(self) -> Dict[str, Dict[str, Any]]:
        with self.lock:
            return self.latest_zscores.copy()

    def get_symbols(self) -> List[str]:
        with self.lock:
            return list(self.latest_stats.keys())

    def get_summary(self) -> Dict[str, Any]:
        with self.lock:
            symbols = list(self.latest_stats.keys())
            latest_prices = {s: stats.get('current_price') for s, stats in self.latest_stats.items() if 'current_price' in stats}

            return {
                'symbols': symbols,
                'symbol_count': len(symbols),
                'window_size': self.window_size,
                'stats_available': len(self.latest_stats),
                'latest_prices': latest_prices
            }

    def clear(self, symbol: str = None):
        with self.lock:
            self.price_stats.clear(symbol)
            self.correlation_calc.clear(symbol)
            self.spread_calc.clear(symbol)
            self.regression_calc.clear(symbol)
            self.adf_test.clear(symbol)

            if symbol:
                self.latest_stats.pop(symbol, None)
                self.latest_zscores.pop(symbol, None)
            else:
                self.latest_stats.clear()
                self.latest_zscores.clear()
