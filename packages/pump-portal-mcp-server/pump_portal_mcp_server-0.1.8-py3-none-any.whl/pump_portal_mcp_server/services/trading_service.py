"""
Trading Service

High-level service for managing trading operations through PumpPortal API.
"""

import logging
from typing import Dict, Any, Optional, Union
from ..config.settings import TradingConfig
from .portal_client import PortalClient


class TradingService:
    """Service for managing trading operations."""

    def __init__(self, api_key: str, config: TradingConfig):
        self.api_key = api_key
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = PortalClient(api_key, config)

    def create_wallet(self) -> Dict[str, str]:
        """
        Create a new trading wallet.

        Returns:
            Dictionary with apiKey, walletPublicKey, and privateKey
        """
        self.logger.info("Creating new wallet...")
        result = self.client.create_wallet()
        self.logger.info(f"Created wallet: {result['walletPublicKey']}")
        return result

    def create_token(
        self,
        name: str,
        symbol: str,
        description: str,
        dev_buy_amount: float,
        image_data: Optional[bytes] = None,
        image_filename: str = "token.png",
        twitter: Optional[str] = None,
        telegram: Optional[str] = None,
        website: Optional[str] = None,
        slippage: Optional[int] = None,
        priority_fee: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a new token.

        Args:
            name: Token name
            symbol: Token symbol
            description: Token description
            dev_buy_amount: SOL amount for initial dev buy
            image_data: Token image bytes
            image_filename: Image filename
            twitter: Twitter URL
            telegram: Telegram URL
            website: Website URL
            slippage: Slippage percentage
            priority_fee: Priority fee in SOL

        Returns:
            Transaction result
        """
        self.logger.info(f"Creating token {symbol}...")

        # Upload metadata to IPFS
        metadata_uri = self.client.upload_metadata_to_ipfs(
            name=name,
            symbol=symbol,
            description=description,
            twitter=twitter,
            telegram=telegram,
            website=website,
            image_data=image_data,
            image_filename=image_filename
        )

        # Prepare token metadata
        token_metadata = {
            'name': name,
            'symbol': symbol,
            'uri': metadata_uri
        }

        # Generate a random mint address (this would normally be done with a keypair)
        # For now, we'll let the API handle it
        import secrets
        import base58
        import os

        # Create a temporary mint keypair (32 bytes)
        mint_bytes = secrets.token_bytes(32)
        mint_keypair = base58.b58encode(mint_bytes).decode('ascii')

        # Execute token creation
        result = self.client.execute_trade(
            action="create",
            mint=mint_keypair,
            amount=dev_buy_amount,
            denominated_in_sol="true",
            slippage=slippage,
            priority_fee=priority_fee,
            pool="pump",
            token_metadata=token_metadata
        )

        self.logger.info(f"Token creation submitted: {result}")
        return result

    def buy_token(
        self,
        mint: str,
        amount: Union[int, str],
        denominated_in_sol: str = "true",
        slippage: Optional[int] = None,
        priority_fee: Optional[float] = None,
        pool: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Buy tokens.

        Args:
            mint: Token contract address
            amount: Amount to trade
            denominated_in_sol: "true" if amount is SOL, "false" if tokens
            slippage: Slippage percentage
            priority_fee: Priority fee in SOL
            pool: Pool type

        Returns:
            Transaction result
        """
        self.logger.info(f"Buying token {mint}...")
        result = self.client.execute_trade(
            action="buy",
            mint=mint,
            amount=amount,
            denominated_in_sol=denominated_in_sol,
            slippage=slippage,
            priority_fee=priority_fee,
            pool=pool
        )
        self.logger.info(f"Buy transaction: {result}")
        return result

    def sell_token(
        self,
        mint: str,
        amount: Union[int, str],
        denominated_in_sol: str = "false",
        slippage: Optional[int] = None,
        priority_fee: Optional[float] = None,
        pool: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sell tokens.

        Args:
            mint: Token contract address
            amount: Amount to trade (can be percentage like "100%")
            denominated_in_sol: "true" if amount is SOL, "false" if tokens
            slippage: Slippage percentage
            priority_fee: Priority fee in SOL
            pool: Pool type

        Returns:
            Transaction result
        """
        self.logger.info(f"Selling token {mint}...")
        result = self.client.execute_trade(
            action="sell",
            mint=mint,
            amount=amount,
            denominated_in_sol=denominated_in_sol,
            slippage=slippage,
            priority_fee=priority_fee,
            pool=pool
        )
        self.logger.info(f"Sell transaction: {result}")
        return result

    def claim_fees(
        self,
        pool: str = "pump",
        mint: Optional[str] = None,
        priority_fee: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Claim creator fees.

        Args:
            pool: Pool type ("pump" or "meteora-dbc")
            mint: Token mint (required for meteora-dbc)
            priority_fee: Priority fee in SOL

        Returns:
            Transaction result
        """
        self.logger.info(f"Claiming fees for pool {pool}...")
        result = self.client.execute_trade(
            action="collectCreatorFee",
            mint=mint or "",
            amount=0,
            denominated_in_sol="true",
            slippage=10,  # Default slippage for fee claims
            priority_fee=priority_fee or 0.000001,  # Lower fee for claims
            pool=pool
        )
        self.logger.info(f"Fee claim transaction: {result}")
        return result

    def get_balance(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive wallet balance including SOL and all token holdings.

        Args:
            wallet_address: Wallet public key (uses configured wallet if not provided)

        Returns:
            Dictionary containing SOL balance, token holdings, and total USD value
        """
        # Use the configured wallet address if none provided
        from ..config.settings import ServerConfig
        if wallet_address is None:
            config = ServerConfig.from_env()
            wallet_address = config.wallet_address

        self.logger.info(f"Checking balance for wallet {wallet_address}...")
        result = self.client.get_balance(wallet_address)
        self.logger.info(f"Total wallet value: ${result['total_value_usd']:.2f} USD")
        return result

    def close(self):
        """Close the service and cleanup resources."""
        if self.client:
            self.client.close()