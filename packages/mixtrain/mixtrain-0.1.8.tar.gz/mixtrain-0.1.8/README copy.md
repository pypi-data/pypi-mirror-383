# Mixtrain

**Mixtrain** is a Python SDK and CLI for [mixtrain.ai](https://mixtrain.ai) platform.

## Installation

Using uv
```bash
uv add mixtrain
```
or if you use pip

```bash
pip install mixtrain
```

To install mixtrain CLI globally, using uv

```bash
uv tool install mixtrain
```
or if you use pipx

```bash
pipx mixtrain
```

## Quick Start

### Authentication

#### Option 1: Interactive Login (Development)

```bash
mixtrain login
```

#### Option 2: API Key (Production/Automation)

For production deployments, CI/CD, or automated scripts, use API key authentication:

```bash
# Set your API key as an environment variable
export MIXTRAIN_API_KEY=mix-your-api-key-here

# Now you can use mixtrain without login
mixtrain workspace list
```

Or in Python:

```python
import os
os.environ['MIXTRAIN_API_KEY'] = 'mix-your-api-key-here'

import mixtrain.client as mix
configs = mix.list_routing_configs()  # Works without login
```

Get your API key from the [mixtrain.ai dashboard](https://app.mixtrain.ai).

### CLI Usage

Refer to `mixtrain --help` for the full list of commands.

### Python SDK

#### Basic Dataset Operations

```python
import mixtrain.client as mix

# Create a dataset from file (csv or parquet)
mix.create_dataset_from_file("my_dataset", "data.csv", description="My dataset")

# List datasets
datasets = mix.list_datasets()
print(datasets)

# Get direct access to remote dataset
table = mix.get_dataset("my_dataset")

# Scan table data
scan = table.scan(limit=1000)
df = scan.to_polars()  # or .to_pandas() or .to_duckdb("my_dataset")
print(df.head())

```

#### Routing Configuration Management

```python
import mixtrain.client as mix

# List all routing configurations
configs = mix.list_routing_configs()
print(f"Found {len(configs)} configurations")

# Get the currently active configuration
active_config = mix.get_active_routing_config()
if active_config:
    print(f"Active: {active_config['name']} (v{active_config['version']})")

# Load a specific configuration by ID
config = mix.get_routing_config(config_id=1)
rules = config['config_data']['rules']
print(f"Configuration has {len(rules)} routing rules")

# Test a configuration with sample data
test_data = {
    "user": {"tier": "premium", "region": "us-west"},
    "request": {"type": "text-generation", "tokens": 1000}
}
result = mix.test_routing_config(config_id=1, test_data=test_data)
if result['matched_rule']:
    print(f"Matched rule: {result['matched_rule']['name']}")
    print(f"Selected {len(result['selected_targets'])} targets")

# Create a new routing configuration
rules = [
    {
        "name": "premium_users",
        "description": "Route premium users to high-performance models",
        "priority": 10,
        "is_enabled": True,
        "strategy": "single",
        "conditions": [
            {"field": "user.tier", "operator": "equals", "value": "premium"}
        ],
        "targets": [
            {
                "provider": "openai",
                "model_name": "gpt-4",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "weight": 1.0
            }
        ]
    }
]

new_config = mix.create_routing_config(
    name="Premium User Routing",
    description="Routes premium users to GPT-4",
    rules=rules
)
print(f"Created configuration: {new_config['name']} (ID: {new_config['id']})")

# Activate a configuration
mix.activate_routing_config(config_id=new_config['id'])
print(f"Configuration activated!")
```

#### Using Routing Configurations with Local Engine

```python
import mixtrain.client as mix
from mixtrain.routing import RoutingEngineFactory

# Load a configuration from the backend
config = mix.get_routing_config(config_id=1)

# Create a local routing engine from the backend config
engine = RoutingEngineFactory.from_json(config['config_data'])

# Use the engine for local routing decisions
request_data = {
    "user": {"tier": "premium", "id": "user123"},
    "request": {"type": "image-generation"}
}

result = engine.route_request(request_data)
if result.matched_rule:
    print(f"Rule: {result.matched_rule.name}")
    print(f"Strategy: {result.matched_rule.strategy}")
    for target in result.selected_targets:
        print(f"Target: {target.provider}/{target.model_name}")
```

## Routing CLI Commands

The mixtrain CLI includes powerful routing configuration tools:

### Validate Configurations

```bash
# Validate a routing configuration file
mixtrain routing validate config.json

# Get detailed validation with linting suggestions
mixtrain routing validate config.json --verbose
```

### Test Routing

```bash
# Test with inline JSON data
mixtrain routing test config.json --data '{"user": {"tier": "premium"}}'

# Test with a JSON file containing request data
mixtrain routing test config.json --request test_request.json

# Test and verify expected rule matches
mixtrain routing test config.json --data '{"user": {"tier": "free"}}' --expected "default_route"
```

### Configuration Analysis

```bash
# Explain configuration in human-readable format
mixtrain routing explain config.json

# Export as markdown
mixtrain routing explain config.json --format markdown

# Analyze rule coverage with test data
mixtrain routing coverage config.json test_requests.json
```

### Create New Configurations

```bash
# Create configuration interactively
mixtrain routing create "My Config" --interactive

# Create simple configuration with default endpoint
mixtrain routing create "Basic Config" --output config.json
```

## Examples

### Complete Examples

See the `examples/` directory for comprehensive examples:

- `routing_config_example.py` - Create, test, and manage routing configurations
- `load_existing_config.py` - Load and work with existing backend configurations
- `api_key_routing_example.py` - Using routing configs with API key authentication
- `routing/example_usage.py` - Advanced routing engine usage

### Running Examples

```bash
# Run routing configuration example
cd mixtrain && uv run python examples/routing_config_example.py

# Run load existing config example
cd mixtrain && uv run python examples/load_existing_config.py

# Run API key routing example (set MIXTRAIN_API_KEY first)
export MIXTRAIN_API_KEY=mix-your-key-here
cd mixtrain && uv run python examples/api_key_routing_example.py
```

### Production Usage with API Keys

```python
#!/usr/bin/env python3
"""Production routing service example"""
import os
import mixtrain.client as mix
from mixtrain.routing import RoutingEngineFactory

# Set API key (in production, use environment variable)
os.environ['MIXTRAIN_API_KEY'] = 'mix-your-production-api-key'

# Load active routing configuration
active_config = mix.get_active_routing_config()
if not active_config:
    raise RuntimeError("No active routing configuration found")

# Create routing engine
engine = RoutingEngineFactory.from_json(active_config['config_data'])

# Route production requests
def route_request(user_data, request_data):
    """Route a request based on user and request attributes."""
    routing_data = {
        "user": user_data,
        "request": request_data
    }

    result = engine.route_request(routing_data)
    if not result.matched_rule:
        raise RuntimeError("No routing rule matched request")

    return {
        "rule": result.matched_rule.name,
        "strategy": result.matched_rule.strategy,
        "targets": [
            {
                "provider": t.provider,
                "model": t.model_name,
                "endpoint": t.endpoint,
                "weight": t.weight
            }
            for t in result.selected_targets
        ]
    }

# Example usage
routing_result = route_request(
    user_data={"tier": "premium", "region": "us-west"},
    request_data={"type": "text-generation", "tokens": 1000}
)
print(f"Route to: {routing_result['targets'][0]['provider']}/{routing_result['targets'][0]['model']}")
```
