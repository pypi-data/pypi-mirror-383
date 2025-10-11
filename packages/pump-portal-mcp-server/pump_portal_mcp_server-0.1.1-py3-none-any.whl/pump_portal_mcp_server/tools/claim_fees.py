"""
Claim Fees Tool

MCP tool for claiming creator fees from PumpPortal.
"""

from fastmcp import FastMCP
from typing import Dict, Any, Optional
import logging


def register_claim_fees_tool(server: FastMCP):
    """Register the claim_fees tool with the MCP server."""

    @server.tool()
    def claim_fees(
        pool: str = "pump",
        mint: Optional[str] = None,
        priority_fee: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Claim creator fees from token trading activity.

        This tool collects accumulated creator fees from your tokens on either
        Pump.fun or Meteora Dynamic Bonding Curves. Fee collection rewards
        token creators with a fraction of trading fees.

        Args:
            pool: Pool type to claim fees from ("pump" or "meteora-dbc")
            mint: Token contract address (required for meteora-dbc, optional for pump)
            priority_fee: Priority fee in SOL for faster execution (default: 0.000001)

        Returns:
            Dictionary containing:
            - success: Whether the fee claim succeeded
            - signature: Transaction signature if successful
            - solscanUrl: Solscan URL to view the transaction
            - message: Status message with fee claim details
            - feesClaimed: Amount of fees claimed (if available)

        Notes:
            - For "pump" pool: Claims fees from all your Pump.fun tokens at once
            - For "meteora-dbc" pool: Claims fees for a specific token (mint required)
            - Lower priority fees are typically sufficient for fee claims
            - Fees are paid in SOL to your wallet

        Example:
            # Claim all Pump.fun fees
            claim_fees(pool="pump")

            # Claim fees for specific Meteora DBC token
            claim_fees(pool="meteora-dbc", mint="So11111111111111111111111111111111111111112")
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                raise RuntimeError("Trading service not available on server")

            # Validate inputs
            if pool not in ["pump", "meteora-dbc"]:
                raise ValueError("Pool must be 'pump' or 'meteora-dbc'")
            if pool == "meteora-dbc" and not mint:
                raise ValueError("Mint address is required when pool is 'meteora-dbc'")
            if mint and len(mint.strip()) == 0:
                raise ValueError("Token mint address cannot be empty")

            logger.info(f"Claiming fees for pool {pool}{' (mint: ' + mint + ')' if mint else ''}...")

            result = trading_service.claim_fees(
                pool=pool,
                mint=mint.strip() if mint else None,
                priority_fee=priority_fee
            )

            if 'signature' in result:
                logger.info(f"Fee claim successful: {result['signature']}")
                return {
                    "success": True,
                    "signature": result['signature'],
                    "solscanUrl": f"https://solscan.io/tx/{result['signature']}",
                    "message": f"Successfully claimed creator fees from {pool} pool",
                    "details": {
                        "pool": pool,
                        "mint": mint if pool == "meteora-dbc" else "All tokens",
                        "priorityFee": priority_fee or 0.000001
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
                    "message": f"Failed to claim fees from {pool} pool: {error_msg}"
                }

        except ValueError as e:
            logger.error(f"Validation error claiming fees: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Validation error: {e}"
            }
        except Exception as e:
            logger.error(f"Unexpected error claiming fees: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Unexpected error claiming fees: {e}"
            }