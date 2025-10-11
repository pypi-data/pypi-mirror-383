"""
Create Wallet Tool

MCP tool for creating new PumpPortal wallets and API keys.
"""

from fastmcp import FastMCP
from typing import Dict, Any
import logging


def register_create_wallet_tool(server: FastMCP):
    """Register the create_wallet tool with the MCP server."""

    @server.tool()
    def create_wallet() -> Dict[str, Any]:
        """
        Create a new wallet and API key for trading on PumpPortal.

        This tool generates a new Solana wallet with an associated API key that can be used
        for all trading operations. The API key is required for the Lightning Transaction API.

        Returns:
            Dictionary containing:
            - apiKey: The API key for Lightning API operations
            - walletPublicKey: The public key of the generated wallet
            - privateKey: The private key of the generated wallet (keep secure!)

        Security Note:
            - Store the privateKey securely as it provides full access to the wallet
            - The apiKey can be used for trading operations through the Lightning API
            - Never share your private key with anyone
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                raise RuntimeError("Trading service not available on server")

            logger.info("Creating new wallet via MCP tool...")
            result = trading_service.create_wallet()

            logger.info(f"Successfully created wallet: {result['walletPublicKey']}")

            return {
                "success": True,
                "apiKey": result["apiKey"],
                "walletPublicKey": result["walletPublicKey"],
                "privateKey": result["privateKey"],
                "message": "Wallet created successfully. Keep the private key secure!",
                "solscanUrl": f"https://solscan.io/address/{result['walletPublicKey']}"
            }

        except Exception as e:
            logger.error(f"Failed to create wallet: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create wallet. Please try again."
            }