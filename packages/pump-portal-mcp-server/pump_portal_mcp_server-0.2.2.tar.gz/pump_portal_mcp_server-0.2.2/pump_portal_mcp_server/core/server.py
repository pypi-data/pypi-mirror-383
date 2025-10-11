from fastmcp import FastMCP
import logging
from ..config.settings import ServerConfig


class PumpPortalMCP:
    """Main FastMCP server class."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize FastMCP server
        self.server = FastMCP(
            name=config.server_name,
            instructions=self._get_server_instructions(),
            mask_error_details=config.mask_error_details,
        )

        # Register components
        self._register_tools()
        self._register_prompts()

    def set_trading_service(self, trading_service):
        """Inject the trading service onto the FastMCP server."""
        self.server.trading_service = trading_service

    def _get_server_instructions(self) -> str:
        """Get server description and instructions."""
        return (
            "This server provides Solana blockchain trading operations through PumpPortal Lightning API. "
            "It allows creating wallets, creating tokens, buying/selling tokens, and claiming creator fees. "
            "All transactions are handled by PumpPortal's infrastructure for reliable execution."
        )

    def _register_tools(self):
        """Register all tools with the server."""
        from ..tools.create_wallet import register_create_wallet_tool
        from ..tools.create_token import register_create_token_tool
        from ..tools.trading import register_trading_tools
        from ..tools.claim_fees import register_claim_fees_tool

        register_create_wallet_tool(self.server)
        register_create_token_tool(self.server)
        register_trading_tools(self.server)
        register_claim_fees_tool(self.server)

  
    def _register_prompts(self):
        """Register all prompts with the server."""
        from ..prompts.trading import register_trading_prompts

        register_trading_prompts(self.server)

    def run(self):
        """Start the server."""
        if self.config.transport == "http":
            self.server.run(transport="http", host=self.config.host, port=self.config.port)
        else:
            self.server.run()
