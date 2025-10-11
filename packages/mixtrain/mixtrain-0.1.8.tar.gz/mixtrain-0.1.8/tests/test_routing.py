"""Tests for the routing engine."""

import pytest
from typing import Dict, Any, List
import json

from mixtrain.routing import (
    RoutingEngine,
    RoutingEngineFactory,
    RoutingConfig,
    RoutingRule,
    RoutingCondition,
    RoutingTarget,
    RoutingStrategy,
    ConditionOperator,
    RoutingValidator,
    ConfigBuilder,
    RoutingConfigValidationError,
    RoutingError,
    ConditionEvaluationError,
    TargetSelectionError,
)
from mixtrain.routing.conditions import ConditionEvaluator
from mixtrain.routing.strategies import TargetSelector


class TestConditionEvaluator:
    """Test condition evaluation logic."""

    def test_equals_condition(self):
        """Test equals condition."""
        condition = RoutingCondition(field="user.tier", operator=ConditionOperator.EQUALS, value="premium")
        request_data = {"user": {"tier": "premium"}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is True

        request_data = {"user": {"tier": "standard"}}
        assert ConditionEvaluator.evaluate_condition(condition, request_data) is False

    def test_not_equals_condition(self):
        """Test not equals condition."""
        condition = RoutingCondition(field="user.tier", operator=ConditionOperator.NOT_EQUALS, value="premium")
        request_data = {"user": {"tier": "standard"}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is True

    def test_in_condition(self):
        """Test in condition."""
        condition = RoutingCondition(field="user.tier", operator=ConditionOperator.IN, value=["premium", "enterprise"])
        request_data = {"user": {"tier": "premium"}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is True

        request_data = {"user": {"tier": "standard"}}
        assert ConditionEvaluator.evaluate_condition(condition, request_data) is False

    def test_contains_condition(self):
        """Test contains condition."""
        condition = RoutingCondition(field="request.type", operator=ConditionOperator.CONTAINS, value="image")
        request_data = {"request": {"type": "image_generation"}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is True

        request_data = {"request": {"type": "text_generation"}}
        assert ConditionEvaluator.evaluate_condition(condition, request_data) is False

    def test_greater_than_condition(self):
        """Test greater than condition."""
        condition = RoutingCondition(field="user.credits", operator=ConditionOperator.GREATER_THAN, value=100)
        request_data = {"user": {"credits": 150}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is True

        request_data = {"user": {"credits": 50}}
        assert ConditionEvaluator.evaluate_condition(condition, request_data) is False

    def test_exists_condition(self):
        """Test exists condition."""
        condition = RoutingCondition(field="user.subscription", operator=ConditionOperator.EXISTS)
        request_data = {"user": {"subscription": "premium"}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is True

        request_data = {"user": {}}
        assert ConditionEvaluator.evaluate_condition(condition, request_data) is False

    def test_regex_condition(self):
        """Test regex condition."""
        condition = RoutingCondition(field="user.email", operator=ConditionOperator.REGEX, value=r".*@company\.com$")
        request_data = {"user": {"email": "user@company.com"}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is True

        request_data = {"user": {"email": "user@gmail.com"}}
        assert ConditionEvaluator.evaluate_condition(condition, request_data) is False

    def test_nested_field_access(self):
        """Test accessing nested fields."""
        condition = RoutingCondition(field="user.profile.tier", operator=ConditionOperator.EQUALS, value="gold")
        request_data = {"user": {"profile": {"tier": "gold"}}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is True

    def test_missing_field(self):
        """Test condition with missing field."""
        condition = RoutingCondition(field="user.nonexistent", operator=ConditionOperator.EQUALS, value="test")
        request_data = {"user": {}}

        assert ConditionEvaluator.evaluate_condition(condition, request_data) is False

    def test_multiple_conditions_and_logic(self):
        """Test multiple conditions with AND logic."""
        conditions = [
            RoutingCondition(field="user.tier", operator=ConditionOperator.EQUALS, value="premium"),
            RoutingCondition(field="request.type", operator=ConditionOperator.EQUALS, value="image")
        ]
        request_data = {
            "user": {"tier": "premium"},
            "request": {"type": "image"}
        }

        assert ConditionEvaluator.evaluate_conditions(conditions, request_data) is True

        # Fail if one condition doesn't match
        request_data["user"]["tier"] = "standard"
        assert ConditionEvaluator.evaluate_conditions(conditions, request_data) is False


class TestTargetSelector:
    """Test target selection strategies."""

    def test_single_strategy(self):
        """Test single target selection."""
        targets = [
            RoutingTarget(provider="modal", model_name="model1", endpoint="http://example1.com"),
            RoutingTarget(provider="modal", model_name="model2", endpoint="http://example2.com")
        ]

        selected = TargetSelector.select_targets(RoutingStrategy.SINGLE, targets, {})
        assert len(selected) == 1
        assert selected[0].model_name == "model1"

    def test_shadow_strategy(self):
        """Test shadow routing strategy."""
        targets = [
            RoutingTarget(provider="modal", model_name="primary", endpoint="http://primary.com"),
            RoutingTarget(provider="modal", model_name="shadow", endpoint="http://shadow.com")
        ]

        selected = TargetSelector.select_targets(RoutingStrategy.SHADOW, targets, {})
        assert len(selected) == 2
        assert not selected[0].is_shadow  # Primary
        assert selected[1].is_shadow      # Shadow

    def test_fallback_strategy(self):
        """Test fallback strategy."""
        targets = [
            RoutingTarget(provider="modal", model_name="primary", endpoint="http://primary.com"),
            RoutingTarget(provider="fal", model_name="fallback", endpoint="http://fallback.com")
        ]

        selected = TargetSelector.select_targets(RoutingStrategy.FALLBACK, targets, {})
        assert len(selected) == 2
        assert selected == targets

    def test_split_strategy_validation(self):
        """Test that split strategy validates weights."""
        targets = [
            RoutingTarget(provider="modal", model_name="model1", endpoint="http://example1.com", weight=0.7),
            RoutingTarget(provider="modal", model_name="model2", endpoint="http://example2.com", weight=0.2)
        ]

        # This should fail validation (weights don't sum to 1.0)
        with pytest.raises(TargetSelectionError):
            rule = RoutingRule(
                name="test",
                strategy=RoutingStrategy.SPLIT,
                targets=targets
            )

    def test_shadow_strategy_validation(self):
        """Test that shadow strategy requires exactly 2 targets."""
        targets = [
            RoutingTarget(provider="modal", model_name="model1", endpoint="http://example1.com")
        ]

        with pytest.raises(TargetSelectionError):
            TargetSelector.select_targets(RoutingStrategy.SHADOW, targets, {})


class TestRoutingEngine:
    """Test the main routing engine."""

    def create_test_config(self) -> RoutingConfig:
        """Create a test routing configuration."""
        return RoutingConfig(
            name="test_config",
            description="Test configuration",
            rules=[
                RoutingRule(
                    name="premium_users",
                    description="Route premium users to premium model",
                    priority=100,
                    conditions=[
                        RoutingCondition(field="user.tier", operator=ConditionOperator.EQUALS, value="premium")
                    ],
                    strategy=RoutingStrategy.SINGLE,
                    targets=[
                        RoutingTarget(provider="modal", model_name="premium-model", endpoint="http://premium.com")
                    ]
                ),
                RoutingRule(
                    name="default_rule",
                    description="Default routing for all other requests",
                    priority=1,
                    conditions=[],  # No conditions = catch-all
                    strategy=RoutingStrategy.SINGLE,
                    targets=[
                        RoutingTarget(provider="modal", model_name="default-model", endpoint="http://default.com")
                    ]
                )
            ]
        )

    def test_rule_matching(self):
        """Test that rules are matched correctly."""
        config = self.create_test_config()
        engine = RoutingEngine(config)

        # Premium user should match premium rule
        request_data = {"user": {"tier": "premium"}}
        result = engine.route_request(request_data)

        assert result.matched_rule is not None
        assert result.matched_rule.name == "premium_users"
        assert len(result.selected_targets) == 1
        assert result.selected_targets[0].model_name == "premium-model"

    def test_default_rule_fallback(self):
        """Test fallback to default rule."""
        config = self.create_test_config()
        engine = RoutingEngine(config)

        # Non-premium user should match default rule
        request_data = {"user": {"tier": "standard"}}
        result = engine.route_request(request_data)

        assert result.matched_rule is not None
        assert result.matched_rule.name == "default_rule"
        assert len(result.selected_targets) == 1
        assert result.selected_targets[0].model_name == "default-model"

    def test_no_rule_matched(self):
        """Test when no rules match."""
        config = RoutingConfig(
            name="test",
            rules=[
                RoutingRule(
                    name="specific_rule",
                    conditions=[
                        RoutingCondition(field="user.tier", operator=ConditionOperator.EQUALS, value="enterprise")
                    ],
                    targets=[
                        RoutingTarget(provider="modal", model_name="enterprise", endpoint="http://enterprise.com")
                    ]
                )
            ]
        )
        engine = RoutingEngine(config)

        request_data = {"user": {"tier": "standard"}}
        result = engine.route_request(request_data)

        assert result.matched_rule is None
        assert len(result.selected_targets) == 0
        assert "No rules matched" in result.explanation

    def test_rule_priority_order(self):
        """Test that rules are evaluated in priority order."""
        config = RoutingConfig(
            name="priority_test",
            rules=[
                RoutingRule(
                    name="low_priority",
                    priority=10,
                    conditions=[
                        RoutingCondition(field="user.tier", operator=ConditionOperator.EQUALS, value="premium")
                    ],
                    targets=[
                        RoutingTarget(provider="modal", model_name="low", endpoint="http://low.com")
                    ]
                ),
                RoutingRule(
                    name="high_priority",
                    priority=100,
                    conditions=[
                        RoutingCondition(field="user.tier", operator=ConditionOperator.EQUALS, value="premium")
                    ],
                    targets=[
                        RoutingTarget(provider="modal", model_name="high", endpoint="http://high.com")
                    ]
                )
            ]
        )
        engine = RoutingEngine(config)

        request_data = {"user": {"tier": "premium"}}
        result = engine.route_request(request_data)

        # Should match the high priority rule
        assert result.matched_rule.name == "high_priority"

    def test_disabled_rules_ignored(self):
        """Test that disabled rules are ignored."""
        config = RoutingConfig(
            name="disabled_test",
            rules=[
                RoutingRule(
                    name="disabled_rule",
                    priority=100,
                    is_enabled=False,
                    conditions=[
                        RoutingCondition(field="user.tier", operator=ConditionOperator.EQUALS, value="premium")
                    ],
                    targets=[
                        RoutingTarget(provider="modal", model_name="disabled", endpoint="http://disabled.com")
                    ]
                ),
                RoutingRule(
                    name="enabled_rule",
                    priority=50,
                    is_enabled=True,
                    conditions=[
                        RoutingCondition(field="user.tier", operator=ConditionOperator.EQUALS, value="premium")
                    ],
                    targets=[
                        RoutingTarget(provider="modal", model_name="enabled", endpoint="http://enabled.com")
                    ]
                )
            ]
        )
        engine = RoutingEngine(config)

        request_data = {"user": {"tier": "premium"}}
        result = engine.route_request(request_data)

        # Should match the enabled rule, not the higher priority disabled one
        assert result.matched_rule.name == "enabled_rule"

    def test_test_request_with_expectation(self):
        """Test the test_request method with expected rule."""
        config = self.create_test_config()
        engine = RoutingEngine(config)

        request_data = {"user": {"tier": "premium"}}
        result = engine.test_request(request_data, expected_rule="premium_users")

        assert result.metadata["is_test"] is True
        assert result.metadata["expected_rule"] == "premium_users"
        assert result.metadata["matched_expected"] is True

        # Test with wrong expectation
        result = engine.test_request(request_data, expected_rule="wrong_rule")
        assert result.metadata["matched_expected"] is False

    def test_rule_coverage_analysis(self):
        """Test rule coverage analysis."""
        config = self.create_test_config()
        engine = RoutingEngine(config)

        test_requests = [
            {"user": {"tier": "premium"}},
            {"user": {"tier": "standard"}},
            {"user": {"tier": "standard"}},
        ]

        coverage = engine.get_rule_coverage(test_requests)

        assert coverage["total_requests"] == 3
        assert coverage["total_rules"] == 2
        assert coverage["covered_rules"] == 2
        assert coverage["coverage_percentage"] == 100.0
        assert coverage["unmatched_requests"] == 0
        assert coverage["rule_hits"]["premium_users"] == 1
        assert coverage["rule_hits"]["default_rule"] == 2


class TestRoutingValidator:
    """Test configuration validation."""

    def test_valid_config(self):
        """Test validation of valid configuration."""
        config = RoutingConfig(
            name="test_config",
            rules=[
                RoutingRule(
                    name="test_rule",
                    targets=[
                        RoutingTarget(provider="modal", model_name="test", endpoint="http://test.com")
                    ]
                )
            ]
        )

        errors = RoutingValidator.validate_config(config)
        assert len(errors) == 0

    def test_empty_config_name(self):
        """Test validation fails for empty config name."""
        config = RoutingConfig(
            name="",
            rules=[
                RoutingRule(
                    name="test_rule",
                    targets=[
                        RoutingTarget(provider="modal", model_name="test", endpoint="http://test.com")
                    ]
                )
            ]
        )

        errors = RoutingValidator.validate_config(config)
        assert any("name is required" in error.lower() for error in errors)

    def test_no_rules(self):
        """Test validation fails when no rules are provided."""
        config = RoutingConfig(name="test", rules=[])

        errors = RoutingValidator.validate_config(config)
        assert any("at least one routing rule" in error.lower() for error in errors)

    def test_duplicate_rule_names(self):
        """Test validation fails for duplicate rule names."""
        config = RoutingConfig(
            name="test",
            rules=[
                RoutingRule(
                    name="duplicate",
                    targets=[RoutingTarget(provider="modal", model_name="test1", endpoint="http://test1.com")]
                ),
                RoutingRule(
                    name="duplicate",
                    targets=[RoutingTarget(provider="modal", model_name="test2", endpoint="http://test2.com")]
                )
            ]
        )

        errors = RoutingValidator.validate_config(config)
        assert any("duplicate" in error.lower() for error in errors)

    def test_invalid_target_weight(self):
        """Test validation fails for invalid target weight."""
        config = RoutingConfig(
            name="test",
            rules=[
                RoutingRule(
                    name="test_rule",
                    targets=[
                        RoutingTarget(provider="modal", model_name="test", endpoint="http://test.com", weight=2.0)
                    ]
                )
            ]
        )

        errors = RoutingValidator.validate_config(config)
        assert any("weight must be between" in error.lower() for error in errors)

    def test_split_strategy_weight_validation(self):
        """Test validation of split strategy weights."""
        config = RoutingConfig(
            name="test",
            rules=[
                RoutingRule(
                    name="split_rule",
                    strategy=RoutingStrategy.SPLIT,
                    targets=[
                        RoutingTarget(provider="modal", model_name="test1", endpoint="http://test1.com", weight=0.6),
                        RoutingTarget(provider="modal", model_name="test2", endpoint="http://test2.com", weight=0.3)
                    ]
                )
            ]
        )

        errors = RoutingValidator.validate_config(config)
        assert any("sum to 1.0" in error for error in errors)


class TestConfigBuilder:
    """Test the configuration builder."""

    def test_simple_config_builder(self):
        """Test building a simple configuration."""
        config = (ConfigBuilder("test", "Test configuration")
                 .add_rule("default", description="Default rule")
                 .add_target("modal", "test-model", "http://test.com")
                 .build())

        assert config.name == "test"
        assert config.description == "Test configuration"
        assert len(config.rules) == 1
        assert config.rules[0].name == "default"
        assert len(config.rules[0].targets) == 1
        assert config.rules[0].targets[0].model_name == "test-model"

    def test_complex_config_builder(self):
        """Test building a complex configuration with conditions."""
        config = (ConfigBuilder("complex", "Complex configuration")
                 .add_rule("premium", priority=100, description="Premium users")
                 .when("user.tier").equals("premium")
                 .use_single_strategy()
                 .add_target("modal", "premium-model", "http://premium.com")
                 .and_rule("default", priority=10, description="Default users")
                 .add_target("modal", "default-model", "http://default.com")
                 .build())

        assert len(config.rules) == 2

        premium_rule = config.rules[0]
        assert premium_rule.name == "premium"
        assert premium_rule.priority == 100
        assert len(premium_rule.conditions) == 1
        assert premium_rule.conditions[0].field == "user.tier"
        assert premium_rule.conditions[0].operator == ConditionOperator.EQUALS
        assert premium_rule.conditions[0].value == "premium"

        default_rule = config.rules[1]
        assert default_rule.name == "default"
        assert default_rule.priority == 10
        assert len(default_rule.conditions) == 0

    def test_split_strategy_builder(self):
        """Test building split strategy configuration."""
        config = (ConfigBuilder("ab_test", "A/B Test")
                 .add_rule("split_test", description="A/B testing")
                 .use_split_strategy()
                 .add_target("modal", "control", "http://control.com", weight=0.7)
                 .with_label("control")
                 .add_target("modal", "variant", "http://variant.com", weight=0.3)
                 .with_label("variant")
                 .build())

        rule = config.rules[0]
        assert rule.strategy == RoutingStrategy.SPLIT
        assert len(rule.targets) == 2
        assert rule.targets[0].weight == 0.7
        assert rule.targets[0].label == "control"
        assert rule.targets[1].weight == 0.3
        assert rule.targets[1].label == "variant"


class TestRoutingEngineFactory:
    """Test routing engine factory methods."""

    def test_from_json(self):
        """Test creating engine from JSON."""
        config_json = {
            "name": "test",
            "description": "Test configuration",
            "rules": [
                {
                    "name": "default",
                    "description": "Default rule",
                    "priority": 0,
                    "is_enabled": True,
                    "conditions": [],
                    "strategy": "single",
                    "targets": [
                        {
                            "provider": "modal",
                            "model_name": "test-model",
                            "endpoint": "http://test.com",
                            "weight": 1.0
                        }
                    ]
                }
            ]
        }

        engine = RoutingEngineFactory.from_json(config_json)
        assert isinstance(engine, RoutingEngine)
        assert engine.config.name == "test"

    def test_create_simple(self):
        """Test creating simple engine."""
        engine = RoutingEngineFactory.create_simple("simple", "http://simple.com")

        assert isinstance(engine, RoutingEngine)
        assert engine.config.name == "simple"
        assert len(engine.config.rules) == 1
        assert engine.config.rules[0].targets[0].endpoint == "http://simple.com"


class TestIntegration:
    """Integration tests."""

    def test_end_to_end_routing(self):
        """Test complete routing workflow."""
        # Create configuration using builder
        config = (ConfigBuilder("production", "Production routing")
                 .add_rule("premium_image", priority=100, description="Premium users for image generation")
                 .when("user.tier").equals("premium")
                 .with_condition("request.type", "equals", "image")
                 .add_modal_target("premium-flux", "premium-flux-app", "generate", "ImageRequest")
                 .and_rule("standard_image", priority=50, description="Standard users for image generation")
                 .when("request.type").equals("image")
                 .add_modal_target("standard-flux", "standard-flux-app", "generate", "ImageRequest")
                 .and_rule("fallback", priority=1, description="Fallback for all other requests")
                 .add_target("fal", "fallback-model", "https://fal.run/fallback")
                 .build())

        # Validate configuration
        errors = RoutingValidator.validate_config(config)
        assert len(errors) == 0

        # Create engine
        engine = RoutingEngine(config)

        # Test premium image request
        request_data = {
            "user": {"tier": "premium"},
            "request": {"type": "image", "prompt": "A beautiful sunset"}
        }

        result = engine.route_request(request_data)
        assert result.matched_rule.name == "premium_image"
        assert result.selected_targets[0].model_name == "premium-flux"

        # Test standard image request
        request_data = {
            "user": {"tier": "standard"},
            "request": {"type": "image", "prompt": "A cat"}
        }

        result = engine.route_request(request_data)
        assert result.matched_rule.name == "standard_image"
        assert result.selected_targets[0].model_name == "standard-flux"

        # Test fallback
        request_data = {
            "user": {"tier": "standard"},
            "request": {"type": "text", "prompt": "Hello world"}
        }

        result = engine.route_request(request_data)
        assert result.matched_rule.name == "fallback"
        assert result.selected_targets[0].provider == "fal"

        # Test coverage
        test_requests = [
            {"user": {"tier": "premium"}, "request": {"type": "image"}},
            {"user": {"tier": "standard"}, "request": {"type": "image"}},
            {"user": {"tier": "standard"}, "request": {"type": "text"}},
        ]

        coverage = engine.get_rule_coverage(test_requests)
        assert coverage["coverage_percentage"] == 100.0


if __name__ == "__main__":
    pytest.main([__file__])