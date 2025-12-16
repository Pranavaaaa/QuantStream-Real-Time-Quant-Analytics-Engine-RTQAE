"""Price statistics calculator for QuantStream RTQAE."""

from typing import Dict, Any, List, Optional
from collections import deque
import numpy as np
import math

from storage.models import Tick
from core.logger import get_logger

logger = get_logger("analytics.price_stats")


def safe_float(value):
    """Convert value to float, replacing NaN/Inf with None or 0."""
    if value is None:
        return 0.0
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return 0.0
        return f
    except (ValueError, TypeError):
        return 0.0


class PriceStatsCalculator:
    """Calculates rolling price statistics."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.price_windows: Dict[str, deque] = {}
        self.volume_windows: Dict[str, deque] = {}
        logger.info(f"Price stats calculator initialized (window: {window_size})")

    def update(self, tick: Tick) -> Dict[str, Any]:
        symbol = tick.symbol
        if symbol not in self.price_windows:
            self.price_windows[symbol] = deque(maxlen=self.window_size)
            self.volume_windows[symbol] = deque(maxlen=self.window_size)

        self.price_windows[symbol].append(tick.price)
        self.volume_windows[symbol].append(tick.size)

        return self.calculate(symbol)

    def calculate(self, symbol: str) -> Dict[str, Any]:
        if symbol not in self.price_windows or len(self.price_windows[symbol]) < 2:
            return {}

        prices = np.array(self.price_windows[symbol])
        volumes = np.array(self.volume_windows[symbol])

        current_price = prices[-1]
        first_price = prices[0]

        # Safely compute statistics
        mean_val = np.mean(prices)
        std_val = np.std(prices)
        
        # Avoid division by zero for price change %
        if first_price > 0:
            price_change_pct = (current_price - first_price) / first_price * 100
        else:
            price_change_pct = 0

        stats = {
            'symbol': symbol,
            'current_price': safe_float(current_price),
            'mean': safe_float(mean_val),
            'median': safe_float(np.median(prices)),
            'std': safe_float(std_val),
            'min': safe_float(np.min(prices)),
            'max': safe_float(np.max(prices)),
            'range': safe_float(np.max(prices) - np.min(prices)),
            'count': len(prices),
            'total_volume': safe_float(np.sum(volumes)),
            'avg_volume': safe_float(np.mean(volumes)),
            'volume_std': safe_float(np.std(volumes)),
            'price_change': safe_float(current_price - first_price),
            'price_change_pct': safe_float(price_change_pct)
        }

        # Calculate VWAP
        total_vol = np.sum(volumes)
        if total_vol > 0:
            stats['vwap'] = safe_float(np.sum(prices * volumes) / total_vol)
        else:
            stats['vwap'] = stats['mean']

        # Calculate volatility (annualized) - avoid division by zero
        if len(prices) > 1:
            with np.errstate(divide='ignore', invalid='ignore'):
                # Filter out zero prices to avoid divide by zero
                valid_prices = prices[prices > 0]
                if len(valid_prices) > 1:
                    returns = np.diff(valid_prices) / valid_prices[:-1]
                    returns = returns[~np.isnan(returns) & ~np.isinf(returns)]
                    if len(returns) > 0:
                        stats['volatility'] = safe_float(np.std(returns) * np.sqrt(252 * 24 * 60))
                    else:
                        stats['volatility'] = 0.0
                else:
                    stats['volatility'] = 0.0
        else:
            stats['volatility'] = 0.0

        return stats

    def get_stats(self, symbol: str) -> Dict[str, Any]:
        return self.calculate(symbol)

    def clear(self, symbol: str = None):
        if symbol:
            if symbol in self.price_windows:
                del self.price_windows[symbol]
            if symbol in self.volume_windows:
                del self.volume_windows[symbol]
        else:
            self.price_windows.clear()
            self.volume_windows.clear()
