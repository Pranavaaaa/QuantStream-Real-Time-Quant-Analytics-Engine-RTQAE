"""Alert notifier for QuantStream RTQAE."""

from storage.models import Alert
from core.logger import get_logger

logger = get_logger("alerts.notifier")


class AlertNotifier:
    def __init__(self):
        self.notification_count = 0
        logger.info("Alert notifier initialized")

    def notify(self, alert: Alert):
        self._notify_console(alert)
        self.notification_count += 1

    def _notify_console(self, alert: Alert):
        # Using ASCII characters instead of emojis for Windows compatibility
        severity_symbol = {
            'low': '[LOW]',
            'medium': '[MEDIUM]', 
            'high': '[HIGH]',
            'critical': '[CRITICAL]'
        }
        symbol = severity_symbol.get(alert.severity.value, '[ALERT]')

        log_message = f"\n{'='*50}\n{symbol} ALERT\nSymbol: {alert.symbol}\nMessage: {alert.message}\n{'='*50}"

        if alert.severity.value == 'critical':
            logger.critical(log_message)
        elif alert.severity.value == 'high':
            logger.error(log_message)
        elif alert.severity.value == 'medium':
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def get_notification_count(self) -> int:
        return self.notification_count
