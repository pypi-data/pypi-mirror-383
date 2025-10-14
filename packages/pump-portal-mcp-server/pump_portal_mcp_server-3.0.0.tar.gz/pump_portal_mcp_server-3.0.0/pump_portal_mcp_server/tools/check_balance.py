"""
Check Balance Tool

MCP tool for checking SOL balance of wallets using Helius RPC.
"""

from fastmcp import FastMCP
from typing import Dict, Any, Optional
import logging


def register_check_balance_tool(server: FastMCP):
    """Register the check_balance tool with the MCP server."""

    @server.tool()
    def check_balance(wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Check comprehensive wallet balance including SOL and all token holdings with USD values.

        This tool queries the Solana blockchain via Helius RPC to get SOL balance and all
        token holdings, then fetches current USD prices from Jupiter API to calculate the
        total wallet value.

        Args:
            wallet_address: Solana wallet public key (optional, uses configured wallet if not provided)

        Returns:
            Dictionary containing:
            - success: Whether the balance check succeeded
            - wallet_address: The wallet address that was checked
            - sol: SOL balance with USD value
            - tokens: List of all token holdings with amounts and USD values
            - total_tokens: Number of different tokens held
            - total_tokens_value_usd: Total value of all tokens in USD
            - total_value_usd: Total wallet value in USD (SOL + tokens)
            - solscan_url: URL to view the wallet on Solscan explorer

        Example:
            # Check configured wallet balance
            check_balance()

            # Check specific wallet balance
            check_balance(wallet_address="So11111111111111111111111111111111111111112")
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                raise RuntimeError("Trading service not available on server")

            logger.info(f"Checking comprehensive wallet balance...")
            result = trading_service.get_balance(wallet_address)

            logger.info(f"Total wallet value: ${result['total_value_usd']:.2f} USD")

            # Format message with summary
            sol_info = result['sol']
            message = (
                f"Total Wallet Value: ${result['total_value_usd']:.2f} USD\n"
                f"SOL: {sol_info['balance']:.4f} SOL (${sol_info['value_usd']:.2f})\n"
                f"Tokens: {result['total_tokens']} holdings (${result['total_tokens_value_usd']:.2f})"
            )

            return {
                "success": True,
                "wallet_address": result["wallet_address"],
                "sol": result["sol"],
                "tokens": result["tokens"],
                "total_tokens": result["total_tokens"],
                "total_tokens_value_usd": result["total_tokens_value_usd"],
                "total_value_usd": result["total_value_usd"],
                "message": message,
                "solscan_url": f"https://solscan.io/address/{result['wallet_address']}"
            }

        except Exception as e:
            logger.error(f"Failed to check balance: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check balance. Please verify the wallet address and try again."
            }
