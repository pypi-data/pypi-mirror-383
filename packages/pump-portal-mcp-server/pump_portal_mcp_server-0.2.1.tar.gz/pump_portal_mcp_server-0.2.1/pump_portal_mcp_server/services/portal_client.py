"""
PumpPortal API Client

HTTP client for interacting with PumpPortal.fun API endpoints.
"""

import requests
from typing import Dict, Any, Optional, Union
import logging
from ..config.settings import TradingConfig


class PortalClient:
    """Client for PumpPortal API interactions."""

    def __init__(self, api_key: str, config: TradingConfig):
        self.api_key = api_key
        self.config = config
        self.base_url = "https://pumpportal.fun/api"
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "pump-portal-mcp-server/0.1.0"
        })

    def create_wallet(self) -> Dict[str, str]:
        """
        Create a new wallet and API key.

        Returns:
            Dictionary containing apiKey, walletPublicKey, and privateKey
        """
        try:
            response = self.session.get(f"{self.base_url}/create-wallet")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to create wallet: {e}")
            raise

    def upload_metadata_to_ipfs(
        self,
        name: str,
        symbol: str,
        description: str,
        twitter: Optional[str] = None,
        telegram: Optional[str] = None,
        website: Optional[str] = None,
        image_data: Optional[bytes] = None,
        image_filename: str = "token.png"
    ) -> str:
        """
        Upload token metadata to IPFS.

        Args:
            name: Token name
            symbol: Token symbol
            description: Token description
            twitter: Twitter URL
            telegram: Telegram URL
            website: Website URL
            image_data: Image file bytes
            image_filename: Image filename

        Returns:
            IPFS metadata URI
        """
        form_data = {
            'name': name,
            'symbol': symbol,
            'description': description,
            'showName': 'true'
        }

        if twitter:
            form_data['twitter'] = twitter
        if telegram:
            form_data['telegram'] = telegram
        if website:
            form_data['website'] = website

        files = {}
        if image_data:
            files['file'] = (image_filename, image_data, 'image/png')

        try:
            response = requests.post(
                "https://pump.fun/api/ipfs",
                data=form_data,
                files=files
            )
            response.raise_for_status()
            result = response.json()
            return result['metadataUri']
        except requests.RequestException as e:
            self.logger.error(f"Failed to upload metadata to IPFS: {e}")
            raise

    def execute_trade(
        self,
        action: str,
        mint: str,
        amount: Union[int, str],
        denominated_in_sol: str,
        slippage: Optional[int] = None,
        priority_fee: Optional[float] = None,
        pool: Optional[str] = None,
        token_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a trade using the Lightning API.

        Args:
            action: "buy", "sell", "create", or "collectCreatorFee"
            mint: Token contract address
            amount: Amount to trade (SOL or tokens)
            denominated_in_sol: "true" if amount is SOL, "false" if tokens
            slippage: Slippage percentage (uses default if not provided)
            priority_fee: Priority fee in SOL (uses default if not provided)
            pool: Pool type (uses default if not provided)
            token_metadata: Token metadata (required for create action)

        Returns:
            Transaction result containing signature or errors
        """
        data = {
            "action": action,
            "mint": mint,
            "amount": amount,
            "denominatedInSol": denominated_in_sol,
            "slippage": slippage or self.config.default_slippage,
            "priorityFee": priority_fee or self.config.default_priority_fee,
            "pool": pool or self.config.default_pool,
        }

        if token_metadata and action == "create":
            data["tokenMetadata"] = token_metadata

        try:
            response = self.session.post(
                f"{self.base_url}/trade",
                params={"api-key": self.api_key},
                data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to execute trade: {e}")
            raise

    def close(self):
        """Close the session."""
        self.session.close()