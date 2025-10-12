"""
Agent context management for picoagents.

This module provides the AgentContext class that replaces the simple message_history
list with a more structured and extensible context object.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .messages import AssistantMessage, Message, UserMessage


class AgentContext(BaseModel):
    """
    Unified context object for agents.

    This replaces the simple message_history list with a structured context
    that can carry messages, metadata, shared state, and environment info.
    """

    messages: List[Message] = Field(
        default_factory=list, description="Conversation history"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Request metadata (request_id, user_id, session_id, etc)",
    )

    shared_state: Dict[str, Any] = Field(
        default_factory=dict, description="State shared across agents in orchestration"
    )

    environment: Dict[str, Any] = Field(
        default_factory=dict, description="Environment variables and configuration"
    )

    session_id: Optional[str] = Field(
        default=None, description="Unique session identifier"
    )

    created_at: datetime = Field(
        default_factory=datetime.now, description="Context creation timestamp"
    )

    # Convenience methods
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation history."""
        self.messages.append(message)

    def get_last_user_message(self) -> Optional[UserMessage]:
        """Get the most recent user message."""
        for msg in reversed(self.messages):
            if isinstance(msg, UserMessage):
                return msg
        return None

    def get_last_assistant_message(self) -> Optional[AssistantMessage]:
        """Get the most recent assistant message."""
        for msg in reversed(self.messages):
            if isinstance(msg, AssistantMessage):
                return msg
        return None

    def clear_messages(self) -> None:
        """Clear message history while preserving metadata and state."""
        self.messages.clear()

    def reset(self) -> None:
        """Complete reset of context including messages, state, and metadata."""
        self.messages.clear()
        self.shared_state.clear()
        self.metadata.clear()
        # Keep environment and session_id as they're typically persistent

    @property
    def message_count(self) -> int:
        """Get the number of messages in the context."""
        return len(self.messages)

    @property
    def is_empty(self) -> bool:
        """Check if the context has no messages."""
        return len(self.messages) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return self.model_dump()

    @classmethod
    def from_messages(cls, messages: List[Message]) -> "AgentContext":
        """Create context from a list of messages (backward compatibility helper)."""
        return cls(messages=messages)

    def __str__(self) -> str:
        """String representation of the context."""
        return f"AgentContext(messages={self.message_count}, session={self.session_id})"
