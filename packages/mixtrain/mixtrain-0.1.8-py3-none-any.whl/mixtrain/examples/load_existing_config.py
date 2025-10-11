#!/usr/bin/env python3
"""
Example demonstrating how to load existing routing configurations from the backend.

This example shows how to:
1. List all routing configurations
2. Get the active configuration
3. Load specific configurations by ID
4. Use routing engine locally with backend configs
5. Sync local configs with backend versions
"""

import json
import os
from typing import Optional

from mixtrain.client import MixClient
from mixtrain.routing import RoutingEngineFactory


def list_all_configs():
    """List and display all routing configurations."""
    print("📋 Listing all routing configurations...")

    client = MixClient()
    response = client.list_routing_configs()
    configs = response.get("data", [])

    if not configs:
        print("  No configurations found in this workspace.")
        return

    print(f"Found {len(configs)} configurations:")

    for config in configs:
        status_emoji = {
            'active': '✅',
            'inactive': '⏸️'
        }.get(config['status'], '❓')

        print(f"  {status_emoji} ID {config['id']}: {config['name']} (v{config['version']})")
        print(f"      Status: {config['status']} | Rules: {config['rules_count']}")
        print(f"      Created: {config['created_at'][:10]} by {config['created_by']}")
        if config['description']:
            print(f"      Description: {config['description']}")
        print()


def get_active_config():
    """Get and display the currently active routing configuration."""
    print("🎯 Getting active routing configuration...")

    client = MixClient()
    active_response = client.get_active_routing_config()
    active_config = active_response.get("data") if active_response else None

    if not active_config:
        print("  No active configuration found.")
        return None

    print(f"Active configuration: {active_config['name']} (ID: {active_config['id']})")
    print(f"Version: {active_config['version']} | Status: {active_config['status']}")
    print(f"Description: {active_config['description'] or 'No description'}")

    # Show rules summary
    rules = active_config.get('rules', [])
    print(f"Rules ({len(rules)}):")

    for i, rule in enumerate(rules):
        priority = rule.get('priority', 0)
        strategy = rule.get('strategy', 'unknown')
        enabled = rule.get('is_enabled', True)
        status = '✅' if enabled else '❌'

        print(f"  {i+1}. {status} {rule['name']} (priority: {priority}, strategy: {strategy})")

        # Show conditions summary
        conditions = rule.get('conditions', [])
        if conditions:
            print(f"     Conditions: {len(conditions)} rules")
        else:
            print(f"     Conditions: matches all requests")

        # Show targets summary
        targets = rule.get('targets', [])
        print(f"     Targets: {len(targets)} models")

    return active_config


def load_specific_config(config_id: int, version: Optional[int] = None):
    """Load and inspect a specific configuration."""
    version_text = f" (version {version})" if version else ""
    print(f"📖 Loading configuration {config_id}{version_text}...")

    try:
        client = MixClient()
        config_response = client.get_routing_config(config_id, version=version)
        config = config_response.get("data", {})

        print(f"Configuration: {config['name']}")
        print(f"Status: {config['status']} | Version: {config['version']}")
        print(f"Description: {config['description'] or 'No description'}")
        print(f"Created: {config['created_at'][:10]} by {config['created_by']}")

        # Analyze the configuration
        rules = config.get('rules', [])

        # Count strategies
        strategy_counts = {}
        enabled_rules = 0
        total_targets = 0

        for rule in rules:
            strategy = rule.get('strategy', 'unknown')
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

            if rule.get('is_enabled', True):
                enabled_rules += 1

            total_targets += len(rule.get('targets', []))

        print(f"\nConfiguration Analysis:")
        print(f"  Total rules: {len(rules)}")
        print(f"  Enabled rules: {enabled_rules}")
        print(f"  Total targets: {total_targets}")
        print(f"  Strategy distribution:")
        for strategy, count in strategy_counts.items():
            print(f"    - {strategy}: {count}")

        return config

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None


def use_config_with_routing_engine(config):
    """Use a backend configuration with the local routing engine."""
    print(f"\n🔧 Creating routing engine from backend config...")

    try:
        # Create routing engine from config data
        engine = RoutingEngineFactory.from_json(config['config_data'])

        print(f"✅ Routing engine created successfully")
        print(f"Engine has {len(config['config_data']['rules'])} rules loaded")

        # Test some sample requests
        test_cases = [
            {
                "name": "Premium user request",
                "data": {
                    "user": {"tier": "premium", "id": "user123"},
                    "request": {"type": "text-generation", "tokens": 1000}
                }
            },
            {
                "name": "Regular user request",
                "data": {
                    "user": {"tier": "free", "id": "user456"},
                    "request": {"type": "text-generation", "tokens": 500}
                }
            },
            {
                "name": "High priority request",
                "data": {
                    "request": {"priority": "high", "type": "image-generation"},
                    "user": {"region": "us-west"}
                }
            }
        ]

        print(f"\n🧪 Testing routing engine with sample requests:")

        for test_case in test_cases:
            print(f"\n  Testing: {test_case['name']}")

            try:
                result = engine.route_request(test_case['data'])

                if result.matched_rule:
                    print(f"    ✅ Matched rule: {result.matched_rule.name}")
                    print(f"    Strategy: {result.matched_rule.strategy}")
                    print(f"    Selected {len(result.selected_targets)} targets")

                    for i, target in enumerate(result.selected_targets):
                        print(f"      {i+1}. {target.provider}/{target.model_name} (weight: {target.weight})")

                    print(f"    Explanation: {result.explanation}")
                else:
                    print(f"    ❌ No rule matched")
                    print(f"    Explanation: {result.explanation}")

            except Exception as e:
                print(f"    ❌ Error testing request: {e}")

        return engine

    except Exception as e:
        print(f"❌ Error creating routing engine: {e}")
        return None


def sync_config_versions():
    """Show how to work with different versions of a configuration."""
    print(f"\n📚 Working with configuration versions...")

    client = MixClient()
    response = client.list_routing_configs()
    configs = response.get("data", [])
    if not configs:
        print("No configurations available to demonstrate versions")
        return

    # Take the first config as example
    config = configs[0]
    config_id = config['id']

    print(f"Getting versions for: {config['name']} (ID: {config_id})")

    try:
        versions_response = client.get_routing_config_versions(config_id)
        versions = versions_response.get("data", [])

        print(f"Found {len(versions)} versions:")
        for version in versions:
            print(f"  v{version['version']} ({version['status']}) - {version['created_at'][:10]}")
            print(f"    Change: {version['change_summary']}")
            print(f"    By: {version['created_by']}")

        # Load different versions
        if len(versions) > 1:
            print(f"\n📖 Comparing versions...")

            latest_version = versions[0]['version']  # Versions are returned in desc order
            older_version = versions[-1]['version'] if len(versions) > 1 else latest_version

            # Load both versions
            latest_response = client.get_routing_config(config_id, version=latest_version)
            older_response = client.get_routing_config(config_id, version=older_version)
            latest_config = latest_response.get("data", {})
            older_config = older_response.get("data", {})

            latest_rules = latest_config.get('rules', [])
            older_rules = older_config.get('rules', [])

            print(f"  Version {latest_version}: {len(latest_rules)} rules")
            print(f"  Version {older_version}: {len(older_rules)} rules")
            print(f"  Rules difference: {len(latest_rules) - len(older_rules):+d}")

    except Exception as e:
        print(f"❌ Error getting versions: {e}")


def save_config_locally(config, filename: Optional[str] = None):
    """Save a backend configuration to a local file."""
    if not filename:
        safe_name = config['name'].lower().replace(' ', '-').replace('/', '-')
        filename = f"routing-config-{safe_name}-v{config['version']}.json"

    print(f"\n💾 Saving configuration to: {filename}")

    try:
        # Create a format that works with the CLI tools
        export_data = {
            "metadata": {
                "exportedAt": config['updated_at'],
                "exportedBy": "mixtrain SDK",
                "originalName": config['name'],
                "originalId": config['id'],
                "version": config['version']
            },
            "config": {
                "name": config['name'],
                "description": config['description'] or '',
                "rules": config['config_data']['rules']
            }
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"✅ Configuration saved successfully")
        print(f"You can now use this with: mixtrain routing validate {filename}")

        return filename

    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return None


def main():
    print("🚀 Loading Existing Routing Configurations Example\n")

    # 1. List all configurations
    list_all_configs()

    # 2. Get the active configuration
    active_config = get_active_config()

    # 3. If we have an active config, work with it
    if active_config:
        print(f"\n{'='*60}")
        print(f"Working with active configuration: {active_config['name']}")
        print(f"{'='*60}")

        # Load full configuration details
        full_config = load_specific_config(active_config['id'])

        if full_config:
            # Use with routing engine
            engine = use_config_with_routing_engine(full_config)

            # Show version history
            sync_config_versions()

            # Save locally
            local_file = save_config_locally(full_config)

            if local_file and os.path.exists(local_file):
                print(f"\n🔧 Testing saved file with CLI:")
                print(f"  mixtrain routing validate {local_file}")
                print(f"  mixtrain routing explain {local_file}")
                print(f"  mixtrain routing test {local_file} -d '{{\"user\": {{\"tier\": \"premium\"}}}}'")

    # 4. Show how to list configs by status
    print(f"\n📊 Configurations by status:")

    for status in ['active', 'inactive']:
        client = MixClient()
        status_response = client.list_routing_configs(status=status)
        status_configs = status_response.get("data", [])
        print(f"  {status}: {len(status_configs)} configurations")

        for config in status_configs[:2]:  # Show first 2 of each status
            print(f"    - {config['name']} (v{config['version']})")

    print(f"\n✨ Example complete!")
    print(f"\nNext steps:")
    print(f"  • Test configurations: client.test_routing_config(config_id, test_data)")
    print(f"  • Activate configs: client.activate_routing_config(config_id)")
    print(f"  • Create new configs: client.create_routing_config(name, desc, rules)")
    print(f"  • Use CLI tools with exported configs for validation and testing")


if __name__ == "__main__":
    main()