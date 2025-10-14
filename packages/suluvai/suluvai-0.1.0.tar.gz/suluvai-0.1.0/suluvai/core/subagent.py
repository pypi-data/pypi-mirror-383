"""
SubAgent configuration for Zita Agents
"""

from typing import List, Optional, Any, Callable
from dataclasses import dataclass


@dataclass
class SubAgent:
    """
    Configuration for a specialized sub-agent.
    
    Args:
        name: Unique identifier for the subagent
        description: What this subagent does (shown to main agent)
        tools: List of tool objects this subagent can use
        instructions: System prompt for this subagent
        model: Optional specific model for this subagent (defaults to main model)
    
    Example:
        data_fetcher = SubAgent(
            name="data_fetcher",
            description="Fetches data from SAP database",
            tools=[get_schema, execute_query],
            instructions="You are a SAP data fetcher. Use tools to get data."
        )
    """
    
    name: str
    description: str
    tools: List[Any]
    instructions: str
    model: Optional[Any] = None
