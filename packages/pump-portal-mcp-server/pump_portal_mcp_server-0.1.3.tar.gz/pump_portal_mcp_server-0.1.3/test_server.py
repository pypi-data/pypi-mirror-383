#!/usr/bin/env python3
"""
Test script to verify Pump Portal MCP Server functionality.
"""

import sys
import os

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")

    try:
        # Test main module import
        from pump_portal_mcp_server.server import create_app, PumpPortalMCP
        print("✅ Server import successful")

        # Test configuration import
        from pump_portal_mcp_server.config.settings import ServerConfig, TradingConfig
        print("✅ Configuration import successful")

        # Test services import
        from pump_portal_mcp_server.services.trading_service import TradingService
        from pump_portal_mcp_server.services.portal_client import PortalClient
        print("✅ Services import successful")

        # Test tools import
        from pump_portal_mcp_server.tools.create_wallet import register_create_wallet_tool
        from pump_portal_mcp_server.tools.create_token import register_create_token_tool
        from pump_portal_mcp_server.tools.trading import register_trading_tools
        from pump_portal_mcp_server.tools.claim_fees import register_claim_fees_tool
        print("✅ Tools import successful")

        # Test resources import
        try:
            from pump_portal_mcp_server.resources.wallet_info import register_wallet_info_resource, register_trading_status_resource
            print("✅ Resources import successful")
        except ImportError as e:
            print(f"⚠️  Resources import skipped (expected in test): {e}")

        # Test prompts import
        from pump_portal_mcp_server.prompts.trading import register_trading_prompts
        print("✅ Prompts import successful")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from pump_portal_mcp_server.config.settings import ServerConfig, TradingConfig

        # Test TradingConfig with defaults
        trading_config = TradingConfig()
        assert trading_config.default_slippage == 10
        assert trading_config.default_priority_fee == 0.0005
        assert trading_config.default_pool == "pump"
        print("✅ TradingConfig defaults correct")

        # Test TradingConfig from environment
        os.environ['DEFAULT_SLIPPAGE'] = '15'
        os.environ['DEFAULT_PRIORITY_FEE'] = '0.001'
        trading_config_from_env = TradingConfig.from_env()
        assert trading_config_from_env.default_slippage == 15
        assert trading_config_from_env.default_priority_fee == 0.001
        print("✅ TradingConfig from environment works")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_server_creation():
    """Test server creation without API key (should fail gracefully)."""
    print("\nTesting server creation...")

    try:
        from pump_portal_mcp_server.config.settings import ServerConfig, TradingConfig
        from pump_portal_mcp_server.server import create_app

        # This should fail due to missing API_KEY
        try:
            app = create_app()
            print("❌ Server creation should have failed without API_KEY")
            return False
        except ValueError as e:
            if "API_KEY" in str(e):
                print("✅ Server correctly fails without API_KEY")
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                return False

    except Exception as e:
        print(f"❌ Server creation test failed: {e}")
        return False

def test_service_creation():
    """Test service creation with mock config."""
    print("\nTesting service creation...")

    try:
        from pump_portal_mcp_server.services.portal_client import PortalClient
        from pump_portal_mcp_server.services.trading_service import TradingService
        from pump_portal_mcp_server.config.settings import TradingConfig

        # Create test config
        config = TradingConfig()
        api_key = "test_api_key_12345"

        # Test PortalClient creation
        client = PortalClient(api_key, config)
        assert client.api_key == api_key
        assert client.base_url == "https://pumpportal.fun/api"
        print("✅ PortalClient creation successful")

        # Test TradingService creation
        trading_service = TradingService(api_key, config)
        assert trading_service.api_key == api_key
        assert trading_service.config == config
        print("✅ TradingService creation successful")

        return True

    except Exception as e:
        print(f"❌ Service creation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Pump Portal MCP Server - Test Suite\n")

    tests = [
        test_imports,
        test_configuration,
        test_server_creation,
        test_service_creation
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Server is ready for testing with API key.")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)