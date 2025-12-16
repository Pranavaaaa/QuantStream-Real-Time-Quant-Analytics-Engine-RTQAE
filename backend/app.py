"""Main application entrypoint for QuantStream RTQAE."""

import signal
import sys
import uvicorn
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import get_logger, setup_logger
from core.config import get_config
from storage.sqlite_client import SQLiteClient
from storage.resampler import Resampler
from ingestion.ws_client import BinanceWSClient
from ingestion.buffer import TickBuffer
from ingestion.router import DataRouter
from analytics.analytics_engine import AnalyticsEngine
from alerts.engine import AlertEngine
from alerts.rules import create_default_rules
from api.server import create_app, set_app_state

# Initialize logger
setup_logger()
logger = get_logger("main")


class QuantStreamApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = get_config()
        
        # Initialize components
        self.db_client = None
        self.resampler = None
        self.buffer = None
        self.router = None
        self.analytics_engine = None
        self.alert_engine = None
        self.ws_client = None
        self.app = None
        
        logger.info("="*60)
        logger.info("QuantStream - Real-Time Quant Analytics Engine")
        logger.info("="*60)
    
    def setup(self):
        """Set up all components."""
        logger.info("Setting up components...")
        
        # Database
        logger.info("Initializing database...")
        Path(self.config.database.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_client = SQLiteClient(self.config.database.db_path)
        
        # Resampler
        logger.info("Initializing resampler...")
        self.resampler = Resampler(['1s', '1m', '5m'])
        
        # Buffer
        logger.info("Initializing tick buffer...")
        self.buffer = TickBuffer()
        
        # Router
        logger.info("Initializing data router...")
        self.router = DataRouter()
        
        # Analytics engine
        logger.info("Initializing analytics engine...")
        self.analytics_engine = AnalyticsEngine()
        
        # Alert engine
        logger.info("Initializing alert engine...")
        self.alert_engine = AlertEngine(
            db_client=self.db_client,
            cooldown_seconds=self.config.alerts.cooldown_seconds
        )
        
        # Register handlers with router
        self.router.register_handler(self._handle_tick)
        
        # WebSocket client (initialized but not started)
        logger.info("Initializing WebSocket client...")
        default_symbols = ['btcusdt', 'ethusdt']  # Default symbols
        self.ws_client = BinanceWSClient(
            symbols=default_symbols,
            on_tick_callback=self.router.route_tick
        )
        
        # Create FastAPI app
        logger.info("Creating API server...")
        self.app = create_app()
        
        # Set global state for API access
        set_app_state(
            ws_client=self.ws_client,
            buffer=self.buffer,
            analytics_engine=self.analytics_engine,
            alert_engine=self.alert_engine,
            db_client=self.db_client,
            resampler=self.resampler
        )
        
        logger.info("All components initialized successfully!")
    
    def _handle_tick(self, tick):
        """
        Handle incoming tick data.
        
        Args:
            tick: Tick data
        """
        try:
            # Add to buffer
            self.buffer.add(tick)
            
            # Update analytics
            self.analytics_engine.update(tick)
            
            # Get latest stats and z-score
            stats = self.analytics_engine.get_stats(tick.symbol)
            zscore_data = self.analytics_engine.get_zscore(tick.symbol)
            
            # Evaluate alerts
            if stats:
                self.alert_engine.evaluate_stats(stats)
            
            if zscore_data:
                self.alert_engine.evaluate_zscore(zscore_data)
            
            # Resample to OHLCV
            candles = self.resampler.add_tick(tick)
            
            # Store new candles in database
            for candle in candles:
                self.db_client.insert_ohlcv(candle)
            
            # Periodically store ticks to database (every 100 ticks)
            if self.router.get_routed_count() % 100 == 0:
                # Store recent ticks
                recent_ticks = self.buffer.get_recent(tick.symbol, 100)
                if recent_ticks:
                    self.db_client.insert_ticks_bulk(recent_ticks[:50])  # Store in batches
        
        except Exception as e:
            logger.error(f"Error handling tick: {e}")
    
    def run(self):
        """Run the application."""
        try:
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Setup components
            self.setup()
            
            # Create default alert rules
            logger.info("Creating default alert rules...")
            default_rules = create_default_rules(['BTCUSDT', 'ETHUSDT'])
            self.alert_engine.add_rules(default_rules)
            
            # Start API server
            logger.info(f"Starting API server on {self.config.api.host}:{self.config.api.port}")
            logger.info(f"API documentation available at: http://{self.config.api.host}:{self.config.api.port}/docs")
            logger.info("\nTo start data ingestion, use the API endpoint:")
            logger.info(f"  POST http://{self.config.api.host}:{self.config.api.port}/ingestion/start")
            logger.info(f"  or use the Streamlit dashboard")
            logger.info("\nPress Ctrl+C to stop\n")
            
            uvicorn.run(
                self.app,
                host=self.config.api.host,
                port=self.config.api.port,
                log_level=self.config.api.log_level
            )
        
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.shutdown()
            sys.exit(1)
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        logger.info("\nShutdown signal received. Cleaning up...")
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self):
        """Shutdown the application gracefully."""
        logger.info("Shutting down...")
        
        if self.ws_client and self.ws_client.running:
            logger.info("Stopping WebSocket client...")
            self.ws_client.stop()
        
        if self.db_client:
            logger.info("Cleaning up old data...")
            self.db_client.delete_old_ticks(self.config.database.tick_retention_days)
            self.db_client.vacuum()
        
        logger.info("Shutdown complete.")


def main():
    """Main entry point."""
    app = QuantStreamApp()
    app.run()


if __name__ == "__main__":
    main()
