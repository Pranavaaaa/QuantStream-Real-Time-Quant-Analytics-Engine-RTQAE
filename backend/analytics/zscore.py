"""Z-score calculator for QuantStream RTQAE."""

from typing import Dict, Any, Optional
from core.logger import get_logger

logger = get_logger("analytics.zscore")


class ZScoreCalculator:
    """Calculates z-scores for price data."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.price_stats: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Z-score calculator initialized (window: {window_size})")

    def calculate(self, symbol: str, current_price: float, mean: float, std: float) -> Dict[str, Any]:
        if std == 0 or std is None:
            return {'symbol': symbol, 'zscore': 0, 'outlier_level': 'normal'}

        zscore = (current_price - mean) / std

        if abs(zscore) > 3:
            outlier_level = 'extreme'
        elif abs(zscore) > 2:
            outlier_level = 'high'
        elif abs(zscore) > 1:
            outlier_level = 'moderate'
        else:
            outlier_level = 'normal'

        return {
            'symbol': symbol,
            'current_price': current_price,
            'mean': mean,
            'std': std,
            'zscore': float(zscore),
            'outlier_level': outlier_level,
            'is_outlier_1sigma': abs(zscore) > 1,
            'is_outlier_2sigma': abs(zscore) > 2,
            'is_outlier_3sigma': abs(zscore) > 3
        }

    def calculate_from_stats(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        if not stats or 'current_price' not in stats:
            return {}

        return self.calculate(
            symbol=stats.get('symbol', ''),
            current_price=stats.get('current_price', 0),
            mean=stats.get('mean', 0),
            std=stats.get('std', 0)
        )
