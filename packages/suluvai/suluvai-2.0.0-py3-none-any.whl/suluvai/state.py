"""
State definition for SuluvAI Agents
Manages messages, files, and todos
"""

from typing import Annotated, Dict, Any, List, Union
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.prebuilt.chat_agent_executor import AgentState


class SuluvAIAgentState(AgentState):
    """
    State schema for SuluvAI Agent.
    Extends AgentState to include filesystem and todos.
    
    Inherited from AgentState:
    - messages: Chat history with automatic merging
    - remaining_steps: Number of remaining agent steps
    - is_last_step: Whether this is the last step
    
    Additional Fields:
    - files: Virtual filesystem for storing data (CSVs, JSONs, etc.)
    - todos: Task list for planning
    - metadata: Additional context
    """
    
    # Virtual filesystem - stores files as strings or bytes
    files: Dict[str, Any]
    
    # TODO list for task planning
    todos: List[Dict[str, Any]]
    
    # Metadata for additional context
    metadata: Dict[str, Any]
