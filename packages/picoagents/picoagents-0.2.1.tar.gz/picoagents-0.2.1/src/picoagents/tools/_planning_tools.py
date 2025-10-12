"""
Planning tools for task management and working memory.

These tools enable agents to maintain structured plans, track task status,
and coordinate across multiple agents using JSON-based persistent storage.
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid4

from ..types import ToolResult
from ._base import BaseTool


class PlanManager:
    """
    Thread-safe manager for plan files with structured JSON storage.

    Provides atomic read/write operations with file locking to prevent
    concurrent modification issues in multi-agent scenarios.
    """

    def __init__(self, plan_file: Path) -> None:
        self.plan_file = Path(plan_file)
        self._lock = asyncio.Lock()
        self._initialize_if_needed()

    def _initialize_if_needed(self) -> None:
        if not self.plan_file.exists():
            self.plan_file.parent.mkdir(parents=True, exist_ok=True)
            initial_plan = {
                "plan_id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "tasks": [],
            }
            self.plan_file.write_text(json.dumps(initial_plan, indent=2))

    async def read(self) -> Dict[str, Any]:
        async with self._lock:
            try:
                content = self.plan_file.read_text()
                result: Dict[str, Any] = json.loads(content)
                return result
            except (FileNotFoundError, json.JSONDecodeError) as e:
                raise ValueError(f"Failed to read plan: {str(e)}")

    async def write(self, plan: Dict[str, Any]) -> None:
        async with self._lock:
            plan["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.plan_file.write_text(json.dumps(plan, indent=2))

    async def add_task(self, description: str, status: str = "pending") -> str:
        plan = await self.read()
        task_id = f"task_{len(plan['tasks']) + 1}"

        task = {
            "id": task_id,
            "description": description,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        plan["tasks"].append(task)
        await self.write(plan)
        return task_id

    async def update_task_status(self, task_id: str, status: str) -> bool:
        plan = await self.read()

        for task in plan["tasks"]:
            if task["id"] == task_id:
                task["status"] = status

                if status == "completed":
                    task["completed_at"] = datetime.now(timezone.utc).isoformat()
                elif status == "in_progress":
                    task["started_at"] = datetime.now(timezone.utc).isoformat()

                await self.write(plan)
                return True

        return False

    async def get_summary(self) -> Dict[str, Any]:
        plan = await self.read()

        total = len(plan["tasks"])
        completed = sum(1 for t in plan["tasks"] if t["status"] == "completed")
        in_progress = sum(1 for t in plan["tasks"] if t["status"] == "in_progress")
        pending = sum(1 for t in plan["tasks"] if t["status"] == "pending")

        return {
            "plan_id": plan["plan_id"],
            "created_at": plan["created_at"],
            "updated_at": plan["updated_at"],
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
        }


class WritePlanTool(BaseTool):
    """Create or overwrite a plan file with initial tasks."""

    def __init__(self, manager: PlanManager) -> None:
        super().__init__(
            name="write_plan",
            description="Create a new plan or overwrite existing plan with a list of tasks. Returns the plan_id.",
        )
        self.manager = manager

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "description": "List of task descriptions to add to the plan",
                    "items": {"type": "string"},
                }
            },
            "required": ["tasks"],
        }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        tasks_descriptions = parameters["tasks"]

        try:
            plan: Dict[str, Any] = {
                "plan_id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "tasks": [],
            }

            for i, description in enumerate(tasks_descriptions, 1):
                task = {
                    "id": f"task_{i}",
                    "description": description,
                    "status": "pending",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                plan["tasks"].append(task)

            await self.manager.write(plan)

            return ToolResult(
                success=True,
                result={"plan_id": plan["plan_id"], "task_count": len(plan["tasks"])},
                error=None,
                metadata={"plan_id": plan["plan_id"]},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to write plan: {str(e)}",
                metadata={},
            )


class ReadPlanTool(BaseTool):
    """Read the current plan and all its tasks."""

    def __init__(self, manager: PlanManager) -> None:
        super().__init__(
            name="read_plan",
            description="Read the current plan including all tasks and their status. Returns the complete plan structure.",
        )
        self.manager = manager

    @property
    def parameters(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            plan = await self.manager.read()

            return ToolResult(
                success=True,
                result=plan,
                error=None,
                metadata={"task_count": len(plan.get("tasks", []))},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to read plan: {str(e)}",
                metadata={},
            )


class UpdateTaskStatusTool(BaseTool):
    """Update the status of a specific task."""

    def __init__(self, manager: PlanManager) -> None:
        super().__init__(
            name="update_task_status",
            description="Update the status of a task. Status can be 'pending', 'in_progress', or 'completed'.",
        )
        self.manager = manager

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of the task to update (e.g., 'task_1')",
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                    "description": "New status for the task",
                },
            },
            "required": ["task_id", "status"],
        }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        task_id = parameters["task_id"]
        status = parameters["status"]

        try:
            success = await self.manager.update_task_status(task_id, status)

            if success:
                return ToolResult(
                    success=True,
                    result=f"Updated {task_id} to status: {status}",
                    error=None,
                    metadata={"task_id": task_id, "status": status},
                )
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Task not found: {task_id}",
                    metadata={"task_id": task_id},
                )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to update task: {str(e)}",
                metadata={"task_id": task_id},
            )


class AddTaskTool(BaseTool):
    """Add a new task to the plan."""

    def __init__(self, manager: PlanManager) -> None:
        super().__init__(
            name="add_task",
            description="Add a new task to the existing plan. Returns the new task ID.",
        )
        self.manager = manager

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Description of the task to add",
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                    "description": "Initial status for the task (default: pending)",
                },
            },
            "required": ["description"],
        }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        description = parameters["description"]
        status = parameters.get("status", "pending")

        try:
            task_id = await self.manager.add_task(description, status)

            return ToolResult(
                success=True,
                result={"task_id": task_id, "description": description},
                error=None,
                metadata={"task_id": task_id},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to add task: {str(e)}",
                metadata={},
            )


class GetPlanSummaryTool(BaseTool):
    """Get a summary of the plan's progress."""

    def __init__(self, manager: PlanManager) -> None:
        super().__init__(
            name="get_plan_summary",
            description="Get a summary of the plan including progress statistics and task counts by status.",
        )
        self.manager = manager

    @property
    def parameters(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            summary = await self.manager.get_summary()

            return ToolResult(
                success=True,
                result=summary,
                error=None,
                metadata={"total_tasks": summary["total_tasks"]},
            )

        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to get plan summary: {str(e)}",
                metadata={},
            )


def create_planning_tools(plan_file: Path) -> Sequence[BaseTool]:
    """
    Create a list of planning tools with shared state management.

    Args:
        plan_file: Path to the JSON file for storing the plan

    Returns:
        List of planning tool instances that share the same PlanManager

    Example:
        >>> from pathlib import Path
        >>> tools = create_planning_tools(Path("/tmp/my_plan.json"))
        >>> agent = Agent(name="planner", tools=tools)
    """
    manager = PlanManager(plan_file)

    return [
        WritePlanTool(manager),
        ReadPlanTool(manager),
        UpdateTaskStatusTool(manager),
        AddTaskTool(manager),
        GetPlanSummaryTool(manager),
    ]
