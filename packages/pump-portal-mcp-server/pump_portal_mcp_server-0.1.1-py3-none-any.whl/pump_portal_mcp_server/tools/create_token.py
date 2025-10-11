"""
Create Token Tool

MCP tool for creating new tokens on PumpPortal.
"""

from fastmcp import FastMCP
from typing import Dict, Any, Optional
import logging
import base64


def register_create_token_tool(server: FastMCP):
    """Register the create_token tool with the MCP server."""

    @server.tool()
    def create_token(
        name: str,
        symbol: str,
        description: str,
        dev_buy_amount: float,
        image_base64: Optional[str] = None,
        twitter: Optional[str] = None,
        telegram: Optional[str] = None,
        website: Optional[str] = None,
        slippage: Optional[int] = None,
        priority_fee: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a new token on PumpPortal with optional metadata.

        This tool creates a new SPL token on the Solana blockchain through PumpPortal,
        with optional dev buy, metadata, and social links.

        Args:
            name: The name of the token (e.g., "Pump Portal Token")
            symbol: The ticker symbol (e.g., "PPT", max 10 characters)
            description: Description of the token
            dev_buy_amount: Amount of SOL to buy during token creation (minimum 0.01 SOL)
            image_base64: Base64-encoded PNG image for token icon (optional)
            twitter: Twitter URL (optional)
            telegram: Telegram URL (optional)
            website: Website URL (optional)
            slippage: Slippage percentage for dev buy (default: 10)
            priority_fee: Priority fee in SOL for faster execution (default: 0.0005)

        Returns:
            Dictionary containing:
            - success: Whether the token creation succeeded
            - signature: Transaction signature if successful
            - mint: Token contract address if successful
            - solscanUrl: Solscan URL to view the transaction
            - message: Status message

        Example:
            create_token(
                name="My Token",
                symbol="MTK",
                description="A test token created via MCP",
                dev_buy_amount=0.1,
                twitter="https://twitter.com/mytoken",
                website="https://mytoken.com"
            )
        """
        logger = logging.getLogger(__name__)

        try:
            # Get the trading service from the server
            trading_service = getattr(server, 'trading_service', None)
            if not trading_service:
                raise RuntimeError("Trading service not available on server")

            # Validate inputs
            if not name or len(name.strip()) == 0:
                raise ValueError("Token name is required")
            if not symbol or len(symbol.strip()) == 0:
                raise ValueError("Token symbol is required")
            if len(symbol) > 10:
                raise ValueError("Token symbol must be 10 characters or less")
            if dev_buy_amount < 0.01:
                raise ValueError("Dev buy amount must be at least 0.01 SOL")

            # Decode base64 image if provided
            image_data = None
            image_filename = "token.png"
            if image_base64:
                try:
                    # Remove data URL prefix if present
                    if image_base64.startswith('data:image/'):
                        image_base64 = image_base64.split(',')[1]
                    image_data = base64.b64decode(image_base64)
                except Exception as e:
                    raise ValueError(f"Invalid base64 image data: {e}")

            logger.info(f"Creating token {symbol} with {dev_buy_amount} SOL dev buy...")

            result = trading_service.create_token(
                name=name.strip(),
                symbol=symbol.strip().upper(),
                description=description.strip(),
                dev_buy_amount=dev_buy_amount,
                image_data=image_data,
                image_filename=image_filename,
                twitter=twitter.strip() if twitter else None,
                telegram=telegram.strip() if telegram else None,
                website=website.strip() if website else None,
                slippage=slippage,
                priority_fee=priority_fee
            )

            if 'signature' in result:
                logger.info(f"Token creation successful: {result['signature']}")
                return {
                    "success": True,
                    "signature": result['signature'],
                    "mint": result.get('mint', 'Unknown'),
                    "solscanUrl": f"https://solscan.io/tx/{result['signature']}",
                    "message": f"Token {symbol} created successfully with {dev_buy_amount} SOL dev buy",
                    "tokenInfo": {
                        "name": name,
                        "symbol": symbol,
                        "description": description
                    }
                }
            else:
                # Handle error response
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Token creation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": f"Failed to create token {symbol}: {error_msg}"
                }

        except ValueError as e:
            logger.error(f"Validation error creating token: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Validation error: {e}"
            }
        except Exception as e:
            logger.error(f"Unexpected error creating token: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Unexpected error creating token: {e}"
            }