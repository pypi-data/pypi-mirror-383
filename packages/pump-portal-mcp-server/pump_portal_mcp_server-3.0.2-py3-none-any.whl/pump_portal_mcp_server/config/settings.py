from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class ServerConfig:
    """Server configuration settings."""

    api_key: str = ""
    wallet_address: str = ""
    server_name: str = "pump-portal-mcp-server"
    transport: str = "stdio"  # stdio or http
    host: str = "127.0.0.1"
    port: int = 9000
    mask_error_details: bool = False
    max_concurrent_requests: int = 10

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Load configuration from environment variables."""
        load_dotenv()

        return cls(
            api_key=os.getenv("API_KEY", ""),
            wallet_address=os.getenv("WALLET_ADDRESS", ""),
            server_name="pump-portal-mcp-server",
            transport=os.getenv("FASTMCP_TRANSPORT", "stdio"),
            host=os.getenv("FASTMCP_HOST", "127.0.0.1"),
            port=int(os.getenv("FASTMCP_PORT", "9000")),
            mask_error_details=os.getenv("FASTMCP_MASK_ERRORS", "false").lower() == "true",
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
        )


@dataclass
class TradingConfig:
    """Pump Portal trading configuration."""

    default_slippage: int = 10
    default_priority_fee: float = 0.0005  # SOL
    default_pool: str = "auto"
    api_timeout: int = 30  # seconds
    helius_api_key: str = ""

    @classmethod
    def from_env(cls) -> "TradingConfig":
        """Load configuration from environment variables."""
        load_dotenv()

        return cls(
            default_slippage=int(os.getenv("DEFAULT_SLIPPAGE", "10")),
            default_priority_fee=float(os.getenv("DEFAULT_PRIORITY_FEE", "0.0005")),
            default_pool=os.getenv("DEFAULT_POOL", "auto"),
            api_timeout=int(os.getenv("API_TIMEOUT", "30")),
            helius_api_key=os.getenv("HELIUS_API_KEY", ""),
        )
