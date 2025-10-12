"""
Entity registry for PicoAgents WebUI.

Manages discovered entities and provides access to them for execution.
"""

import logging
from typing import Any, Dict, List, Optional

from ._discovery import PicoAgentsScanner
from ._models import Entity

logger: logging.Logger = logging.getLogger(__name__)


class EntityRegistry:
    """Registry for managing discovered PicoAgents entities."""

    def __init__(self, entities_dir: Optional[str] = None) -> None:
        """Initialize the entity registry.

        Args:
            entities_dir: Directory to scan for entities
        """
        self.entities_dir = entities_dir
        self.scanner = PicoAgentsScanner(entities_dir) if entities_dir else None
        self._entities: Dict[str, Entity] = {}
        self._in_memory_entities: Dict[str, Any] = {}

        # Perform initial discovery if directory provided
        if self.scanner:
            self._refresh_entities()

    def _refresh_entities(self) -> None:
        """Refresh entities from directory scan."""
        if not self.scanner:
            return

        try:
            discovered = self.scanner.discover_entities()
            self._entities = {entity.id: entity for entity in discovered}
            logger.info(f"Refreshed registry with {len(self._entities)} entities")
        except Exception as e:
            logger.error(f"Error refreshing entities: {e}")

    def register_entity(self, entity_id: str, entity_obj: Any) -> None:
        """Register an in-memory entity.

        Args:
            entity_id: Unique identifier for the entity
            entity_obj: Entity object (Agent, Orchestrator, or Workflow)
        """
        self._in_memory_entities[entity_id] = entity_obj

        # Create entity info for the in-memory entity
        entity_info = self._create_entity_info_from_object(entity_id, entity_obj)
        if entity_info:
            self._entities[entity_id] = entity_info
            logger.info(f"Registered in-memory entity: {entity_id}")

    def get_entity_info(self, entity_id: str) -> Optional[Entity]:
        """Get entity information by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity information or None if not found
        """
        return self._entities.get(entity_id)

    def get_entity_object(self, entity_id: str) -> Optional[Any]:
        """Get the actual entity object for execution.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity object or None if not found
        """
        # Check in-memory entities first
        if entity_id in self._in_memory_entities:
            return self._in_memory_entities[entity_id]

        # Check discovered entities
        if self.scanner and entity_id in self._entities:
            return self.scanner.get_entity_object(entity_id)

        return None

    def list_entities(self) -> List[Entity]:
        """List all registered entities.

        Returns:
            List of entity information objects
        """
        return list(self._entities.values())

    def list_agents(self) -> List[Entity]:
        """List only agent entities.

        Returns:
            List of agent entity information
        """
        return [entity for entity in self._entities.values() if entity.type == "agent"]

    def list_orchestrators(self) -> List[Entity]:
        """List only orchestrator entities.

        Returns:
            List of orchestrator entity information
        """
        return [
            entity
            for entity in self._entities.values()
            if entity.type == "orchestrator"
        ]

    def list_workflows(self) -> List[Entity]:
        """List only workflow entities.

        Returns:
            List of workflow entity information
        """
        return [
            entity for entity in self._entities.values() if entity.type == "workflow"
        ]

    def clear_cache(self) -> None:
        """Clear cache and refresh from directory."""
        if self.scanner:
            self.scanner.clear_cache()
            self._refresh_entities()

    def _create_entity_info_from_object(
        self, entity_id: str, entity_obj: Any
    ) -> Optional[Entity]:
        """Create entity info from an in-memory object.

        Args:
            entity_id: Entity identifier
            entity_obj: Entity object

        Returns:
            Entity information or None if object is not recognized
        """
        from ._models import AgentInfo, OrchestratorInfo, WorkflowInfo

        common_attrs = {
            "id": entity_id,
            "name": getattr(entity_obj, "name", entity_id),
            "description": getattr(entity_obj, "description", None),
            "source": "memory",
            "module_path": None,
            "has_env": False,
        }

        # Try to determine type by checking for PicoAgents base classes
        try:
            from ..agents import BaseAgent

            if isinstance(entity_obj, BaseAgent):
                # Extract agent-specific info
                tools = [
                    getattr(tool, "name", str(tool))
                    for tool in getattr(entity_obj, "tools", [])
                ]
                model = getattr(
                    getattr(entity_obj, "model_client", None), "model", None
                )
                memory_type = (
                    type(getattr(entity_obj, "memory", None)).__name__
                    if getattr(entity_obj, "memory", None)
                    else None
                )

                return AgentInfo(
                    **common_attrs,
                    type="agent",
                    tools=tools,
                    model=model,
                    memory_type=memory_type,
                )
        except ImportError:
            pass

        try:
            from ..orchestration import BaseOrchestrator

            if isinstance(entity_obj, BaseOrchestrator):
                # Extract orchestrator-specific info
                orchestrator_type = (
                    type(entity_obj).__name__.lower().replace("orchestrator", "")
                )
                agents = [agent.name for agent in getattr(entity_obj, "agents", [])]
                termination_conditions = []
                termination = getattr(entity_obj, "termination", None)
                if termination and hasattr(termination, "__class__"):
                    termination_conditions = [termination.__class__.__name__]

                return OrchestratorInfo(
                    **common_attrs,
                    type="orchestrator",
                    orchestrator_type=orchestrator_type,
                    agents=agents,
                    termination_conditions=termination_conditions,
                )
        except ImportError:
            pass

        # Check for agent-like objects first (most specific)
        if (
            hasattr(entity_obj, "run")
            and callable(getattr(entity_obj, "run"))
            and hasattr(entity_obj, "name")
            and hasattr(entity_obj, "description")
        ):
            # Treat as agent
            tools = [
                getattr(tool, "name", str(tool))
                for tool in getattr(entity_obj, "tools", [])
            ]
            model = getattr(getattr(entity_obj, "model_client", None), "model", None)
            memory_type = (
                type(getattr(entity_obj, "memory", None)).__name__
                if getattr(entity_obj, "memory", None)
                else None
            )

            return AgentInfo(
                **common_attrs,
                type="agent",
                tools=tools,
                model=model,
                memory_type=memory_type,
            )

        # Check for orchestrator-like objects (has agents attribute)
        if (
            hasattr(entity_obj, "run_stream")
            and callable(getattr(entity_obj, "run_stream"))
            and hasattr(entity_obj, "agents")
        ):
            # Treat as orchestrator
            orchestrator_type = (
                type(entity_obj).__name__.lower().replace("orchestrator", "")
            )
            agents = [
                getattr(agent, "name", str(agent))
                for agent in getattr(entity_obj, "agents", [])
            ]
            termination_conditions = []
            termination = getattr(entity_obj, "termination", None)
            if termination and hasattr(termination, "__class__"):
                termination_conditions = [termination.__class__.__name__]

            return OrchestratorInfo(
                **common_attrs,
                type="orchestrator",
                orchestrator_type=orchestrator_type if orchestrator_type else "custom",
                agents=agents,
                termination_conditions=termination_conditions,
            )

        # Fallback: check for workflow duck typing (has steps or just run_stream)
        if hasattr(entity_obj, "run_stream") and callable(
            getattr(entity_obj, "run_stream")
        ):
            # Treat as workflow
            steps = (
                list(getattr(entity_obj, "steps", {}).keys())
                if hasattr(entity_obj, "steps")
                else []
            )
            start_step = getattr(entity_obj, "start_step", None)
            input_schema = getattr(entity_obj, "input_schema", None)

            return WorkflowInfo(
                **common_attrs,
                type="workflow",
                steps=steps,
                start_step=start_step,
                input_schema=input_schema,
            )

        return None
