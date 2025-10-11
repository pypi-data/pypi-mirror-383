#!/usr/bin/env python3
"""
Example demonstrating how to work with routing configurations in mixtrain.

This example shows how to:
1. List existing routing configurations
2. Load and inspect a routing configuration
3. Create a new routing configuration
4. Test routing configurations
5. Manage configuration versions
"""

import json
from typing import Dict, Any

from mixtrain.client import MixClient


def main():
    print("🚀 Mixtrain Routing Configuration Example\n")

    # 1. List existing routing configurations
    print("📋 Listing routing configurations...")
    client = MixClient()
    response = client.list_routing_configs()
    configs = response.get("data", [])

    if configs:
        print(f"Found {len(configs)} routing configurations:")
        for config in configs:
            status_icon = "✅" if config["status"] == "active" else "⏸️"
            print(f"  {status_icon} {config['name']} (v{config['version']}) - {config['rules_count']} rules")
    else:
        print("  No routing configurations found")

    # 2. Get the active configuration (if any)
    print("\n🎯 Checking for active routing configuration...")
    active_response = client.get_active_routing_config()
    active_config = active_response.get("data") if active_response else None

    if active_config:
        print(f"Active config: {active_config['name']} (v{active_config['version']})")
        print(f"Description: {active_config['description']}")

        # Show rules summary
        rules = active_config.get('rules', [])
        print(f"Rules ({len(rules)}):")
        for rule in rules[:3]:  # Show first 3 rules
            print(f"  • {rule['name']} (priority: {rule['priority']}) - {rule['strategy']} strategy")
        if len(rules) > 3:
            print(f"  ... and {len(rules) - 3} more rules")

        # 3. Test the active configuration
        print(f"\n🧪 Testing active configuration...")
        test_data = {
            "user": {"tier": "premium", "region": "us-west"},
            "request": {"type": "text-generation", "tokens": 1000}
        }

        try:
            test_response = client.test_routing_config(active_config['id'], test_data)
            test_result = test_response.get("data", {})
            if test_result.get('matched_rule'):
                rule = test_result['matched_rule']
                print(f"✅ Matched rule: {rule['name']} ({rule['strategy']} strategy)")
                print(f"   Targets: {len(test_result.get('selected_targets', []))}")
                print(f"   Explanation: {test_result.get('explanation', 'No explanation')}")
            else:
                print("❌ No rules matched the test data")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("No active routing configuration found")

    # 4. Create a new routing configuration
    print("\n🔧 Creating example routing configuration...")

    example_rules = [
        {
            "name": "premium_users",
            "description": "Route premium users to high-performance models",
            "priority": 10,
            "is_enabled": True,
            "strategy": "single",
            "conditions": [
                {
                    "field": "user.tier",
                    "operator": "equals",
                    "value": "premium"
                }
            ],
            "targets": [
                {
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "endpoint": "https://api.openai.com/v1/chat/completions",
                    "weight": 1.0
                }
            ]
        },
        {
            "name": "default_route",
            "description": "Default routing for all other requests",
            "priority": 1,
            "is_enabled": True,
            "strategy": "fallback",
            "conditions": [],  # No conditions = matches everything
            "targets": [
                {
                    "provider": "openai",
                    "model_name": "gpt-3.5-turbo",
                    "endpoint": "https://api.openai.com/v1/chat/completions",
                    "weight": 0.8
                },
                {
                    "provider": "anthropic",
                    "model_name": "claude-3-sonnet",
                    "endpoint": "https://api.anthropic.com/v1/messages",
                    "weight": 0.2
                }
            ]
        }
    ]

    try:
        new_config_response = client.create_routing_config(
            name="Example Multi-tier Routing",
            description="Example configuration showing premium vs default routing",
            rules=example_rules
        )
        new_config = new_config_response.get("data", {})
        print(f"✅ Created configuration: {new_config['name']} (ID: {new_config['id']})")

        # 5. Load the full configuration we just created
        print(f"\n📖 Loading full configuration...")
        full_config_response = client.get_routing_config(new_config['id'])
        full_config = full_config_response.get("data", {})

        print(f"Configuration: {full_config['name']}")
        print(f"Status: {full_config['status']}")
        print(f"Rules:")

        for rule in full_config['config_data']['rules']:
            conditions_text = f"{len(rule['conditions'])} conditions" if rule['conditions'] else "no conditions"
            targets_text = f"{len(rule['targets'])} targets"
            print(f"  • {rule['name']} (priority {rule['priority']}) - {conditions_text}, {targets_text}")

        # 6. Test the new configuration
        print(f"\n🧪 Testing new configuration...")

        # Test premium user
        premium_test = {
            "user": {"tier": "premium", "id": "user123"},
            "request": {"type": "chat", "model": "auto"}
        }

        premium_result_response = client.test_routing_config(new_config['id'], premium_test)
        result = premium_result_response.get("data", {})
        if result.get('matched_rule'):
            print(f"Premium user → {result['matched_rule']['name']} rule")

        # Test regular user
        regular_test = {
            "user": {"tier": "free", "id": "user456"},
            "request": {"type": "chat", "model": "auto"}
        }

        regular_result_response = client.test_routing_config(new_config['id'], regular_test)
        result = regular_result_response.get("data", {})
        if result.get('matched_rule'):
            print(f"Regular user → {result['matched_rule']['name']} rule")

        # 7. Show configuration versions
        print(f"\n📚 Configuration versions:")
        versions_response = client.get_routing_config_versions(new_config['id'])
        versions = versions_response.get("data", [])
        for version in versions:
            print(f"  v{version['version']} ({version['status']}) - {version['change_summary']}")

    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")

    print(f"\n✨ Example complete!")


def demonstrate_advanced_routing():
    """Show more advanced routing scenarios."""
    print("\n🔥 Advanced Routing Examples")

    # A/B testing configuration
    ab_test_rules = [
        {
            "name": "ab_test_group_a",
            "description": "A/B test group A (50% traffic)",
            "priority": 5,
            "is_enabled": True,
            "strategy": "split",
            "conditions": [
                {
                    "field": "user.ab_group",
                    "operator": "equals",
                    "value": "A"
                }
            ],
            "targets": [
                {
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "endpoint": "https://api.openai.com/v1/chat/completions",
                    "weight": 1.0,
                    "label": "test_model_a"
                }
            ]
        },
        {
            "name": "ab_test_group_b",
            "description": "A/B test group B (50% traffic)",
            "priority": 5,
            "is_enabled": True,
            "strategy": "split",
            "conditions": [
                {
                    "field": "user.ab_group",
                    "operator": "equals",
                    "value": "B"
                }
            ],
            "targets": [
                {
                    "provider": "anthropic",
                    "model_name": "claude-3-sonnet",
                    "endpoint": "https://api.anthropic.com/v1/messages",
                    "weight": 1.0,
                    "label": "test_model_b"
                }
            ]
        }
    ]

    # Shadow traffic configuration
    shadow_rules = [
        {
            "name": "shadow_testing",
            "description": "Shadow traffic to test new model",
            "priority": 8,
            "is_enabled": True,
            "strategy": "shadow",
            "conditions": [
                {
                    "field": "request.shadow_test",
                    "operator": "equals",
                    "value": True
                }
            ],
            "targets": [
                {
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "endpoint": "https://api.openai.com/v1/chat/completions",
                    "weight": 1.0,
                    "is_shadow": False  # Primary
                },
                {
                    "provider": "test_provider",
                    "model_name": "experimental-model-v2",
                    "endpoint": "https://test-api.example.com/v1/chat/completions",
                    "weight": 0.0,
                    "is_shadow": True  # Shadow
                }
            ]
        }
    ]

    print("Advanced routing patterns defined (A/B testing, shadow traffic)")


if __name__ == "__main__":
    main()
    demonstrate_advanced_routing()