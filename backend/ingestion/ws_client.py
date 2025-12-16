"""Binance WebSocket client for QuantStream RTQAE."""

import asyncio
import json
import threading
from typing import List, Callable, Optional
import websockets

from storage.models import Tick
from core.logger import get_logger
from core.config import get_config
from core.utils import current_timestamp_iso

logger = get_logger("ingestion.ws_client")


class BinanceWSClient:
    """WebSocket client for Binance Futures trade streams."""

    def __init__(self, symbols: List[str], on_tick_callback: Callable[[Tick], None] = None):
        self.config = get_config().binance
        self.symbols = [s.lower() for s in symbols]
        self.on_tick_callback = on_tick_callback
        self.running = False
        self._thread = None
        self._loop = None
        self._ws = None
        self._tick_count = 0
        self._connected_symbols = []
        logger.info(f"WebSocket client initialized for symbols: {self.symbols}")

    def start(self):
        if self.running:
            logger.warning("WebSocket client already running")
            return
        self.running = True
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()
        logger.info("WebSocket client started")

    def stop(self):
        self.running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("WebSocket client stopped")

    def _run_async_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            logger.error(f"Async loop error: {e}")
        finally:
            self._loop.close()

    async def _connect_and_listen(self):
        streams = "/".join([f"{s}@trade" for s in self.symbols])
        url = f"{self.config.base_stream_url}/{streams}"
        reconnect_attempts = 0

        while self.running and reconnect_attempts < self.config.max_reconnect_attempts:
            try:
                logger.info(f"Connecting to Binance: {url}")
                async with websockets.connect(url, ping_interval=self.config.ping_interval) as ws:
                    self._ws = ws
                    self._connected_symbols = self.symbols.copy()
                    reconnect_attempts = 0
                    logger.info("Connected to Binance WebSocket")

                    while self.running:
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=30)
                            self._process_message(message)
                        except asyncio.TimeoutError:
                            continue
                        except websockets.ConnectionClosed:
                            logger.warning("WebSocket connection closed")
                            break

            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                reconnect_attempts += 1
                if self.running:
                    await asyncio.sleep(self.config.reconnect_delay)

        if reconnect_attempts >= self.config.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")

    def _process_message(self, message: str):
        try:
            data = json.loads(message)
            if 'e' in data and data['e'] == 'trade':
                tick = Tick(
                    symbol=data['s'].upper(),
                    timestamp=current_timestamp_iso(),
                    price=float(data['p']),
                    size=float(data['q']),
                    trade_id=data.get('t'),
                    is_buyer_maker=data.get('m', False)
                )
                self._tick_count += 1
                if self.on_tick_callback:
                    self.on_tick_callback(tick)
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def get_tick_count(self) -> int:
        return self._tick_count

    def get_connected_symbols(self) -> List[str]:
        return self._connected_symbols
