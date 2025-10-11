"""
Trading Tools

MCP tools for buying and selling tokens on PumpPortal.
"""

from fastmcp import FastMCP
from typing import Dict, Any, Optional, Union
import logging


def register_trading_tools(server: FastMCP):
    """Register the trading tools with the MCP server."""

    @server.tool()
    def buy_token(
        mint: str,
        amount: Union[int, float],
        denominated_in_sol: str = "true",
        slippage: Optional[int] = None,
        priority_fee: Optional[float] = None,
        pool: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Buy tokens on PumpPortal using the Lightning API.

        This tool executes a buy order for a specified token using the PumpPortal
        Lightning transaction API, which handles transaction signing and execution.

        Args:
            mint: The token contract address (CA) to buy
            amount: Amount to trade (SOL amount if denominated_in_sol is "true")
            denominated_in_sol: "true" if amount is SOL, "false" if amount is token count
            slippage: Slippage percentage (default: 10)
            priority_fee: Priority fee in SOL for faster execution (default: 0.0005)
            pool: Exchange pool (pump, raydium, pump-amm, launchlab, raydium-cpmm, bonk, auto)

        Returns:
            Dictionary containing:
            - success: Whether the buy order succeeded
            - signature: Transaction signature if successful
            - solscanUrl: Solscan URL to view the transaction
            - message: Status message with transaction details

        Example:
            buy_token(
                mint="So11111111111111111111111111111111111111112",
                amount=0.1,
                denominated_in_sol="true",
                slippage=15
            )
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                raise RuntimeError("Trading service not available on server")

            # Validate inputs
            if not mint or len(mint.strip()) == 0:
                raise ValueError("Token mint address is required")
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            if denominated_in_sol not in ["true", "false"]:
                raise ValueError("denominated_in_sol must be 'true' or 'false'")
            if slippage is not None and (slippage < 0 or slippage > 100):
                raise ValueError("Slippage must be between 0 and 100")

            logger.info(f"Buying {amount} {'SOL worth of' if denominated_in_sol == 'true' else ''} token {mint}...")

            result = trading_service.buy_token(
                mint=mint.strip(),
                amount=amount,
                denominated_in_sol=denominated_in_sol,
                slippage=slippage,
                priority_fee=priority_fee,
                pool=pool
            )

            if 'signature' in result:
                logger.info(f"Buy order successful: {result['signature']}")
                return {
                    "success": True,
                    "signature": result['signature'],
                    "solscanUrl": f"https://solscan.io/tx/{result['signature']}",
                    "message": f"Buy order executed successfully for {amount} {'SOL' if denominated_in_sol == 'true' else 'tokens'}",
                    "details": {
                        "mint": mint,
                        "amount": amount,
                        "denominatedInSol": denominated_in_sol,
                        "pool": pool or "default"
                    }
                }
            else:
                # Handle error response
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Buy order failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": f"Failed to execute buy order: {error_msg}"
                }

        except ValueError as e:
            logger.error(f"Validation error buying token: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Validation error: {e}"
            }
        except Exception as e:
            logger.error(f"Unexpected error buying token: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Unexpected error buying token: {e}"
            }

    @server.tool()
    def sell_token(
        mint: str,
        amount: Union[int, float, str],
        denominated_in_sol: str = "false",
        slippage: Optional[int] = None,
        priority_fee: Optional[float] = None,
        pool: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sell tokens on PumpPortal using the Lightning API.

        This tool executes a sell order for a specified token using the PumpPortal
        Lightning transaction API, which handles transaction signing and execution.

        Args:
            mint: The token contract address (CA) to sell
            amount: Amount to trade (token count if denominated_in_sol is "false",
                   can be percentage like "100%" to sell all tokens)
            denominated_in_sol: "true" if amount is SOL, "false" if amount is token count
            slippage: Slippage percentage (default: 10)
            priority_fee: Priority fee in SOL for faster execution (default: 0.0005)
            pool: Exchange pool (pump, raydium, pump-amm, launchlab, raydium-cpmm, bonk, auto)

        Returns:
            Dictionary containing:
            - success: Whether the sell order succeeded
            - signature: Transaction signature if successful
            - solscanUrl: Solscan URL to view the transaction
            - message: Status message with transaction details

        Example:
            sell_token(
                mint="So11111111111111111111111111111111111111112",
                amount="100%",  # Sell all tokens
                denominated_in_sol="false",
                slippage=15
            )
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                raise RuntimeError("Trading service not available on server")

            # Validate inputs
            if not mint or len(mint.strip()) == 0:
                raise ValueError("Token mint address is required")

            # Handle percentage amounts for selling
            if isinstance(amount, str) and amount.endswith('%'):
                # Percentage format is valid for selling
                pass
            elif isinstance(amount, (int, float)) and amount <= 0:
                raise ValueError("Amount must be greater than 0")
            elif denominated_in_sol == "true" and isinstance(amount, (int, float)) and amount <= 0:
                raise ValueError("SOL amount must be greater than 0")

            if denominated_in_sol not in ["true", "false"]:
                raise ValueError("denominated_in_sol must be 'true' or 'false'")
            if slippage is not None and (slippage < 0 or slippage > 100):
                raise ValueError("Slippage must be between 0 and 100")

            logger.info(f"Selling {amount} {'SOL worth of' if denominated_in_sol == 'true' else ''} token {mint}...")

            result = trading_service.sell_token(
                mint=mint.strip(),
                amount=amount,
                denominated_in_sol=denominated_in_sol,
                slippage=slippage,
                priority_fee=priority_fee,
                pool=pool
            )

            if 'signature' in result:
                logger.info(f"Sell order successful: {result['signature']}")
                return {
                    "success": True,
                    "signature": result['signature'],
                    "solscanUrl": f"https://solscan.io/tx/{result['signature']}",
                    "message": f"Sell order executed successfully for {amount} {'SOL' if denominated_in_sol == 'true' else 'tokens'}",
                    "details": {
                        "mint": mint,
                        "amount": amount,
                        "denominatedInSol": denominated_in_sol,
                        "pool": pool or "default"
                    }
                }
            else:
                # Handle error response
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Sell order failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": f"Failed to execute sell order: {error_msg}"
                }

        except ValueError as e:
            logger.error(f"Validation error selling token: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Validation error: {e}"
            }
        except Exception as e:
            logger.error(f"Unexpected error selling token: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Unexpected error selling token: {e}"
            }