# Pump Portal MCP Server Transformation Plan

## Overview
Transform the existing Nano Banana MCP server from AI image generation to a Pump Portal MCP server for Solana blockchain trading operations using only Lightning transactions, based strictly on the provided migration documentation.

## Key Changes Required

### 1. Project Identity & Configuration
- **Package name**: `nanobanana-mcp-server` → `pump-portal-mcp-server`
- **Module name**: `nanobanana_mcp_server` → `pump_portal_mcp_server`
- **Description**: Update from image generation to Solana trading
- **Dependencies**: Replace Gemini/image libraries with requests library for API calls
- **Configuration**: Switch from `GEMINI_API_KEY` to `API_KEY` from wallet creation

### 2. Core Architecture Replacement
- **Services**: Replace image services with trading/wallet services
- **Tools**: Transform image generation tools to Lightning trading operations
- **Resources**: Update from image metadata to token/wallet resources
- **Prompts**: Remove photography prompts, add trading-related prompts

### 3. New MCP Tools to Implement (Lightning API Only)

#### `create_wallet`
- Implement wallet creation via `/api/create-wallet`
- Returns: apiKey, walletPublicKey, privateKey
- No parameters required
- Generated API key used for all subsequent operations

#### `create_token`
- Implement token creation using IPFS metadata + Lightning trade API
- Flow: upload to `/api/ipfs` then create via `/api/trade?api-key=...`
- Parameters: name, symbol, description, twitter, telegram, website, image file, dev buy amount
- Uses action: "create" with the generated API key

#### `buy_token` / `sell_token`
- Implement using Lightning Transaction API only
- Endpoint: `/api/trade?api-key=...`
- Parameters: mint, amount, denominatedInSol, slippage, priorityFee, pool
- PumpPortal handles transaction execution and signing

#### `claim_fees`
- Implement fee collection via `/api/trade?api-key=...` with action "collectCreatorFee"
- Support both "pump" and "meteora-dbc" pool types
- Parameters: priorityFee, pool, mint (optional for meteora-dbc)

### 4. New Services Architecture
- `PortalClient` - HTTP client for pumpportal.fun API endpoints
- `WalletService` - Wallet creation and API key management
- `TradingService` - Lightning trading operations
- `TokenService` - Token creation and IPFS metadata handling

### 5. Configuration Updates

**Required Environment Variables:**
- `API_KEY` - The apiKey from `/api/create-wallet` (replaces GEMINI_API_KEY)

**Optional Environment Variables:**
- `DEFAULT_SLIPPAGE` - Default: `10`
- `DEFAULT_PRIORITY_FEE` - Default: `0.0005` SOL
- `DEFAULT_POOL` - Default: `pump`

### 6. File Structure Changes
- Rename all `nanobanana_mcp_server` directories to `pump_portal_mcp_server`
- Update imports and references across all files
- Replace image-related modules with trading modules

## Implementation Steps
1. Update project configuration (pyproject.toml, package names)
2. Rename main package directory and update all imports
3. Replace service layer with Lightning API trading services
4. Implement 4 core MCP tools: create_wallet, create_token, buy_token/sell_token, claim_fees
5. Update configuration system for API_KEY management
6. Replace resources and prompts for trading context
7. Update documentation and examples
8. Update tests and CI configuration

This transformation leverages the existing robust FastMCP architecture while completely changing from AI image generation to Solana blockchain trading, using only the Lightning API approach for simplified implementation and user experience.