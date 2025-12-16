"""Configuration management for QuantStream RTQAE."""

from dataclasses import dataclass
from typing import List


@dataclass
class BinanceConfig:
    """Binance WebSocket configuration."""
    base_stream_url: str = "wss://fstream.binance.com/ws"
    reconnect_delay: int = 5
    ping_interval: int = 20
    max_reconnect_attempts: int = 10


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_path: str = "data/quantstream.db"
    tick_retention_days: int = 7
    batch_insert_size: int = 1000


@dataclass
class BufferConfig:
    """In-memory buffer configuration."""
    max_ticks_per_symbol: int = 10000
    cleanup_interval: int = 60


@dataclass
class AnalyticsConfig:
    """Analytics engine configuration."""
    default_window_size: int = 100
    zscore_threshold: float = 3.0
    correlation_min_periods: int = 30
    regression_min_periods: int = 30
    adf_max_lag: int = 10


@dataclass
class AlertConfig:
    """Alert system configuration."""
    price_change_threshold: float = 2.0
    zscore_threshold: float = 3.0
    volume_spike_threshold: float = 3.0
    cooldown_seconds: int = 300


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    log_level: str = "info"
    cors_origins: List[str] = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:8501", "http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]


@dataclass
class Config:
    """Main application configuration."""
    binance: BinanceConfig
    database: DatabaseConfig
    buffer: BufferConfig
    analytics: AnalyticsConfig
    alerts: AlertConfig
    api: APIConfig

    def __init__(self):
        self.binance = BinanceConfig()
        self.database = DatabaseConfig()
        self.buffer = BufferConfig()
        self.analytics = AnalyticsConfig()
        self.alerts = AlertConfig()
        self.api = APIConfig()


config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config
