"""Data router for QuantStream RTQAE."""

from typing import List, Callable
from threading import Lock

from storage.models import Tick
from core.logger import get_logger

logger = get_logger("ingestion.router")


class DataRouter:
    """Routes incoming tick data to registered handlers."""

    def __init__(self):
        self.handlers: List[Callable[[Tick], None]] = []
        self.lock = Lock()
        self._routed_count = 0
        logger.info("Data router initialized")

    def register_handler(self, handler: Callable[[Tick], None]):
        with self.lock:
            self.handlers.append(handler)
            logger.info(f"Handler registered (total: {len(self.handlers)})")

    def unregister_handler(self, handler: Callable[[Tick], None]):
        with self.lock:
            if handler in self.handlers:
                self.handlers.remove(handler)
                logger.info("Handler unregistered")

    def route_tick(self, tick: Tick):
        with self.lock:
            handlers = self.handlers.copy()
        for handler in handlers:
            try:
                handler(tick)
            except Exception as e:
                logger.error(f"Handler error: {e}")
        self._routed_count += 1

    def get_routed_count(self) -> int:
        return self._routed_count

    def get_handler_count(self) -> int:
        with self.lock:
            return len(self.handlers)

    def clear_handlers(self):
        with self.lock:
            self.handlers.clear()
            logger.info("All handlers cleared")
