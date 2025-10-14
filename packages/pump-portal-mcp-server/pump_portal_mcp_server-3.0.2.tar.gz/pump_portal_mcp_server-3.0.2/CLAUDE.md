# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a production-ready **Pump Portal MCP Server** - a Solana blockchain trading server that leverages PumpPortal Lightning API through the FastMCP framework. The codebase implements a complete MCP (Model Context Protocol) server with modular architecture, comprehensive error handling, and production-ready features for cryptocurrency trading operations.

## Development Commands

### Environment Setup
```bash
# Using uv (recommended)
uv sync

# Set up environment (optional at startup - can use create_wallet tool first)
# cp .env.example .env
# Edit .env to add your API_KEY and WALLET_ADDRESS after using create_wallet tool
```

### Running the Server
```bash
# FastMCP CLI (recommended for development)
fastmcp dev pump_portal_mcp_server.server:create_app

# Direct Python execution
python -m pump_portal_mcp_server.server

# HTTP transport mode
FASTMCP_TRANSPORT=http python -m pump_portal_mcp_server.server
```

### Development Workflow
```bash
# Start development server (clean startup)
./scripts/cleanup-ports.sh && fastmcp dev pump_portal_mcp_server.server:create_app

# Code formatting and linting
ruff format .
ruff check .

# Type checking
mypy .

# Run tests
pytest
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

### Git Workflow - Single Commit History

**This repository maintains a single clean commit in its history.** When making changes:

```bash
# 1. ALWAYS increment version in pyproject.toml before committing
# Edit pyproject.toml and bump the version (e.g., 0.1.0 -> 0.1.1)

# 2. Make your changes and stage them
git add -A

# 3. Amend the existing commit (or create new commit if needed)
git commit --amend -m "Pump Portal MCP Server: Complete Solana trading suite with wallet management, token creation, trading, and balance checking"

# 4. Force push to update remote (use with caution)
git push -f origin master

# Alternative: If you have multiple commits, squash into one
git reset --soft HEAD~N  # N = number of commits to squash
git commit -m "Pump Portal MCP Server: Complete Solana trading suite with wallet management, token creation, trading, and balance checking"
git push -f origin master
```

**Important Notes:**
- **ALWAYS increment the version in `pyproject.toml` before pushing** (this triggers PyPI publishing)
- Always use `git push -f` carefully as it rewrites history
- Maintain a single comprehensive commit message describing the full project
- This keeps the repository clean and focused on the current state
- Version bumps should follow semantic versioning (MAJOR.MINOR.PATCH)

## Architecture & Implementation

### Core Architecture Pattern

The codebase follows a **layered architecture** with clear separation of concerns:

1. **Entry Point Layer** (`server.py`) - Application factory and main entry point
2. **Core Layer** (`core/`) - FastMCP server setup and fundamental components
3. **Service Layer** (`services/`) - Business logic and PumpPortal API integration
4. **Tool Layer** (`tools/`) - MCP tool implementations (create_wallet, create_token, trading)
5. **Resource Layer** (`resources/`) - MCP resource implementations (wallet info, trading status)
6. **Prompt Layer** (`prompts/`) - Reusable trading prompts and guidance
7. **Configuration Layer** (`config/`) - Settings management and environment handling
8. **Utilities Layer** (`utils/`) - Shared utilities and helper functions

### Key Components

**Server Factory Pattern** (`server.py:create_app()`):
- Factory function used by FastMCP CLI: `fastmcp dev server:create_app`
- Handles configuration loading, service initialization, and dependency injection
- Returns configured `PumpPortalMCP` instance ready to run

**Service Layer Architecture**:
- `PortalClient`: Low-level HTTP client for PumpPortal API interactions and Helius RPC calls
- `TradingService`: High-level trading operations (wallet creation, token creation, trading, balance checking)
- Global service registry for dependency injection

**MCP Component Registration**:
- Tools: Registered via `register_*_tool()` functions in each tool module
- Resources: Registered via `register_*_resource()` functions
- Prompts: Trading guidance prompts with registration functions

**Available Tools**:
- `create_wallet`: Generate new wallet and API key
- `check_balance`: Get comprehensive wallet balance (SOL + tokens with USD values via Helius RPC + Jupiter API)
- `create_token`: Launch new tokens (uses 50% slippage, 0.00005 SOL priority fee, pump pool)
- `buy_token`: Buy tokens (uses 10% slippage, 0.00005 SOL priority fee, pump pool)
- `sell_token`: Sell tokens (uses 10% slippage, 0.00005 SOL priority fee, pump pool)
- `claim_fees`: Claim creator fees from all Pump.fun tokens (uses 0.000001 SOL priority fee)

### Configuration Management

**Environment-Based Configuration** (`config/settings.py`):
- `ServerConfig`: Server transport, host, port, API key and wallet address management
- `TradingConfig`: Trading defaults (slippage, priority fees, pool types) and Helius API key
- Loads from environment variables
- API key and wallet address are optional at startup (can be set after using create_wallet tool)
- `HELIUS_API_KEY`: Required environment variable for balance checking (no default provided)

**Configuration Priority**:
1. Environment variables
2. `.env` file values
3. Default values in dataclass definitions

**Tool Parameter Simplification**:
All trading tools use hardcoded optimal parameters to simplify the interface:
- `create_token`: Always uses 50% slippage (for high volatility new launches), pump pool
- `buy_token` / `sell_token`: Always use 10% slippage, pump pool
- `claim_fees`: Always uses pump pool with minimal priority fee (0.000001 SOL)
- Priority fees are set to 0.00005 SOL for most operations (balanced speed/cost)

### Dependency Management

**Key Dependencies**:
- `fastmcp>=2.11.0`: MCP server framework
- `requests>=2.31.0`: HTTP client for API calls
- `python-dotenv>=1.0.1`: Environment variable management
- `pydantic>=2.0.0`: Data validation and serialization

**Development Dependencies**:
- `ruff`: Fast Python linter and formatter
- `mypy`: Static type checker
- `pytest`: Testing framework with async support
- `pytest-cov`: Coverage reporting

### Error Handling Strategy

**Layered Error Handling**:
1. **Configuration Errors**: Fail fast at startup with clear messages
2. **Validation Errors**: Input validation with detailed error context
3. **API Errors**: Graceful handling of PumpPortal API failures
4. **Runtime Errors**: Structured logging with error context preservation

**Custom Exception Hierarchy** (`core/exceptions.py`):
- Base exception classes for different error categories
- Context preservation for debugging
- User-friendly error messages vs internal logging

### Trading Operations Pipeline

**Wallet Creation Flow**:
1. Call to `/api/create-wallet` endpoint
2. Response with apiKey, walletPublicKey, privateKey
3. API key used for subsequent Lightning API operations

**Token Creation Flow**:
1. Input validation and image processing
2. IPFS metadata upload via `/api/ipfs`
3. Token creation via `/api/trade` with Lightning API
4. Transaction signature and metadata return

**Trading Flow**:
1. Input validation (mint address, amounts, slippage)
2. Lightning API call via `/api/trade`
3. Transaction execution by PumpPortal infrastructure
4. Result processing with signature and status

**Balance Checking Flow**:
1. Query Helius RPC for SOL balance via `getBalance`
2. Query Helius RPC for token accounts via `getTokenAccountsByOwner`
3. Fetch USD prices for SOL and all tokens from Jupiter API (up to 50 at once)
4. Calculate individual token values and total portfolio value in USD
5. Return comprehensive balance data with SOL, tokens, and USD valuations

### Testing Architecture

**Test Categories** (configured in `pyproject.toml`):
- `unit`: Fast, isolated unit tests
- `integration`: Service integration tests
- `network`: Tests requiring API access
- `slow`: Long-running performance tests

**Coverage Requirements**:
- Minimum 80% coverage (`fail_under = 80`)
- Excludes test files, `__init__.py`, and debugging code
- HTML coverage reports generated in `htmlcov/`

### FastMCP Integration Patterns

**Tool Registration Pattern**:
```python
def register_create_wallet_tool(server: FastMCP):
    @server.tool()
    def create_wallet() -> Dict[str, Any]:
        # Implementation returns structured result
        return {"success": True, "apiKey": "...", "walletPublicKey": "..."}
```

**Resource Registration Pattern**:
```python
def register_wallet_info_resource(server: FastMCP):
    @server.resource("pumpportal://wallet/current")
    def get_wallet_info() -> dict:
        # Returns dict auto-converted to JSON
```

**Prompt Template Pattern**:
```python
def register_trading_prompts(server: FastMCP):
    @server.prompt()
    def token_launch_checklist() -> str:
        # Returns comprehensive guidance text
```

## Production Considerations

### Logging Configuration
- Structured logging with configurable formats (standard/json/detailed)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request correlation and performance timing
- Sensitive data filtering (API keys, private keys)

### Security Features
- Input validation and sanitization
- API key and private key protection in logs
- Error message masking for production (`mask_error_details`)
- Safe handling of base64 image data

### Performance Optimizations
- Connection pooling and reuse for API calls
- Configurable timeouts for network operations
- Memory management for large transactions
- Efficient error handling and retries

### Deployment Support
- Environment-based configuration
- Process management compatibility (systemd, PM2)
- Health check capabilities (when using HTTP transport)
- Docker containerization ready

## Common Issues & Troubleshooting

### FastMCP Development Issues

**Port Conflicts**:
```bash
# Quick fix: Use the cleanup script
./scripts/cleanup-ports.sh

# Then run normally
fastmcp dev pump_portal_mcp_server.server:create_app

# Alternative: Specify different ports
fastmcp dev pump_portal_mcp_server.server:create_app --ui-port 6275 --server-port 6278
```

**JSON Parsing Errors in STDIO**:
- All logging correctly uses `stderr` instead of `stdout`
- MCP STDIO transport requires `stdout` reserved for JSON-RPC messages only
- Application logs go to `stderr` to avoid interfering with MCP communication

### Runtime Configuration

**API Key and Wallet Address Setup**:

The create_wallet tool will display the exact JSON env configuration to add to your MCP server config:
```json
"env": {
  "API_KEY": "your-pumpportal-api-key-here",
  "WALLET_ADDRESS": "your-wallet-public-key-here"
}
```

**Trading Configuration**:
```bash
# Optional trading parameters (note: tools use hardcoded values for simplicity)
export DEFAULT_SLIPPAGE=10
export DEFAULT_PRIORITY_FEE=0.0005
export DEFAULT_POOL=pump
export API_TIMEOUT=30

# Helius API Key (required for balance checking - get free key at https://www.helius.dev/)
export HELIUS_API_KEY=your-helius-api-key-here
```

**Logging Levels**:
```bash
# Debug mode for development
LOG_LEVEL=DEBUG fastmcp dev pump_portal_mcp_server.server:create_app

# Production logging with JSON format
LOG_LEVEL=INFO LOG_FORMAT=json python -m pump_portal_mcp_server.server
```

### Trading Operations

**API Key and Wallet Address Generation**:

You have three options to get your API key and wallet address:

**Option 1: Use the create_wallet tool (Recommended)**
1. Start server (API_KEY and WALLET_ADDRESS are optional at startup)
2. Use `create_wallet` tool to generate new wallet
3. The tool will display a reminder message with the exact JSON env configuration to add
4. Copy the env configuration and add it to your MCP server config
5. Restart server for the changes to take effect

**Option 2: Use PumpPortal web interface**
1. Visit https://pumpportal.fun/trading-api/setup
2. Click 'Create Wallet'
3. Copy the `apiKey` and `walletPublicKey` from the response
4. Set them as environment variables and restart server

**Option 3: Use curl command**
```bash
curl 'https://pumpportal.fun/api/create-wallet'
```
Copy the `apiKey` and `walletPublicKey` from the response, set as environment variables, and restart server.

**Common Trading Errors**:
- **Insufficient SOL**: Ensure wallet has SOL for trading and fees
- **Invalid Mint Address**: Verify token contract address is correct
- **High Slippage**: Adjust slippage settings for volatile markets
- **Network Congestion**: Increase priority fees during high traffic

**Pool Selection Guide**:
- `pump`: New token launches, high volatility (used by all tools)
- `raydium`: Established tokens, better liquidity
- `auto`: Automatic optimal pool selection
- `pump-amm`, `launchlab`, `raydium-cpmm`, `bonk`: Specialized pools

**Balance Checking**:
- Requires `HELIUS_API_KEY` environment variable (get free key at https://www.helius.dev/)
- Uses Helius RPC for blockchain data (`getBalance`, `getTokenAccountsByOwner`)
- Hardcoded base URL: `https://mainnet.helius-rpc.com/?api-key=` + API key from environment
- Uses Jupiter API for USD price data (supports up to 50 tokens per request)
- Returns comprehensive portfolio view: SOL + all SPL tokens with USD values
- Automatically filters out zero-balance token accounts
- Fails with clear error message if HELIUS_API_KEY is not set
- SOL mint address: `So11111111111111111111111111111111111111112`

## Security Best Practices

### API Key Management
- Never commit API keys to version control
- Use environment variables for configuration
- Rotate API keys periodically
- Monitor API key usage and access patterns

### Trading Security
- Use minimum required permissions
- Validate all input parameters
- Implement rate limiting for API calls
- Monitor for suspicious trading activity
- Keep private keys secure and offline when possible

### Operational Security
- Regular security audits of dependencies
- Monitor for vulnerabilities in dependencies
- Use HTTPS for all API communications
- Implement proper error handling without information leakage