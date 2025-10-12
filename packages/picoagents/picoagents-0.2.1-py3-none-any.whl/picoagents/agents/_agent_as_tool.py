"""
AgentAsTool wrapper - allows any agent to be used as a tool by other agents.

This module provides the AgentAsTool class that wraps BaseAgent instances,
exposing them as BaseTool instances for composition patterns.
"""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from .._cancellation_token import CancellationToken
from ..messages import Message
from ..tools import BaseTool
from ..types import AgentEvent, AgentResponse, ToolResult

if TYPE_CHECKING:
    from ._base import BaseAgent


class AgentAsTool(BaseTool):
    """
    Wraps any BaseAgent to expose it as a tool that other agents can use.

    This enables hierarchical composition where specialized agents can be
    used as tools by higher-level coordinating agents.
    """

    def __init__(self, agent: "BaseAgent", task_parameter_name: str = "task"):
        """
        Initialize the agent-as-tool wrapper.

        Args:
            agent: The agent to wrap as a tool
            task_parameter_name: Parameter name for the task input
        """
        from ._base import BaseAgent

        if not isinstance(agent, BaseAgent):
            raise TypeError("agent must be a BaseAgent instance")

        super().__init__(name=agent.name, description=agent.description)

        self.agent = agent
        self.task_parameter_name = task_parameter_name

    @property
    def parameters(self) -> Dict[str, Any]:
        """
        Define the tool's parameter schema.

        Returns:
            JSON schema for tool parameters
        """
        return {
            "type": "object",
            "properties": {
                self.task_parameter_name: {
                    "type": "string",
                    "description": f"Task for {self.agent.name} to complete",
                }
            },
            "required": [self.task_parameter_name],
        }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute the wrapped agent and return final result.

        Args:
            parameters: Tool parameters containing the task

        Returns:
            ToolResult with agent's final response
        """
        task = parameters.get(self.task_parameter_name, "")

        try:
            response = await self.agent.run(task)

            # Extract final message content
            final_content = ""
            if response.messages:
                final_content = response.messages[-1].content

            return ToolResult(
                success=True,
                result=final_content,
                error=None,
                metadata={
                    "agent_name": self.agent.name,
                    "message_count": len(response.messages),
                    "usage": response.usage.model_dump() if response.usage else None,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result="",
                error=f"Agent execution failed: {str(e)}",
                metadata={"agent_name": self.agent.name},
            )

    async def execute_stream(
        self,
        parameters: Dict[str, Any],
        cancellation_token: Optional[CancellationToken] = None,
    ) -> AsyncGenerator[Union[Message, "AgentEvent", ToolResult], None]:
        """
        Execute the wrapped agent with streaming output.

        Args:
            parameters: Tool parameters containing the task
            cancellation_token: Optional cancellation token

        Yields:
            Agent messages/events, followed by final ToolResult
        """
        task = parameters.get(self.task_parameter_name, "")

        final_response = None
        error_occurred = False
        error_message = ""

        try:
            # Stream all agent output
            async for item in self.agent.run_stream(task, cancellation_token):
                if isinstance(item, AgentResponse):
                    final_response = item
                else:
                    # Forward agent messages and events
                    yield item

        except Exception as e:
            error_occurred = True
            error_message = str(e)

        # Emit final ToolResult
        if error_occurred:
            yield ToolResult(
                success=False,
                result="",
                error=f"Agent execution failed: {error_message}",
                metadata={"agent_name": self.agent.name},
            )
        else:
            final_content = ""
            if final_response and final_response.messages:
                final_content = final_response.messages[-1].content

            yield ToolResult(
                success=True,
                result=final_content,
                error=None,
                metadata={
                    "agent_name": self.agent.name,
                    "message_count": len(final_response.messages)
                    if final_response
                    else 0,
                    "usage": final_response.usage.model_dump()
                    if final_response and final_response.usage
                    else None,
                },
            )

    def model_dump(self) -> Dict[str, Any]:
        """Serialize the agent-as-tool wrapper for persistence."""
        return {
            "type": "agent_as_tool",
            "agent": {"name": self.agent.name},
            "task_parameter_name": self.task_parameter_name,
        }
