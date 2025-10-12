"""
Middleware system for picoagents.

This module provides the middleware infrastructure for intercepting and processing
agent operations like model calls, tool calls, and memory access.
"""

import asyncio
import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .context import AgentContext
from .messages import Message


class MiddlewareContext(BaseModel):
    """Context passed through middleware chain."""

    operation: str = Field(
        description="Operation type: 'model_call', 'tool_call', 'memory_access'"
    )
    agent_name: str = Field(description="Name of the agent executing the operation")
    agent_context: AgentContext = Field(description="The agent's context")
    data: Any = Field(
        description="Operation-specific data (messages, tool request, etc)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for middleware use"
    )


class BaseMiddleware(ABC):
    """
    Abstract base class for middleware components.

    Middleware can intercept and modify requests/responses for agent operations.
    Each middleware instance can maintain its own state.
    """

    @abstractmethod
    async def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
        """
        Process before the operation executes.

        Args:
            context: The middleware context

        Returns:
            Modified context (or same context if no changes)

        Raises:
            Exception: To abort the operation
        """
        return context

    @abstractmethod
    async def process_response(self, context: MiddlewareContext, result: Any) -> Any:
        """
        Process after the operation completes successfully.

        Args:
            context: The middleware context
            result: The operation result

        Returns:
            Modified result (or same result if no changes)
        """
        return result

    @abstractmethod
    async def process_error(
        self, context: MiddlewareContext, error: Exception
    ) -> Optional[Any]:
        """
        Handle errors from the operation.

        Args:
            context: The middleware context
            error: The exception that occurred

        Returns:
            Recovery value to use instead of raising error, or None to propagate error

        Raises:
            Exception: Re-raise or raise new exception
        """
        raise error


class MiddlewareChain:
    """Executes a chain of middleware in sequence."""

    def __init__(self, middlewares: Optional[List[BaseMiddleware]] = None):
        """
        Initialize the middleware chain.

        Args:
            middlewares: List of middleware to execute in order
        """
        self.middlewares = middlewares or []

    def add(self, middleware: BaseMiddleware) -> None:
        """Add a middleware to the chain."""
        self.middlewares.append(middleware)

    def remove(self, middleware: BaseMiddleware) -> None:
        """Remove a middleware from the chain."""
        if middleware in self.middlewares:
            self.middlewares.remove(middleware)

    async def execute(
        self,
        operation: str,
        agent_name: str,
        agent_context: AgentContext,
        data: Any,
        func: Callable,
    ) -> Any:
        """
        Execute the middleware chain around an operation.

        Args:
            operation: Type of operation being performed
            agent_name: Name of the agent
            agent_context: Agent's context
            data: Operation-specific data
            func: The actual operation to execute

        Returns:
            Result from the operation (possibly modified by middleware)
        """
        # Create middleware context
        ctx = MiddlewareContext(
            operation=operation,
            agent_name=agent_name,
            agent_context=agent_context,
            data=data,
        )

        # Pre-process through all middleware (forward order)
        for middleware in self.middlewares:
            try:
                ctx = await middleware.process_request(ctx)
            except Exception as e:
                # Middleware can abort the operation by raising an exception
                # Try error handlers in reverse order
                for error_middleware in reversed(self.middlewares):
                    try:
                        result = await error_middleware.process_error(ctx, e)
                        if result is not None:
                            return result
                    except Exception:
                        continue
                raise e

        # Execute the actual operation with processed data
        try:
            result = await func(ctx.data)
        except Exception as e:
            # Error handling through middleware (reverse order)
            for middleware in reversed(self.middlewares):
                try:
                    recovered = await middleware.process_error(ctx, e)
                    if recovered is not None:
                        return recovered
                except Exception:
                    continue
            raise e

        # Post-process through all middleware (reverse order)
        for middleware in reversed(self.middlewares):
            try:
                result = await middleware.process_response(ctx, result)
            except Exception as e:
                # Handle errors in response processing
                for error_middleware in reversed(self.middlewares):
                    try:
                        recovered = await error_middleware.process_error(ctx, e)
                        if recovered is not None:
                            return recovered
                    except Exception:
                        continue
                raise e

        return result


# Example Middleware Implementations


class LoggingMiddleware(BaseMiddleware):
    """Logs all agent operations."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    async def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
        """Log operation start."""
        self.logger.info(
            f"[{context.agent_name}] Starting {context.operation}",
            extra={
                "agent": context.agent_name,
                "operation": context.operation,
                "session_id": context.agent_context.session_id,
            },
        )
        context.metadata["start_time"] = time.time()
        return context

    async def process_response(self, context: MiddlewareContext, result: Any) -> Any:
        """Log operation completion."""
        duration = time.time() - context.metadata.get("start_time", 0)
        self.logger.info(
            f"[{context.agent_name}] Completed {context.operation} in {duration:.2f}s",
            extra={
                "agent": context.agent_name,
                "operation": context.operation,
                "duration": duration,
                "session_id": context.agent_context.session_id,
            },
        )
        return result

    async def process_error(
        self, context: MiddlewareContext, error: Exception
    ) -> Optional[Any]:
        """Log operation error."""
        self.logger.error(
            f"[{context.agent_name}] Error in {context.operation}: {error}",
            extra={
                "agent": context.agent_name,
                "operation": context.operation,
                "error_type": type(error).__name__,
                "session_id": context.agent_context.session_id,
            },
        )
        raise error


class RateLimitMiddleware(BaseMiddleware):
    """Rate limits operations per agent."""

    def __init__(self, max_calls_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_calls_per_minute: Maximum operations allowed per minute
        """
        self.max_calls = max_calls_per_minute
        self.call_times: List[float] = []  # Stateful tracking of call times

    async def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
        """Check and enforce rate limit."""
        now = time.time()

        # Remove calls outside the 60-second window
        self.call_times = [t for t in self.call_times if now - t < 60]

        # Check if we've hit the limit
        if len(self.call_times) >= self.max_calls:
            # Calculate how long to wait
            oldest_call = self.call_times[0]
            wait_time = 60 - (now - oldest_call)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                now = time.time()

        # Record this call
        self.call_times.append(now)
        return context

    async def process_response(self, context: MiddlewareContext, result: Any) -> Any:
        """No response processing needed."""
        return result

    async def process_error(
        self, context: MiddlewareContext, error: Exception
    ) -> Optional[Any]:
        """No error recovery."""
        raise error


class PIIRedactionMiddleware(BaseMiddleware):
    """Redacts personally identifiable information from inputs and outputs."""

    def __init__(self, patterns: Optional[Dict[str, str]] = None):
        """
        Initialize PII redactor.

        Args:
            patterns: Custom patterns for PII detection (regex -> replacement)
        """
        self.patterns = patterns or {
            # SSN
            r"\b\d{3}-\d{2}-\d{4}\b": "[SSN-REDACTED]",
            # Email
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b": "[EMAIL-REDACTED]",
            # Phone
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b": "[PHONE-REDACTED]",
            # Credit card
            r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b": "[CC-REDACTED]",
        }

    def _redact_text(self, text: str) -> str:
        """Apply redaction patterns to text."""
        for pattern, replacement in self.patterns.items():
            text = re.sub(pattern, replacement, text)
        return text

    async def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
        """Redact PII from inputs."""
        if context.operation == "model_call" and isinstance(context.data, list):
            # Create new messages with redacted content (since messages are frozen)
            redacted_messages = []
            for msg in context.data:
                if hasattr(msg, "content"):
                    # Create a new message with redacted content
                    redacted_content = self._redact_text(msg.content)
                    if redacted_content != msg.content:
                        # Only create new object if content changed
                        new_msg = msg.model_copy(update={"content": redacted_content})
                        redacted_messages.append(new_msg)
                    else:
                        redacted_messages.append(msg)
                else:
                    redacted_messages.append(msg)
            context.data = redacted_messages
        elif context.operation == "tool_call" and hasattr(context.data, "parameters"):
            # Redact PII from tool parameters
            params = (
                context.data.parameters.copy()
                if isinstance(context.data.parameters, dict)
                else context.data.parameters
            )
            if isinstance(params, dict):
                for key, value in params.items():
                    if isinstance(value, str):
                        params[key] = self._redact_text(value)
                # Create new tool call with redacted parameters
                context.data = context.data.model_copy(update={"parameters": params})
        return context

    async def process_response(self, context: MiddlewareContext, result: Any) -> Any:
        """Redact PII from outputs."""
        if context.operation == "model_call":
            # Redact from model response
            if hasattr(result, "message") and hasattr(result.message, "content"):
                redacted_content = self._redact_text(result.message.content)
                if redacted_content != result.message.content:
                    # Create new message with redacted content
                    redacted_message = result.message.model_copy(
                        update={"content": redacted_content}
                    )
                    # Create new result with redacted message
                    result = result.model_copy(update={"message": redacted_message})
        elif context.operation == "tool_call":
            # Redact from tool result
            if hasattr(result, "result") and isinstance(result.result, str):
                redacted_result = self._redact_text(result.result)
                if redacted_result != result.result:
                    result = result.model_copy(update={"result": redacted_result})
        return result

    async def process_error(
        self, context: MiddlewareContext, error: Exception
    ) -> Optional[Any]:
        """No error recovery."""
        raise error


class GuardrailMiddleware(BaseMiddleware):
    """Enforces safety guardrails on operations."""

    def __init__(
        self,
        blocked_tools: Optional[List[str]] = None,
        blocked_patterns: Optional[List[str]] = None,
    ):
        """
        Initialize guardrails.

        Args:
            blocked_tools: List of tool names to block
            blocked_patterns: List of regex patterns to block in content
        """
        self.blocked_tools = blocked_tools or []
        self.blocked_patterns = [re.compile(p) for p in (blocked_patterns or [])]

    async def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
        """Check for policy violations."""
        if context.operation == "tool_call":
            # Block dangerous tools
            tool_name = getattr(context.data, "tool_name", None)
            if tool_name in self.blocked_tools:
                raise ValueError(f"Tool '{tool_name}' is blocked by guardrails")

            # Check parameters for dangerous patterns
            params = getattr(context.data, "parameters", {})
            params_str = str(params)
            for pattern in self.blocked_patterns:
                if pattern.search(params_str):
                    raise ValueError(
                        f"Tool parameters match blocked pattern: {pattern.pattern}"
                    )

        elif context.operation == "model_call":
            # Check messages for blocked patterns
            for msg in context.data:
                if hasattr(msg, "content"):
                    for pattern in self.blocked_patterns:
                        if pattern.search(msg.content):
                            raise ValueError(
                                f"Message contains blocked pattern: {pattern.pattern}"
                            )

        return context

    async def process_response(self, context: MiddlewareContext, result: Any) -> Any:
        """No response processing."""
        return result

    async def process_error(
        self, context: MiddlewareContext, error: Exception
    ) -> Optional[Any]:
        """No error recovery."""
        raise error


class MetricsMiddleware(BaseMiddleware):
    """Collects metrics about agent operations."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "total_operations": 0,
            "operations_by_type": {},
            "errors_by_type": {},
            "total_duration": 0.0,
            "operation_durations": [],
        }

    async def process_request(self, context: MiddlewareContext) -> MiddlewareContext:
        """Track operation start."""
        self.metrics["total_operations"] += 1
        self.metrics["operations_by_type"][context.operation] = (
            self.metrics["operations_by_type"].get(context.operation, 0) + 1
        )
        context.metadata["metrics_start_time"] = time.time()
        return context

    async def process_response(self, context: MiddlewareContext, result: Any) -> Any:
        """Track operation completion."""
        duration = time.time() - context.metadata.get("metrics_start_time", 0)
        self.metrics["total_duration"] += duration
        self.metrics["operation_durations"].append((context.operation, duration))

        # Keep only last 100 durations to avoid memory issues
        if len(self.metrics["operation_durations"]) > 100:
            self.metrics["operation_durations"] = self.metrics["operation_durations"][
                -100:
            ]

        return result

    async def process_error(
        self, context: MiddlewareContext, error: Exception
    ) -> Optional[Any]:
        """Track operation errors."""
        error_type = type(error).__name__
        self.metrics["errors_by_type"][error_type] = (
            self.metrics["errors_by_type"].get(error_type, 0) + 1
        )
        raise error

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        avg_duration = (
            self.metrics["total_duration"] / self.metrics["total_operations"]
            if self.metrics["total_operations"] > 0
            else 0
        )
        return {
            **self.metrics,
            "average_duration": avg_duration,
        }
