"""
Enhanced state definition for SuluvAI Agents
Manages messages, files, todos, and memory
"""

from typing import Annotated, Dict, Any, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.prebuilt.chat_agent_executor import AgentState


class SuluvAIState(AgentState):
    """
    Enhanced state schema for SuluvAI Agent (DeepAgents compatible + enhanced).
    
    Inherited from AgentState:
    - messages: Chat history with automatic merging
    - remaining_steps: Number of remaining agent steps
    - is_last_step: Whether this is the last step
    
    Core Fields (DeepAgents Compatible):
    - files: Virtual/local filesystem for storing data
    - todos: Task planning list
    
    Enhanced Fields:
    - memory: Multi-type memory storage
    - metadata: Execution metadata (tokens, cost, etc.)
    """
    
    # Core state (deepagents compatible)
    files: Dict[str, Any]  # Virtual filesystem
    todos: List[Dict[str, Any]]  # Task planning
    
    # Enhanced features
    memory: Dict[str, Any]  # Memory storage
    metadata: Dict[str, Any]  # Execution metadata
