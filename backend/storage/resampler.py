"""Tick to OHLCV resampler for QuantStream RTQAE."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from storage.models import Tick, OHLCV
from core.logger import get_logger

logger = get_logger("storage.resampler")


class CandleBuilder:
    """Builds a single OHLCV candle from ticks."""

    def __init__(self, symbol: str, timeframe: str, start_time: datetime):
        self.symbol = symbol
        self.timeframe = timeframe
        self.start_time = start_time
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = 0.0
        self.trade_count = 0

    def add_tick(self, tick: Tick):
        price = tick.price
        size = tick.size
        if self.open is None:
            self.open = price
        self.high = max(self.high, price) if self.high else price
        self.low = min(self.low, price) if self.low else price
        self.close = price
        self.volume += size
        self.trade_count += 1

    def to_ohlcv(self) -> Optional[OHLCV]:
        if self.open is None:
            return None
        # Use ISO format without the extra 'Z' since we have timezone info
        timestamp_str = self.start_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        return OHLCV(
            symbol=self.symbol,
            timestamp=timestamp_str,
            timeframe=self.timeframe,
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
            trade_count=self.trade_count
        )


class Resampler:
    """Resamples tick data to OHLCV candlesticks."""

    TIMEFRAME_SECONDS = {
        '1s': 1,
        '1m': 60,
        '5m': 300,
        '1min': 60,
        '5min': 300,
        '15min': 900,
        '1hour': 3600,
        '4hour': 14400,
        '1day': 86400
    }

    def __init__(self, timeframes: List[str] = None):
        self.timeframes = timeframes or ['1s', '1m', '5m']
        self.candles: Dict[str, Dict[str, CandleBuilder]] = defaultdict(dict)
        logger.info(f"Resampler initialized with timeframes: {self.timeframes}")

    def add_tick(self, tick: Tick) -> List[OHLCV]:
        completed_candles = []
        try:
            tick_time = datetime.fromisoformat(tick.timestamp.replace('Z', '+00:00'))
        except:
            tick_time = datetime.now()

        for timeframe in self.timeframes:
            candle_start = self._get_candle_start(tick_time, timeframe)
            key = f"{tick.symbol}_{timeframe}"

            if key in self.candles:
                builder = self.candles[key]
                if builder.start_time != candle_start:
                    completed = builder.to_ohlcv()
                    if completed:
                        completed_candles.append(completed)
                    self.candles[key] = CandleBuilder(tick.symbol, timeframe, candle_start)
            else:
                self.candles[key] = CandleBuilder(tick.symbol, timeframe, candle_start)

            self.candles[key].add_tick(tick)

        return completed_candles

    def _get_candle_start(self, tick_time: datetime, timeframe: str) -> datetime:
        seconds = self.TIMEFRAME_SECONDS.get(timeframe, 60)
        timestamp = tick_time.timestamp()
        candle_timestamp = (timestamp // seconds) * seconds
        return datetime.fromtimestamp(candle_timestamp, tz=tick_time.tzinfo)

    def get_current_candle(self, symbol: str, timeframe: str) -> Optional[OHLCV]:
        key = f"{symbol}_{timeframe}"
        if key in self.candles:
            return self.candles[key].to_ohlcv()
        return None

    def clear(self, symbol: str = None):
        if symbol:
            keys_to_delete = [k for k in self.candles if k.startswith(f"{symbol}_")]
            for key in keys_to_delete:
                del self.candles[key]
        else:
            self.candles.clear()
