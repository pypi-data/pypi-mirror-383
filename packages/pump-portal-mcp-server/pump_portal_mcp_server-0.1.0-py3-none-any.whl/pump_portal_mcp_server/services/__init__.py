"""Service registry for dependency injection."""

from typing import Optional
from .trading_service import TradingService
from ..config.settings import ServerConfig, TradingConfig

# Global service instances (initialized by the server)
_trading_service: Optional[TradingService] = None


def initialize_services(server_config: ServerConfig, trading_config: TradingConfig):
    """Initialize all services with configurations."""
    global _trading_service

    # Initialize trading service
    _trading_service = TradingService(server_config.api_key, trading_config)


def get_trading_service() -> TradingService:
    """Get the trading service instance."""
    if _trading_service is None:
        raise RuntimeError("Services not initialized. Call initialize_services() first.")
    return _trading_service