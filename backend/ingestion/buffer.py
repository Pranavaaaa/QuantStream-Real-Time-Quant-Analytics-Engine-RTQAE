"""Tick buffer for QuantStream RTQAE."""

from typing import Dict, List, Optional
from collections import deque
from threading import Lock
from datetime import datetime, timedelta

from storage.models import Tick
from core.logger import get_logger
from core.config import get_config

logger = get_logger("ingestion.buffer")


class TickBuffer:
    """Thread-safe circular buffer for tick data."""

    def __init__(self, max_ticks_per_symbol: int = None):
        config = get_config().buffer
        self.max_ticks = max_ticks_per_symbol or config.max_ticks_per_symbol
        self.buffers: Dict[str, deque] = {}
        self.lock = Lock()
        logger.info(f"Tick buffer initialized (max per symbol: {self.max_ticks})")

    def add(self, tick: Tick):
        with self.lock:
            if tick.symbol not in self.buffers:
                self.buffers[tick.symbol] = deque(maxlen=self.max_ticks)
            self.buffers[tick.symbol].append(tick)

    def get_recent(self, symbol: str, count: int = 100) -> List[Tick]:
        with self.lock:
            if symbol not in self.buffers:
                return []
            buffer = self.buffers[symbol]
            return list(buffer)[-count:]

    def get_by_time(self, symbol: str, seconds: int = 60) -> List[Tick]:
        with self.lock:
            if symbol not in self.buffers:
                return []
            cutoff = datetime.now() - timedelta(seconds=seconds)
            result = []
            for tick in self.buffers[symbol]:
                try:
                    tick_time = datetime.fromisoformat(tick.timestamp.replace('Z', '+00:00'))
                    if tick_time.replace(tzinfo=None) >= cutoff:
                        result.append(tick)
                except:
                    continue
            return result

    def get_latest_price(self, symbol: str) -> Optional[float]:
        with self.lock:
            if symbol not in self.buffers or len(self.buffers[symbol]) == 0:
                return None
            return self.buffers[symbol][-1].price

    def get_all_symbols(self) -> List[str]:
        with self.lock:
            return list(self.buffers.keys())

    def get_stats(self) -> Dict[str, int]:
        with self.lock:
            return {
                'symbols': len(self.buffers),
                'total_ticks': sum(len(b) for b in self.buffers.values()),
                'per_symbol': {s: len(b) for s, b in self.buffers.items()}
            }

    def clear(self, symbol: str = None):
        with self.lock:
            if symbol:
                if symbol in self.buffers:
                    self.buffers[symbol].clear()
            else:
                self.buffers.clear()
