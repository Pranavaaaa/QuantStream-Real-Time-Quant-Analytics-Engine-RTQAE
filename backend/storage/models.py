"""Data models for QuantStream RTQAE."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Tick(BaseModel):
    """Tick data model."""
    symbol: str
    timestamp: str
    price: float
    size: float
    trade_id: Optional[int] = None
    is_buyer_maker: Optional[bool] = None


class OHLCV(BaseModel):
    """OHLCV candlestick data model."""
    symbol: str
    timestamp: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: int = 0


class AnalyticMetric(BaseModel):
    """Analytics metric data model."""
    symbol: str
    timestamp: str
    metric_name: str
    metric_value: float
    metadata: Optional[Dict[str, Any]] = None


class Alert(BaseModel):
    """Alert data model."""
    symbol: str
    timestamp: str
    rule_type: str
    message: str
    severity: AlertSeverity = AlertSeverity.MEDIUM
    triggered_value: Optional[float] = None
    acknowledged: bool = False


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ticks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    price REAL NOT NULL,
    size REAL NOT NULL,
    trade_id INTEGER,
    is_buyer_maker INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ticks_symbol ON ticks(symbol);
CREATE INDEX IF NOT EXISTS idx_ticks_timestamp ON ticks(timestamp);

CREATE TABLE IF NOT EXISTS ohlcv (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    trade_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp, timeframe)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol ON ohlcv(symbol);
CREATE INDEX IF NOT EXISTS idx_ohlcv_timestamp ON ohlcv(timestamp);

CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analytics_symbol ON analytics(symbol);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT NOT NULL,
    triggered_value REAL,
    acknowledged INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
"""
