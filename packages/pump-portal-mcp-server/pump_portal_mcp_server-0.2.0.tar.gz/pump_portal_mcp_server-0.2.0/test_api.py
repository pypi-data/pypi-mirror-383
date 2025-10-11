#!/usr/bin/env python3
"""
Test script to verify Pump Portal API integration.
"""

import json
from unittest.mock import Mock, patch
import sys
import os

def test_portal_client():
    """Test PortalClient functionality."""
    print("Testing PortalClient...")

    try:
        from pump_portal_mcp_server.services.portal_client import PortalClient
        from pump_portal_mcp_server.config.settings import TradingConfig

        config = TradingConfig()
        api_key = "test_api_key"

        # Test client creation
        client = PortalClient(api_key, config)
        assert client.api_key == api_key
        assert client.base_url == "https://pumpportal.fun/api"
        print("✅ PortalClient created successfully")

        # Mock create_wallet response
        mock_response = Mock()
        mock_response.json.return_value = {
            "apiKey": "test_generated_key",
            "walletPublicKey": "test_public_key",
            "privateKey": "test_private_key"
        }
        mock_response.raise_for_status.return_value = None

        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            result = client.create_wallet()
            mock_get.assert_called_once_with("https://pumpportal.fun/api/create-wallet")
            assert result["apiKey"] == "test_generated_key"
            assert result["walletPublicKey"] == "test_public_key"
            assert result["privateKey"] == "test_private_key"
            print("✅ create_wallet API call works correctly")

        return True

    except Exception as e:
        print(f"❌ PortalClient test failed: {e}")
        return False

def test_trading_service():
    """Test TradingService functionality."""
    print("\nTesting TradingService...")

    try:
        from pump_portal_mcp_server.services.trading_service import TradingService
        from pump_portal_mcp_server.config.settings import TradingConfig

        config = TradingConfig()
        api_key = "test_api_key"

        # Test service creation
        service = TradingService(api_key, config)
        assert service.api_key == api_key
        assert service.config == config
        print("✅ TradingService created successfully")

        # Mock API responses
        mock_client = Mock()
        mock_client.create_wallet.return_value = {
            "apiKey": "new_api_key",
            "walletPublicKey": "new_wallet_key",
            "privateKey": "new_private_key"
        }

        service.client = mock_client

        # Test wallet creation
        result = service.create_wallet()
        assert result["apiKey"] == "new_api_key"
        assert result["walletPublicKey"] == "new_wallet_key"
        print("✅ TradingService wallet creation works correctly")

        return True

    except Exception as e:
        print(f"❌ TradingService test failed: {e}")
        return False

def test_mcp_tools():
    """Test MCP tool registration."""
    print("\nTesting MCP tools...")

    try:
        from fastmcp import FastMCP
        from pump_portal_mcp_server.tools.create_wallet import register_create_wallet_tool
        from pump_portal_mcp_server.tools.create_token import register_create_token_tool
        from pump_portal_mcp_server.tools.trading import register_trading_tools
        from pump_portal_mcp_server.tools.claim_fees import register_claim_fees_tool

        # Create mock server
        server = FastMCP("test-server")

        # Test tool registration
        register_create_wallet_tool(server)
        register_create_token_tool(server)
        register_trading_tools(server)
        register_claim_fees_tool(server)

        print("✅ All MCP tools registered successfully")

        # Tools are registered via decorators - just verify no exceptions occurred
        print("✅ Tool registration completed without errors")

        return True

    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        return False

def test_configuration():
    """Test configuration with environment variables."""
    print("\nTesting configuration...")

    try:
        from pump_portal_mcp_server.config.settings import TradingConfig

        # Set test environment variables
        os.environ['DEFAULT_SLIPPAGE'] = '12'
        os.environ['DEFAULT_PRIORITY_FEE'] = '0.0008'
        os.environ['DEFAULT_POOL'] = 'raydium'
        os.environ['API_TIMEOUT'] = '45'

        config = TradingConfig.from_env()

        assert config.default_slippage == 12
        assert config.default_priority_fee == 0.0008
        assert config.default_pool == 'raydium'
        assert config.api_timeout == 45

        print("✅ Environment variable configuration works correctly")
        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 Pump Portal MCP Server - API Integration Tests\n")

    tests = [
        test_portal_client,
        test_trading_service,
        test_mcp_tools,
        test_configuration
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n📊 API Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All API tests passed! Server is ready for publishing.")
        return True
    else:
        print("❌ Some API tests failed. Please fix issues before publishing.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)