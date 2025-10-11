"""
Mixtrain Routing Engine

A standalone routing engine for intelligent model selection and traffic management.
Supports multiple routing strategies, conditional logic, and provider-agnostic configuration.
"""

from .engine import RoutingEngine, RoutingEngineFactory
from .models import (
    RoutingConfig,
    RoutingRule,
    RoutingCondition,
    RoutingTarget,
    RoutingResult,
    RoutingStrategy,
    ConditionOperator,
)
from .validator import RoutingValidator, ConfigurationLinter
from .builder import ConfigBuilder, RuleBuilder
from .executor import (
    FallbackExecutor,
    ExecutionResult,
    FallbackExecutionResult,
    ExecutionStatus,
    ModelProvider,
    ProviderRegistry,
    execute_fallback,
)
from .exceptions import (
    RoutingError,
    ConfigurationError,
    RoutingConfigValidationError,
    TargetSelectionError,
    ConditionEvaluationError,
)

__all__ = [
    # Core classes
    "RoutingEngine",
    "RoutingEngineFactory",
    "RoutingValidator",
    "ConfigurationLinter",

    # Configuration models
    "RoutingConfig",
    "RoutingRule",
    "RoutingCondition",
    "RoutingTarget",
    "RoutingResult",

    # Enums
    "RoutingStrategy",
    "ConditionOperator",
    "ExecutionStatus",

    # Builder pattern
    "ConfigBuilder",
    "RuleBuilder",

    # Execution
    "FallbackExecutor",
    "ExecutionResult",
    "FallbackExecutionResult",
    "ModelProvider",
    "ProviderRegistry",
    "execute_fallback",

    # Exceptions
    "RoutingError",
    "ConfigurationError",
    "RoutingConfigValidationError",
    "TargetSelectionError",
    "ConditionEvaluationError",
]

__version__ = "0.1.0"