"""
Tool wrappers to make tools state-aware
Allows tools to access and modify state["files"], state["todos"], etc.
"""

from typing import List, Any
from langchain_core.tools import BaseTool, StructuredTool
from functools import wraps
import inspect


def create_stateful_tools(tools: List[BaseTool]) -> List[BaseTool]:
    """
    Wrap tools to make them aware of the agent state.
    
    This allows filesystem and TODO tools to actually read/write to state.
    """
    stateful_tools = []
    
    for tool in tools:
        # Check if this is a filesystem or TODO tool that needs state access
        if tool.name in ['write_file', 'read_file', 'list_files', 'delete_file',
                         'write_todos', 'get_todos', 'mark_todo_done']:
            # These tools need to be wrapped with state access
            # For now, we'll pass them through and handle state in the graph
            stateful_tools.append(tool)
        else:
            # Regular tools pass through unchanged
            stateful_tools.append(tool)
    
    return stateful_tools


def bind_tool_to_state(tool: BaseTool, state_key: str):
    """
    Bind a tool to a specific state key (e.g., 'files', 'todos').
    
    This is used internally to connect filesystem/TODO tools to the state.
    """
    # This would be implemented in the graph nodes
    # For now, tools work directly with state in the compiled graph
    pass
