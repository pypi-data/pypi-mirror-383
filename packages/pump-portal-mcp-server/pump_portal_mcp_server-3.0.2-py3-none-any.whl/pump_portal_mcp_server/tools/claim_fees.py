"""
Claim Fees Tool

MCP tool for claiming creator fees from PumpPortal.
"""

from fastmcp import FastMCP
from typing import Dict, Any
import logging


def register_claim_fees_tool(server: FastMCP):
    """Register the claim_fees tool with the MCP server."""

    @server.tool()
    def claim_fees() -> Dict[str, Any]:
        """
        Claim creator fees from all your Pump.fun tokens.

        This tool collects accumulated creator fees from all your tokens on Pump.fun.
        Fee collection rewards token creators with a fraction of trading fees.

        Returns:
            Dictionary containing:
            - success: Whether the fee claim succeeded
            - signature: Transaction signature if successful
            - solscanUrl: Solscan URL to view the transaction
            - message: Status message with fee claim details
            - feesClaimed: Amount of fees claimed (if available)

        Notes:
            - Claims fees from all your Pump.fun tokens at once
            - Uses default priority fee (0.000001 SOL)
            - Fees are paid in SOL to your wallet

        Example:
            claim_fees()
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                raise RuntimeError("Trading service not available on server")

            logger.info("Claiming fees from Pump.fun pool...")

            result = trading_service.claim_fees(
                pool="auto",
                mint=None,
                priority_fee=None
            )

            if 'signature' in result:
                logger.info(f"Fee claim successful: {result['signature']}")
                return {
                    "success": True,
                    "signature": result['signature'],
                    "solscanUrl": f"https://solscan.io/tx/{result['signature']}",
                    "message": "Successfully claimed creator fees from all Pump.fun tokens",
                    "details": {
                        "pool": "auto",
                        "tokens": "All tokens",
                        "priorityFee": 0.000001
                    },
                    "feesClaimed": result.get('feesClaimed', 'Amount will be shown in transaction')
                }
            else:
                # Handle error response
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Fee claim failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": f"Failed to claim fees: {error_msg}"
                }

        except Exception as e:
            logger.error(f"Unexpected error claiming fees: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Unexpected error claiming fees: {e}"
            }