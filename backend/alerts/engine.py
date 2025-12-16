"""Alert engine for QuantStream RTQAE."""

from typing import List, Dict, Any
from datetime import datetime
from threading import Lock

from alerts.rules import AlertRule
from alerts.notifier import AlertNotifier
from storage.models import Alert, AlertSeverity
from core.logger import get_logger

logger = get_logger("alerts.engine")


class AlertEngine:
    def __init__(self, db_client=None, cooldown_seconds: int = 300):
        self.db_client = db_client
        self.cooldown_seconds = cooldown_seconds
        self.rules: List[AlertRule] = []
        self.notifier = AlertNotifier()
        self.last_alert_time: Dict[str, datetime] = {}
        self.lock = Lock()
        self.alert_count = 0
        logger.info(f"Alert engine initialized (cooldown: {cooldown_seconds}s)")

    def add_rule(self, rule: AlertRule):
        with self.lock:
            self.rules.append(rule)

    def add_rules(self, rules: List[AlertRule]):
        with self.lock:
            self.rules.extend(rules)
            logger.info(f"Added {len(rules)} alert rules")

    def evaluate_stats(self, stats: Dict[str, Any]):
        if not stats or 'symbol' not in stats:
            return
        symbol = stats['symbol']

        with self.lock:
            symbol_rules = [r for r in self.rules if r.symbol == symbol and r.enabled]

        for rule in symbol_rules:
            try:
                result = rule.evaluate(stats)
                if result:
                    self._trigger_alert(result, rule)
            except Exception as e:
                logger.error(f"Error evaluating rule: {e}")

    def evaluate_zscore(self, zscore_data: Dict[str, Any]):
        if not zscore_data or 'symbol' not in zscore_data:
            return
        symbol = zscore_data['symbol']

        with self.lock:
            symbol_rules = [r for r in self.rules if r.symbol == symbol and r.enabled and 'zscore' in r.rule_type.value]

        for rule in symbol_rules:
            try:
                result = rule.evaluate(zscore_data)
                if result:
                    self._trigger_alert(result, rule)
            except Exception as e:
                logger.error(f"Error evaluating z-score rule: {e}")

    def _trigger_alert(self, alert_data: Dict[str, Any], rule: AlertRule):
        rule_key = f"{rule.rule_type.value}_{rule.symbol}"

        if rule_key in self.last_alert_time:
            time_since = datetime.now() - self.last_alert_time[rule_key]
            if time_since.total_seconds() < self.cooldown_seconds:
                return

        severity = self._determine_severity(alert_data)

        alert = Alert(
            symbol=alert_data['symbol'],
            timestamp=datetime.now().isoformat() + 'Z',
            rule_type=alert_data['rule_type'],
            message=alert_data['message'],
            severity=severity,
            triggered_value=alert_data.get('triggered_value')
        )

        self.notifier.notify(alert)

        if self.db_client:
            try:
                self.db_client.insert_alert(alert)
            except Exception as e:
                logger.error(f"Failed to store alert: {e}")

        self.last_alert_time[rule_key] = datetime.now()
        self.alert_count += 1
        logger.info(f"Alert triggered: {alert.message}")

    def _determine_severity(self, alert_data: Dict[str, Any]) -> AlertSeverity:
        triggered_value = alert_data.get('triggered_value', 0)
        rule_type = alert_data.get('rule_type', '')

        if 'zscore' in rule_type:
            if abs(triggered_value) > 4:
                return AlertSeverity.CRITICAL
            elif abs(triggered_value) > 3:
                return AlertSeverity.HIGH
            elif abs(triggered_value) > 2:
                return AlertSeverity.MEDIUM
        return AlertSeverity.LOW

    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.db_client:
            return []
        return self.db_client.query_alerts(limit=limit)

    def get_alert_count(self) -> int:
        return self.alert_count

    def get_rule_count(self) -> int:
        with self.lock:
            return len([r for r in self.rules if r.enabled])
