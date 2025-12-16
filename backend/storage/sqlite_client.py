"""SQLite database client for QuantStream RTQAE."""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

from storage.models import Tick, OHLCV, AnalyticMetric, Alert, SCHEMA_SQL
from core.logger import get_logger

logger = get_logger("storage.sqlite")


class SQLiteClient:
    """SQLite database client for persistent storage."""

    def __init__(self, db_path: str = "data/quantstream.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"SQLite client initialized: {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        conn = self._get_connection()
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
            logger.info("Database schema initialized")
        finally:
            conn.close()

    def insert_tick(self, tick: Tick):
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO ticks (symbol, timestamp, price, size, trade_id, is_buyer_maker) VALUES (?, ?, ?, ?, ?, ?)",
                (tick.symbol, tick.timestamp, tick.price, tick.size, tick.trade_id, tick.is_buyer_maker)
            )
            conn.commit()
        finally:
            conn.close()

    def insert_ticks_bulk(self, ticks: List[Tick]):
        if not ticks:
            return
        conn = self._get_connection()
        try:
            conn.executemany(
                "INSERT INTO ticks (symbol, timestamp, price, size, trade_id, is_buyer_maker) VALUES (?, ?, ?, ?, ?, ?)",
                [(t.symbol, t.timestamp, t.price, t.size, t.trade_id, t.is_buyer_maker) for t in ticks]
            )
            conn.commit()
        finally:
            conn.close()

    def insert_ohlcv(self, ohlcv: OHLCV):
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO ohlcv (symbol, timestamp, timeframe, open, high, low, close, volume, trade_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ohlcv.symbol, ohlcv.timestamp, ohlcv.timeframe, ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close, ohlcv.volume, ohlcv.trade_count)
            )
            conn.commit()
        finally:
            conn.close()

    def insert_alert(self, alert: Alert):
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO alerts (symbol, timestamp, rule_type, message, severity, triggered_value, acknowledged) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (alert.symbol, alert.timestamp, alert.rule_type, alert.message, alert.severity.value, alert.triggered_value, alert.acknowledged)
            )
            conn.commit()
        finally:
            conn.close()

    def query_ticks(self, symbol: str = None, start_time: str = None, end_time: str = None, limit: int = 1000) -> List[Dict]:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM ticks WHERE 1=1"
            params = []
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def query_ohlcv(self, symbol: str, timeframe: str = "1min", start_time: str = None, end_time: str = None, limit: int = 500) -> List[Dict]:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM ohlcv WHERE symbol = ? AND timeframe = ?"
            params = [symbol, timeframe]
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def query_alerts(self, symbol: str = None, severity: str = None, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM alerts WHERE 1=1"
            params = []
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def query_analytics(self, symbol: str, metric_name: str = None, start_time: str = None, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM analytics WHERE symbol = ?"
            params = [symbol]
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete_old_ticks(self, days: int = 7):
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM ticks WHERE timestamp < ?", (cutoff,))
            conn.commit()
            logger.info(f"Deleted ticks older than {days} days")
        finally:
            conn.close()

    def vacuum(self):
        conn = self._get_connection()
        try:
            conn.execute("VACUUM")
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, int]:
        conn = self._get_connection()
        try:
            stats = {}
            for table in ['ticks', 'ohlcv', 'analytics', 'alerts']:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            return stats
        finally:
            conn.close()
