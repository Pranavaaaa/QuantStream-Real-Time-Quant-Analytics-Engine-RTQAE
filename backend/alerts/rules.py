"""Alert rules for QuantStream RTQAE."""

from typing import Dict, Any, Optional
from enum import Enum

from core.logger import get_logger
from core.config import get_config

logger = get_logger("alerts.rules")


class AlertType(str, Enum):
    PRICE_THRESHOLD = "price_threshold"
    PRICE_CHANGE = "price_change"
    ZSCORE_THRESHOLD = "zscore_threshold"
    VOLUME_SPIKE = "volume_spike"


class AlertRule:
    def __init__(self, rule_type: AlertType, symbol: str, **params):
        self.rule_type = rule_type
        self.symbol = symbol
        self.params = params
        self.enabled = True

    def evaluate(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class ZScoreThresholdRule(AlertRule):
    def __init__(self, symbol: str, threshold: float = 3.0):
        super().__init__(AlertType.ZSCORE_THRESHOLD, symbol, threshold=threshold)

    def evaluate(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.enabled or 'zscore' not in data:
            return None

        zscore = data['zscore']
        threshold = self.params['threshold']

        if abs(zscore) > threshold:
            return {
                'rule_type': self.rule_type.value,
                'symbol': self.symbol,
                'message': f"Z-score {zscore:.2f} exceeds threshold {threshold}",
                'triggered_value': abs(zscore),
                'threshold': threshold
            }
        return None


class PriceChangeRule(AlertRule):
    def __init__(self, symbol: str, threshold_pct: float):
        super().__init__(AlertType.PRICE_CHANGE, symbol, threshold_pct=threshold_pct)

    def evaluate(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.enabled or 'price_change_pct' not in data:
            return None

        change_pct = abs(data['price_change_pct'])
        threshold = self.params['threshold_pct']

        if change_pct > threshold:
            return {
                'rule_type': self.rule_type.value,
                'symbol': self.symbol,
                'message': f"Price changed by {change_pct:.2f}%",
                'triggered_value': change_pct,
                'threshold': threshold
            }
        return None


class VolumeSpikeRule(AlertRule):
    def __init__(self, symbol: str, multiplier: float = 3.0):
        super().__init__(AlertType.VOLUME_SPIKE, symbol, multiplier=multiplier)

    def evaluate(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.enabled or 'total_volume' not in data or 'avg_volume' not in data:
            return None

        current_vol = data.get('total_volume', 0)
        avg_vol = data.get('avg_volume', 1)
        multiplier = self.params['multiplier']

        if avg_vol > 0 and current_vol > avg_vol * multiplier:
            return {
                'rule_type': self.rule_type.value,
                'symbol': self.symbol,
                'message': f"Volume spike: {current_vol:.2f} (avg: {avg_vol:.2f})",
                'triggered_value': current_vol / avg_vol,
                'threshold': multiplier
            }
        return None


def create_default_rules(symbols: list) -> list:
    config = get_config().alerts
    rules = []

    for symbol in symbols:
        rules.append(ZScoreThresholdRule(symbol, config.zscore_threshold))
        rules.append(PriceChangeRule(symbol, config.price_change_threshold))
        rules.append(VolumeSpikeRule(symbol, config.volume_spike_threshold))

    logger.info(f"Created {len(rules)} default rules for {len(symbols)} symbols")
    return rules
