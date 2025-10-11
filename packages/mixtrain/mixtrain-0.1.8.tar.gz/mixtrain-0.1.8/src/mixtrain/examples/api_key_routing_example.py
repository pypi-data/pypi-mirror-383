#!/usr/bin/env python3
"""
Example demonstrating how to use routing configurations with API Key authentication.

This example shows how to:
1. Set up API key authentication
2. Load routing configurations without login
3. Use routing configs in production/automated environments
4. Handle API key errors gracefully

API Keys are useful for:
- Production deployments
- Automated scripts and CI/CD
- Server-to-server communication
- When browser-based login isn't available
"""

import os
import json
from typing import Optional

from mixtrain.client import MixClient
from mixtrain.routing import RoutingEngineFactory


def setup_api_key_auth():
    """Set up API key authentication."""
    print("🔐 Setting up API Key authentication...")

    # Check if API key is already set
    api_key = os.getenv("MIXTRAIN_API_KEY")

    if api_key:
        if api_key.startswith("mix-"):
            print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
            return True
        else:
            print("❌ Invalid API key format. API keys must start with 'mix-'")
            return False
    else:
        print("❌ No API key found in environment variable MIXTRAIN_API_KEY")
        print("\nTo use API key authentication:")
        print("1. Get your API key from the mixtrain.ai dashboard")
        print("2. Set it as environment variable:")
        print("   export MIXTRAIN_API_KEY=mix-your-api-key-here")
        print("3. Or set it programmatically:")
        print("   os.environ['MIXTRAIN_API_KEY'] = 'mix-your-api-key-here'")
        return False


def demonstrate_api_key_usage():
    """Show how to set API key programmatically."""
    print("\n📋 API Key Setup Methods:")

    print("\n1. Environment variable (recommended for production):")
    print("   export MIXTRAIN_API_KEY=mix-your-api-key-here")
    print("   python your_script.py")

    print("\n2. Set programmatically in Python:")
    print("   import os")
    print("   os.environ['MIXTRAIN_API_KEY'] = 'mix-your-key-here'")
    print("   from mixtrain.client import MixClient")
    print("   client = MixClient()  # Workspace auto-detected from API key")

    print("\n3. Docker environment:")
    print("   docker run -e MIXTRAIN_API_KEY=mix-your-key-here your-image")

    print("\n4. CI/CD secrets:")
    print("   # GitHub Actions")
    print("   env:")
    print("     MIXTRAIN_API_KEY: ${{ secrets.MIXTRAIN_API_KEY }}")


def load_configs_with_api_key():
    """Load routing configurations using API key authentication."""
    print("\n🔍 Loading routing configurations with API key...")

    try:
        # List all configurations using API key
        # Workspace is automatically determined from the API key
        client = MixClient()  # Will automatically detect and use API key
        response = client.list_routing_configs()
        configs = response.get("data", [])
        print(f"✅ Successfully loaded {len(configs)} configurations")

        if not configs:
            print("No configurations found in this workspace")
            return None

        # Show configuration summary
        for config in configs:
            status_emoji = {'active': '🟢', 'inactive': '🔴'}.get(config['status'], '⚪')
            print(f"  {status_emoji} {config['name']} (ID: {config['id']}, v{config['version']})")
            print(f"     Status: {config['status']} | Rules: {config['rules_count']}")

        return configs

    except Exception as e:
        print(f"❌ Error loading configurations: {e}")

        # Common API key error handling
        error_str = str(e).lower()
        if "api key" in error_str or "authentication" in error_str:
            print("\n🔧 API Key troubleshooting:")
            print("1. Verify your API key starts with 'mix-'")
            print("2. Check the key hasn't expired")
            print("3. Ensure you have access to this workspace")
            print("4. Try regenerating the API key if needed")

        return None


def production_routing_example():
    """Example of using routing configs in a production environment."""
    print("\n🚀 Production Routing Example...")

    try:
        # Get the active configuration (typical production use case)
        client = MixClient()
        active_response = client.get_active_routing_config()
        active_config = active_response.get("data") if active_response else None

        if not active_config:
            print("❌ No active routing configuration found")
            print("You need to activate a configuration in the frontend first")
            return

        print(f"✅ Active config: {active_config['name']} (v{active_config['version']})")

        # Create routing engine from active config
        engine = RoutingEngineFactory.from_json(active_config['config_data'])
        print(f"✅ Routing engine created with {len(active_config['config_data']['rules'])} rules")

        # Simulate production requests
        production_requests = [
            {
                "request_id": "req_001",
                "user": {"tier": "premium", "region": "us-west", "id": "user123"},
                "request": {"type": "text-generation", "tokens": 1000, "priority": "high"}
            },
            {
                "request_id": "req_002",
                "user": {"tier": "free", "region": "eu-west", "id": "user456"},
                "request": {"type": "image-generation", "size": "1024x1024"}
            },
            {
                "request_id": "req_003",
                "user": {"tier": "enterprise", "region": "ap-south", "id": "corp789"},
                "request": {"type": "text-generation", "tokens": 2000, "model": "gpt-4"}
            }
        ]

        print(f"\n🧪 Processing {len(production_requests)} production requests:")

        for req in production_requests:
            request_id = req.pop("request_id")

            try:
                result = engine.route_request(req)

                if result.matched_rule:
                    print(f"  ✅ {request_id}: Routed via '{result.matched_rule.name}' rule")
                    print(f"     Strategy: {result.matched_rule.strategy}")
                    print(f"     Targets: {len(result.selected_targets)} models")

                    # Show selected models
                    for i, target in enumerate(result.selected_targets):
                        weight_info = f" (weight: {target.weight})" if result.matched_rule.strategy == "split" else ""
                        shadow_info = " [SHADOW]" if getattr(target, 'is_shadow', False) else ""
                        print(f"       {i+1}. {target.provider}/{target.model_name}{weight_info}{shadow_info}")
                else:
                    print(f"  ❌ {request_id}: No rule matched - request would fail")
                    print(f"     Reason: {result.explanation}")

            except Exception as e:
                print(f"  ❌ {request_id}: Routing error - {e}")

            print()  # Empty line between requests

    except Exception as e:
        print(f"❌ Production routing error: {e}")


def test_config_with_api_key():
    """Test a routing configuration using the backend API with API key."""
    print("\n🧪 Testing configuration via API...")

    try:
        client = MixClient()
        response = client.list_routing_configs()
        configs = response.get("data", [])
        if not configs:
            print("No configurations available for testing")
            return

        # Use the first available config for testing
        test_config = configs[0]
        print(f"Testing configuration: {test_config['name']} (ID: {test_config['id']})")

        # Test with sample data
        test_data = {
            "user": {
                "tier": "premium",
                "id": "test_user",
                "region": "us-west"
            },
            "request": {
                "type": "text-generation",
                "tokens": 1000,
                "priority": "high"
            },
            "metadata": {
                "timestamp": "2024-01-15T10:30:00Z",
                "source": "api_test"
            }
        }

        print("Test data:")
        print(json.dumps(test_data, indent=2))

        # Test via backend API
        test_response = client.test_routing_config(test_config['id'], test_data)
        result = test_response.get("data", {})

        print(f"\n📊 Test Results:")
        if result.get('matched_rule'):
            rule = result['matched_rule']
            print(f"  ✅ Matched Rule: {rule['name']}")
            print(f"  📝 Description: {rule.get('description', 'No description')}")
            print(f"  🎯 Strategy: {rule['strategy']}")
            print(f"  🏆 Priority: {rule['priority']}")

            targets = result.get('selected_targets', [])
            print(f"  🎯 Selected {len(targets)} targets:")
            for i, target in enumerate(targets):
                print(f"     {i+1}. {target['provider']}/{target['model_name']}")
                if target.get('weight'):
                    print(f"        Weight: {target['weight']}")
                if target.get('label'):
                    print(f"        Label: {target['label']}")
        else:
            print("  ❌ No rule matched")

        if result.get('explanation'):
            print(f"  💡 Explanation: {result['explanation']}")

    except Exception as e:
        print(f"❌ Testing error: {e}")


def configuration_management_with_api_key():
    """Show configuration management operations with API key."""
    print("\n⚙️ Configuration Management with API Key...")

    try:
        # Show version management
        client = MixClient()
        response = client.list_routing_configs()
        configs = response.get("data", [])
        if not configs:
            print("No configurations available")
            return

        config = configs[0]
        print(f"Managing configuration: {config['name']}")

        # Get version history
        versions_response = client.get_routing_config_versions(config['id'])
        versions = versions_response.get("data", [])
        print(f"📚 Found {len(versions)} versions:")

        for version in versions[:3]:  # Show first 3 versions
            print(f"  v{version['version']} - {version['status']} - {version['created_at'][:10]}")
            print(f"    Change: {version['change_summary']}")
            print(f"    By: {version['created_by']}")

        if len(versions) > 3:
            print(f"  ... and {len(versions) - 3} more versions")

        # Load specific version
        if len(versions) > 1:
            older_version = versions[-1]['version']  # Get oldest version
            print(f"\n📖 Loading version {older_version}...")

            version_response = client.get_routing_config(config['id'], version=older_version)
            version_config = version_response.get("data", {})
            version_rules = version_config.get('rules', [])
            current_rules = config.get('rules', []) if 'rules' in config else []

            print(f"  Version {older_version}: {len(version_rules)} rules")
            print(f"  Current version: {len(current_rules)} rules")
            print(f"  Difference: {len(current_rules) - len(version_rules):+d} rules")

    except Exception as e:
        print(f"❌ Configuration management error: {e}")


def error_handling_examples():
    """Show proper error handling with API keys."""
    print("\n🛡️ Error Handling Examples...")

    # Test with invalid config ID
    try:
        print("Testing invalid config ID...")
        client = MixClient()
        invalid_response = client.get_routing_config(99999)
        invalid_config = invalid_response.get("data")
        print("This shouldn't print")
    except Exception as e:
        print(f"  ✅ Correctly caught error: {e}")

    # Test with invalid test data
    try:
        print("\nTesting with invalid test data...")
        client = MixClient()
        response = client.list_routing_configs()
        configs = response.get("data", [])
        if configs:
            # Use invalid JSON data
            invalid_data = "not json data"
            test_response = client.test_routing_config(configs[0]['id'], invalid_data)
            result = test_response.get("data")
        else:
            print("  No configs available for error testing")
    except Exception as e:
        print(f"  ✅ Correctly caught test error: {e}")


def main():
    """Main function demonstrating API key usage with routing configurations."""
    print("🔑 Mixtrain API Key Routing Configuration Example")
    print("=" * 60)

    # Setup and verify API key
    if not setup_api_key_auth():
        demonstrate_api_key_usage()
        return

    # Load configurations
    configs = load_configs_with_api_key()
    if not configs:
        return

    # Production routing example
    production_routing_example()

    # Test configuration via API
    test_config_with_api_key()

    # Configuration management
    configuration_management_with_api_key()

    # Error handling
    error_handling_examples()

    print("\n✨ API Key example complete!")
    print("\n💡 Key takeaways for production use:")
    print("  • Store API keys securely in environment variables")
    print("  • Handle authentication errors gracefully")
    print("  • Use active configurations for production routing")
    print("  • Test configurations before deploying")
    print("  • Monitor for configuration changes and updates")


if __name__ == "__main__":
    main()