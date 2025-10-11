"""Routing executor with fallback logic and provider-specific implementations."""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .models import RoutingTarget

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    """Status of a target execution attempt."""

    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class ExecutionResult:
    """Result of executing a single target."""

    target: RoutingTarget
    status: ExecutionStatus
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    attempt_number: int = 1


@dataclass
class FallbackExecutionResult:
    """Result of executing fallback chain."""

    success: bool
    final_response: Optional[Dict[str, Any]]
    attempts: List[ExecutionResult]
    total_time_ms: float
    explanation: str


class ModelProvider(ABC):
    """Abstract base class for model provider implementations."""

    @abstractmethod
    async def call_model(
        self,
        target: RoutingTarget,
        request_data: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, Any]:
        """
        Call the model endpoint.

        Args:
            target: Target configuration
            request_data: Request payload
            timeout_ms: Timeout in milliseconds

        Returns:
            Model response

        Raises:
            TimeoutError: If request exceeds timeout
            Exception: For other errors
        """
        pass


class ModalProvider(ModelProvider):
    """Modal.com provider implementation."""

    async def call_model(
        self,
        target: RoutingTarget,
        request_data: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Call Modal model endpoint."""
        logger.info(
            f"[Modal] Calling model={target.model_name}, "
            f"function={target.function_name or 'main'}, "
            f"timeout={timeout_ms}ms"
        )

        try:
            # Simulate Modal API call
            # In production, this would use Modal's SDK or HTTP API
            await asyncio.sleep(0.1)  # Simulate network latency

            return {
                "provider": "modal",
                "model": target.model_name,
                "function": target.function_name or "main",
                "status": "completed",
                "output": f"Response from {target.model_name}",
                "metadata": {
                    "endpoint": target.endpoint,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"Modal call exceeded {timeout_ms}ms timeout")


class FALProvider(ModelProvider):
    """FAL.ai provider implementation."""

    async def call_model(
        self,
        target: RoutingTarget,
        request_data: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Call FAL model endpoint."""
        logger.info(
            f"[FAL] Calling model={target.model_name}, "
            f"timeout={timeout_ms}ms"
        )

        try:
            # Simulate FAL API call
            # In production, this would use FAL's SDK or HTTP API
            await asyncio.sleep(0.15)  # Simulate network latency

            return {
                "provider": "fal",
                "model": target.model_name,
                "status": "completed",
                "output": f"Response from {target.model_name}",
                "metadata": {
                    "endpoint": target.endpoint,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"FAL call exceeded {timeout_ms}ms timeout")


class OpenAIProvider(ModelProvider):
    """OpenAI provider implementation."""

    async def call_model(
        self,
        target: RoutingTarget,
        request_data: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Call OpenAI model endpoint."""
        logger.info(
            f"[OpenAI] Calling model={target.model_name}, "
            f"timeout={timeout_ms}ms"
        )

        try:
            # Simulate OpenAI API call
            await asyncio.sleep(0.2)  # Simulate network latency

            return {
                "provider": "openai",
                "model": target.model_name,
                "status": "completed",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": f"Response from {target.model_name}"
                    }
                }],
                "metadata": {
                    "endpoint": target.endpoint,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"OpenAI call exceeded {timeout_ms}ms timeout")


class AnthropicProvider(ModelProvider):
    """Anthropic provider implementation."""

    async def call_model(
        self,
        target: RoutingTarget,
        request_data: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Call Anthropic model endpoint."""
        logger.info(
            f"[Anthropic] Calling model={target.model_name}, "
            f"timeout={timeout_ms}ms"
        )

        try:
            # Simulate Anthropic API call
            await asyncio.sleep(0.18)  # Simulate network latency

            return {
                "provider": "anthropic",
                "model": target.model_name,
                "status": "completed",
                "content": [{
                    "type": "text",
                    "text": f"Response from {target.model_name}"
                }],
                "metadata": {
                    "endpoint": target.endpoint,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"Anthropic call exceeded {timeout_ms}ms timeout")


class ReplicateProvider(ModelProvider):
    """Replicate provider implementation."""

    async def call_model(
        self,
        target: RoutingTarget,
        request_data: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Call Replicate model endpoint."""
        logger.info(
            f"[Replicate] Calling model={target.model_name}, "
            f"timeout={timeout_ms}ms"
        )

        try:
            # Simulate Replicate API call
            await asyncio.sleep(0.25)  # Simulate network latency

            return {
                "provider": "replicate",
                "model": target.model_name,
                "status": "succeeded",
                "output": f"Response from {target.model_name}",
                "metadata": {
                    "endpoint": target.endpoint,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"Replicate call exceeded {timeout_ms}ms timeout")


class CustomProvider(ModelProvider):
    """Custom/Generic HTTP endpoint provider."""

    async def call_model(
        self,
        target: RoutingTarget,
        request_data: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, Any]:
        """Call custom HTTP endpoint."""
        logger.info(
            f"[Custom] Calling endpoint={target.endpoint}, "
            f"timeout={timeout_ms}ms"
        )

        try:
            # Simulate HTTP call
            await asyncio.sleep(0.1)  # Simulate network latency

            return {
                "provider": "custom",
                "model": target.model_name,
                "endpoint": target.endpoint,
                "status": "success",
                "result": f"Response from {target.model_name}",
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"Custom endpoint call exceeded {timeout_ms}ms timeout")


class ProviderRegistry:
    """Registry for model providers."""

    _providers: Dict[str, ModelProvider] = {
        "modal": ModalProvider(),
        "fal": FALProvider(),
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "replicate": ReplicateProvider(),
        "custom": CustomProvider(),
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> ModelProvider:
        """Get provider by name, default to custom if not found."""
        provider_name = provider_name.lower()
        return cls._providers.get(provider_name, cls._providers["custom"])

    @classmethod
    def register_provider(cls, name: str, provider: ModelProvider) -> None:
        """Register a new provider."""
        cls._providers[name.lower()] = provider


class FallbackExecutor:
    """Executor for fallback routing strategy."""

    def __init__(self, targets: List[RoutingTarget]):
        """
        Initialize fallback executor.

        Args:
            targets: List of targets in fallback order (primary first)
        """
        self.targets = targets

    async def execute(
        self,
        request_data: Dict[str, Any]
    ) -> FallbackExecutionResult:
        """
        Execute fallback chain.

        Tries each target in order until one succeeds or all fail.

        Args:
            request_data: Request payload to send to models

        Returns:
            FallbackExecutionResult with execution details
        """
        start_time = asyncio.get_event_loop().time()
        attempts: List[ExecutionResult] = []

        for attempt_num, target in enumerate(self.targets, start=1):
            target_type = "Primary" if attempt_num == 1 else f"Fallback {attempt_num - 1}"
            logger.info(f"Attempting {target_type}: {target.model_name}")

            result = await self._execute_target(
                target=target,
                request_data=request_data,
                attempt_number=attempt_num
            )
            attempts.append(result)

            # If successful, return immediately
            if result.status == ExecutionStatus.SUCCESS:
                total_time = (asyncio.get_event_loop().time() - start_time) * 1000
                return FallbackExecutionResult(
                    success=True,
                    final_response=result.response,
                    attempts=attempts,
                    total_time_ms=total_time,
                    explanation=f"Success on {target_type}: {target.label or target.model_name}"
                )

            # Log failure and continue to next target
            logger.warning(
                f"{target_type} failed: {result.error} "
                f"(status={result.status}, time={result.execution_time_ms:.2f}ms)"
            )

        # All targets failed
        total_time = (asyncio.get_event_loop().time() - start_time) * 1000
        return FallbackExecutionResult(
            success=False,
            final_response=None,
            attempts=attempts,
            total_time_ms=total_time,
            explanation=f"All {len(attempts)} targets failed"
        )

    async def _execute_target(
        self,
        target: RoutingTarget,
        request_data: Dict[str, Any],
        attempt_number: int
    ) -> ExecutionResult:
        """
        Execute a single target with timeout and retry logic.

        Args:
            target: Target to execute
            request_data: Request payload
            attempt_number: Which attempt this is in the fallback chain

        Returns:
            ExecutionResult with outcome
        """
        timeout_ms = target.timeout_ms or 30000  # Default 30s timeout
        retry_count = target.retry_count or 0

        for retry in range(retry_count + 1):
            if retry > 0:
                logger.info(f"Retry {retry}/{retry_count} for {target.model_name}")

            start_time = asyncio.get_event_loop().time()

            try:
                # Get the appropriate provider
                provider = ProviderRegistry.get_provider(target.provider)

                # Execute with timeout
                response = await asyncio.wait_for(
                    provider.call_model(target, request_data, timeout_ms),
                    timeout=timeout_ms / 1000.0  # Convert to seconds
                )

                execution_time = (asyncio.get_event_loop().time() - start_time) * 1000

                return ExecutionResult(
                    target=target,
                    status=ExecutionStatus.SUCCESS,
                    response=response,
                    execution_time_ms=execution_time,
                    attempt_number=attempt_number
                )

            except asyncio.TimeoutError:
                execution_time = (asyncio.get_event_loop().time() - start_time) * 1000

                # Don't retry on timeout for last attempt
                if retry == retry_count:
                    return ExecutionResult(
                        target=target,
                        status=ExecutionStatus.TIMEOUT,
                        error=f"Request exceeded timeout of {timeout_ms}ms",
                        execution_time_ms=execution_time,
                        attempt_number=attempt_number
                    )

                logger.warning(f"Timeout after {execution_time:.2f}ms, retrying...")

            except Exception as e:
                execution_time = (asyncio.get_event_loop().time() - start_time) * 1000

                # Don't retry on error for last attempt
                if retry == retry_count:
                    return ExecutionResult(
                        target=target,
                        status=ExecutionStatus.ERROR,
                        error=str(e),
                        execution_time_ms=execution_time,
                        attempt_number=attempt_number
                    )

                logger.warning(f"Error: {e}, retrying...")

        # Should not reach here, but just in case
        return ExecutionResult(
            target=target,
            status=ExecutionStatus.ERROR,
            error="Unexpected execution path",
            execution_time_ms=0.0,
            attempt_number=attempt_number
        )


# Convenience function for simple usage
async def execute_fallback(
    targets: List[RoutingTarget],
    request_data: Dict[str, Any]
) -> FallbackExecutionResult:
    """
    Execute fallback routing for a list of targets.

    This is a convenience function that creates an executor and runs it.

    Args:
        targets: List of targets in fallback order
        request_data: Request payload

    Returns:
        FallbackExecutionResult
    """
    executor = FallbackExecutor(targets)
    return await executor.execute(request_data)
