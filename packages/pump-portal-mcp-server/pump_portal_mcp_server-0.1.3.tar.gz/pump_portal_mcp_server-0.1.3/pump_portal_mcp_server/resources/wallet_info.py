"""
Wallet Info Resource

MCP resource for accessing wallet information and status.
"""

from fastmcp import FastMCP
from typing import Dict, Any
import logging


def register_wallet_info_resource(server: FastMCP):
    """Register the wallet info resource with the MCP server."""

    @server.resource("pumpportal://wallet/current")
    def get_current_wallet_info() -> Dict[str, Any]:
        """
        Get information about the current configured wallet.

        This resource provides details about the wallet currently configured
        in the MCP server, including public key and configuration status.
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                return {
                    "error": "Trading service not available",
                    "configured": False
                }

            # Extract wallet info from API key (simplified - in production you'd
            # make an API call to get wallet details)
            api_key = trading_service.api_key
            has_api_key = bool(api_key and api_key.strip())

            return {
                "configured": has_api_key,
                "hasApiKey": has_api_key,
                "serviceStatus": "active" if has_api_key else "no_api_key",
                "supportedPools": ["pump", "raydium", "pump-amm", "launchlab", "raydium-cpmm", "bonk", "auto"],
                "defaultSlippage": trading_service.config.default_slippage,
                "defaultPriorityFee": trading_service.config.default_priority_fee,
                "defaultPool": trading_service.config.default_pool,
                "message": "Wallet configured and ready for trading" if has_api_key else "API key required for trading"
            }

        except Exception as e:
            logger.error(f"Error getting wallet info: {e}")
            return {
                "error": str(e),
                "configured": False,
                "message": "Failed to get wallet information"
            }


def register_trading_status_resource(server: FastMCP):
    """Register the trading status resource with the MCP server."""

    @server.resource("pumpportal://status/trading")
    def get_trading_status() -> Dict[str, Any]:
        """
        Get current trading service status and capabilities.

        This resource provides information about the trading service,
        including supported operations and current configuration.
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                return {
                    "status": "unavailable",
                    "message": "Trading service not configured"
                }

            return {
                "status": "active",
                "service": "PumpPortal Lightning API",
                "capabilities": [
                    "create_wallet",
                    "create_token",
                    "buy_token",
                    "sell_token",
                    "claim_fees"
                ],
                "supportedPools": {
                    "pump": "Pump.fun tokens",
                    "raydium": "Raydium DEX",
                    "pump-amm": "Pump.fun AMM",
                    "launchlab": "LaunchLab",
                    "raydium-cpmm": "Raydium CPMM",
                    "bonk": "Bonk pool",
                    "auto": "Automatic pool selection"
                },
                "configuration": {
                    "defaultSlippage": trading_service.config.default_slippage,
                    "defaultPriorityFee": trading_service.config.default_priority_fee,
                    "defaultPool": trading_service.config.default_pool,
                    "apiTimeout": trading_service.config.api_timeout
                },
                "endpoints": {
                    "walletCreation": "/api/create-wallet",
                    "ipfsUpload": "https://pump.fun/api/ipfs",
                    "lightningTrading": "/api/trade"
                }
            }

        except Exception as e:
            logger.error(f"Error getting trading status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to get trading status"
            }