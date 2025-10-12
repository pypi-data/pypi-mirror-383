"""
Tool system for picoagents framework.

This module provides the foundation for tools that agents can use to
interact with the world beyond text generation.
"""

from ._base import BaseTool, FunctionTool
from ._core_tools import create_core_tools
from ._planning_tools import create_planning_tools

try:
    from ._research_tools import create_research_tools

    RESEARCH_TOOLS_AVAILABLE = True
except ImportError:
    RESEARCH_TOOLS_AVAILABLE = False

from ._coding_tools import create_coding_tools

__all__ = [
    "BaseTool",
    "FunctionTool",
    "create_core_tools",
    "create_research_tools",
    "create_coding_tools",
    "create_planning_tools",
    "RESEARCH_TOOLS_AVAILABLE",
]
