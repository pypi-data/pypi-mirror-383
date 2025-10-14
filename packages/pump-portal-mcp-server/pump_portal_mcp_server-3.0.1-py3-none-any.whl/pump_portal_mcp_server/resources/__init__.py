"""Resources module for FastMCP server."""

from .wallet_info import register_wallet_info_resource, register_trading_status_resource

__all__ = [
    "register_wallet_info_resource",
    "register_trading_status_resource",
]
