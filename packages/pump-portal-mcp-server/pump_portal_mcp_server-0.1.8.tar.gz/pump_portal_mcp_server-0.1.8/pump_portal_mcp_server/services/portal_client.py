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

        # Construct Helius RPC URL with API key
        if config.helius_api_key:
            self.helius_rpc_url = f"https://mainnet.helius-rpc.com/?api-key={config.helius_api_key}"
        else:
            self.helius_rpc_url = None

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

    def get_token_accounts(self, wallet_address: str) -> list[Dict[str, Any]]:
        """
        Get all token accounts for a wallet using Helius RPC.

        Args:
            wallet_address: Solana wallet public key

        Returns:
            List of token accounts with mint and amount
        """
        if not self.helius_rpc_url:
            raise ValueError(
                "HELIUS_API_KEY environment variable is required for balance checking. "
                "Please set HELIUS_API_KEY in your environment or .env file."
            )

        rpc_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet_address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        }

        try:
            response = self.session.post(
                self.helius_rpc_url,
                json=rpc_payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                self.logger.error(f"RPC error getting token accounts: {result['error']}")
                return []

            accounts = []
            for account_info in result.get("result", {}).get("value", []):
                parsed = account_info.get("account", {}).get("data", {}).get("parsed", {})
                info = parsed.get("info", {})
                token_amount = info.get("tokenAmount", {})

                # Only include accounts with non-zero balance
                if float(token_amount.get("uiAmount", 0)) > 0:
                    accounts.append({
                        "mint": info.get("mint"),
                        "amount": float(token_amount.get("uiAmount", 0)),
                        "decimals": token_amount.get("decimals", 0)
                    })

            return accounts
        except requests.RequestException as e:
            self.logger.error(f"Failed to get token accounts: {e}")
            return []

    def get_token_prices(self, mint_addresses: list[str]) -> Dict[str, float]:
        """
        Get USD prices for tokens from Jupiter API (up to 50 at once).

        Args:
            mint_addresses: List of token mint addresses (max 50)

        Returns:
            Dictionary mapping mint address to USD price
        """
        if not mint_addresses:
            return {}

        # Jupiter API allows up to 50 mints at once
        mint_addresses = mint_addresses[:50]
        ids_param = ",".join(mint_addresses)

        try:
            response = self.session.get(
                f"https://lite-api.jup.ag/price/v3?ids={ids_param}"
            )
            response.raise_for_status()
            result = response.json()

            # Extract only USD prices
            prices = {}
            for mint, data in result.items():
                if isinstance(data, dict) and "usdPrice" in data:
                    prices[mint] = float(data["usdPrice"])

            return prices
        except requests.RequestException as e:
            self.logger.error(f"Failed to get token prices from Jupiter: {e}")
            return {}

    def get_balance(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get comprehensive wallet balance including SOL and all token holdings with USD values.

        Args:
            wallet_address: Solana wallet public key

        Returns:
            Dictionary containing SOL balance, token holdings, and total USD value
        """
        if not self.helius_rpc_url:
            raise ValueError(
                "HELIUS_API_KEY environment variable is required for balance checking. "
                "Please set HELIUS_API_KEY in your environment or .env file."
            )

        # Get SOL balance
        rpc_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address]
        }

        try:
            response = self.session.post(
                self.helius_rpc_url,
                json=rpc_payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                self.logger.error(f"RPC error: {result['error']}")
                raise Exception(f"RPC error: {result['error']}")

            lamports = result.get("result", {}).get("value", 0)
            sol_balance = lamports / 1_000_000_000

            # Get token accounts
            token_accounts = self.get_token_accounts(wallet_address)

            # Get prices for all tokens including SOL
            mint_addresses = [acc["mint"] for acc in token_accounts]
            # Add SOL mint address
            sol_mint = "So11111111111111111111111111111111111111112"
            if sol_mint not in mint_addresses:
                mint_addresses.insert(0, sol_mint)

            prices = self.get_token_prices(mint_addresses)

            # Calculate SOL value
            sol_price = prices.get(sol_mint, 0)
            sol_value_usd = sol_balance * sol_price

            # Calculate token holdings with USD values
            token_holdings = []
            total_tokens_value_usd = 0

            for account in token_accounts:
                mint = account["mint"]
                amount = account["amount"]
                price = prices.get(mint, 0)
                value_usd = amount * price

                token_holdings.append({
                    "mint": mint,
                    "amount": amount,
                    "usd_price": price,
                    "value_usd": value_usd
                })
                total_tokens_value_usd += value_usd

            # Calculate total wallet value
            total_value_usd = sol_value_usd + total_tokens_value_usd

            return {
                "wallet_address": wallet_address,
                "sol": {
                    "balance": sol_balance,
                    "balance_lamports": lamports,
                    "usd_price": sol_price,
                    "value_usd": sol_value_usd
                },
                "tokens": token_holdings,
                "total_tokens": len(token_holdings),
                "total_tokens_value_usd": total_tokens_value_usd,
                "total_value_usd": total_value_usd
            }
        except requests.RequestException as e:
            self.logger.error(f"Failed to get balance: {e}")
            raise

    def close(self):
        """Close the session."""
        self.session.close()