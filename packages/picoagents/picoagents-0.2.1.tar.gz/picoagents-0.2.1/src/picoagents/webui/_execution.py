"""
Execution engine for PicoAgents WebUI.

Streams raw PicoAgent events with session context management.
"""

import json
import logging
from typing import Any, AsyncGenerator, List, Optional

from ..context import AgentContext
from ..messages import Message
from ._models import WebUIStreamEvent
from ._sessions import SessionManager

logger: logging.Logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Engine for executing PicoAgents entities with session management."""

    def __init__(self, session_manager: SessionManager) -> None:
        """Initialize execution engine.

        Args:
            session_manager: Session manager for tracking executions
        """
        self.session_manager = session_manager

    async def execute_agent_stream(
        self,
        agent: Any,
        messages: List[Message],
        session_id: Optional[str] = None,
        stream_tokens: bool = True,
    ) -> AsyncGenerator[str, None]:
        """Stream raw PicoAgent events with session management.

        Args:
            agent: Agent object to execute
            messages: New messages to add to session
            session_id: Optional existing session ID (creates new if None)
            stream_tokens: Enable token-level streaming

        Yields:
            Server-sent events containing raw PicoAgent events
        """
        # Create or get existing session
        if session_id is None:
            session_id = self.session_manager.create_session_id()

        # Use both id and name - prefer id for consistency
        entity_id = getattr(agent, "id", None) or getattr(agent, "name", "unknown")
        context = await self.session_manager.get_or_create(
            session_id, entity_id, "agent"
        )

        # Add new messages to context
        for msg in messages:
            context.add_message(msg)

        try:
            # Stream raw PicoAgent events
            async for event in agent.run_stream(
                context.messages, verbose=True, stream_tokens=stream_tokens
            ):
                # Wrap the raw event with session context
                wrapped_event = WebUIStreamEvent(
                    session_id=session_id,
                    event=event,  # Raw PicoAgent event
                )

                yield f"data: {wrapped_event.model_dump_json()}\n\n"

            # Update session with final context
            # Agent has already updated context.messages internally
            await self.session_manager.update(session_id, context)

        except Exception as e:
            logger.error(f"Error in agent streaming execution: {e}")
            error_event = WebUIStreamEvent(
                session_id=session_id, event={"type": "error", "message": str(e)}
            )
            yield f"data: {error_event.model_dump_json()}\n\n"

    async def execute_orchestrator_stream(
        self,
        orchestrator: Any,
        messages: List[Message],
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream raw orchestrator events with session management.

        Args:
            orchestrator: Orchestrator object to execute
            messages: New messages to add to session
            session_id: Optional existing session ID

        Yields:
            Server-sent events containing raw orchestrator events
        """
        if session_id is None:
            session_id = self.session_manager.create_session_id()

        # Use both id and name - prefer id for consistency
        entity_id = getattr(orchestrator, "id", None) or getattr(orchestrator, "name", "unknown")
        context = await self.session_manager.get_or_create(
            session_id, entity_id, "orchestrator"
        )

        # Add new messages to context
        for msg in messages:
            context.add_message(msg)

        try:
            # Stream raw orchestrator events
            async for event in orchestrator.run_stream(context.messages):
                wrapped_event = WebUIStreamEvent(
                    session_id=session_id, event=event
                )
                yield f"data: {wrapped_event.model_dump_json()}\n\n"

            # Update session
            await self.session_manager.update(session_id, context)

        except Exception as e:
            logger.error(f"Error in orchestrator streaming: {e}")
            error_event = WebUIStreamEvent(
                session_id=session_id, event={"type": "error", "message": str(e)}
            )
            yield f"data: {error_event.model_dump_json()}\n\n"

    async def execute_workflow_stream(
        self,
        workflow: Any,
        input_data: Any,
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream raw workflow events with session management.

        Args:
            workflow: Workflow object to execute
            input_data: Input data for workflow
            session_id: Optional existing session ID

        Yields:
            Server-sent events containing raw workflow events
        """
        if session_id is None:
            session_id = self.session_manager.create_session_id()

        # Use both id and name - prefer id for consistency
        entity_id = getattr(workflow, "id", None) or getattr(workflow, "name", "unknown")
        context = await self.session_manager.get_or_create(
            session_id, entity_id, "workflow"
        )

        # Store input data in metadata
        context.metadata["last_input"] = input_data

        try:
            # Stream raw workflow events
            async for event in workflow.run_stream(input_data):
                wrapped_event = WebUIStreamEvent(
                    session_id=session_id, event=event
                )
                yield f"data: {wrapped_event.model_dump_json()}\n\n"

            # Update session
            await self.session_manager.update(session_id, context)

        except Exception as e:
            logger.error(f"Error in workflow streaming: {e}")
            error_event = WebUIStreamEvent(
                session_id=session_id, event={"type": "error", "message": str(e)}
            )
            yield f"data: {error_event.model_dump_json()}\n\n"
