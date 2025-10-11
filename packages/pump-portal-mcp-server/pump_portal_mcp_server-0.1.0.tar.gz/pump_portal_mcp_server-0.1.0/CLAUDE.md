# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a production-ready **Pump Portal MCP Server** - a Solana blockchain trading server that leverages PumpPortal Lightning API through the FastMCP framework. The codebase implements a complete MCP (Model Context Protocol) server with modular architecture, comprehensive error handling, and production-ready features for cryptocurrency trading operations.

## Development Commands

### Environment Setup
```bash
# Using uv (recommended)
uv sync

# Set up environment - first create a wallet to get API_KEY
# cp .env.example .env
# Edit .env to add your API_KEY
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
- `PortalClient`: Low-level HTTP client for PumpPortal API interactions
- `TradingService`: High-level trading operations (wallet creation, token creation, trading)
- Global service registry for dependency injection

**MCP Component Registration**:
- Tools: Registered via `register_*_tool()` functions in each tool module
- Resources: Registered via `register_*_resource()` functions
- Prompts: Trading guidance prompts with registration functions

### Configuration Management

**Environment-Based Configuration** (`config/settings.py`):
- `ServerConfig`: Server transport, host, port, API key management
- `TradingConfig`: Trading defaults (slippage, priority fees, pool types)
- Loads from environment variables
- Validates required API keys at startup

**Configuration Priority**:
1. Environment variables
2. `.env` file values
3. Default values in dataclass definitions

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

**API Key Setup**:
```bash
# Required environment variable - obtain from create_wallet tool
export API_KEY=your_pumpportal_api_key_here
```

**Trading Configuration**:
```bash
# Optional trading parameters
export DEFAULT_SLIPPAGE=10
export DEFAULT_PRIORITY_FEE=0.0005
export DEFAULT_POOL=pump
export API_TIMEOUT=30
```

**Logging Levels**:
```bash
# Debug mode for development
LOG_LEVEL=DEBUG fastmcp dev pump_portal_mcp_server.server:create_app

# Production logging with JSON format
LOG_LEVEL=INFO LOG_FORMAT=json python -m pump_portal_mcp_server.server
```

### Trading Operations

**API Key Generation**:
1. Start server temporarily without API_KEY
2. Use `create_wallet` tool to generate new wallet
3. Copy `apiKey` from response
4. Update configuration and restart server

**Common Trading Errors**:
- **Insufficient SOL**: Ensure wallet has SOL for trading and fees
- **Invalid Mint Address**: Verify token contract address is correct
- **High Slippage**: Adjust slippage settings for volatile markets
- **Network Congestion**: Increase priority fees during high traffic

**Pool Selection Guide**:
- `pump`: New token launches, high volatility
- `raydium`: Established tokens, better liquidity
- `auto`: Automatic optimal pool selection
- `pump-amm`, `launchlab`, `raydium-cpmm`, `bonk`: Specialized pools

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