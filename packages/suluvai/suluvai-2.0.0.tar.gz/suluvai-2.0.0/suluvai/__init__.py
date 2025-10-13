"""
SuluvAI - Production-ready Deep Agents implementation
Built on stable LangGraph with advanced streaming and storage capabilities

Features:
- Sub-agents with specialized roles
- Virtual filesystem for large data
- TODO list for task planning
- File management tools
- Multi-turn conversations with state
- LangSmith tracing for monitoring & debugging
- **NEW** Token & event streaming support
- **NEW** Local file storage with multi-level folders
- **NEW** Enhanced filesystem operations

Usage:
    from suluvai import create_enhanced_agent, EnhancedAgentConfig
    
    # Create enhanced agent with streaming and local storage
    config = EnhancedAgentConfig(
        storage_mode="local",
        storage_path="./my_workspace"
    )
    
    agent, storage = create_enhanced_agent(
        model=llm,
        tools=[...],
        subagents=[...],
        instructions="You are a helpful assistant",
        config=config
    )
    
    # Stream tokens in real-time
    from suluvai.streaming import stream_agent_events, StreamEventType
    
    async for event in stream_agent_events(agent, {"messages": [("user", "Hello")]}):
        if event.event_type == StreamEventType.TOKEN:
            print(event.data, end="")
"""

from suluvai.agent import create_suluvai_agent
from suluvai.enhanced_agent import create_enhanced_agent, EnhancedAgentConfig
from suluvai.state import SuluvAIAgentState
from suluvai.subagent import SubAgent
from suluvai.local_storage import LocalFileStorage, FileMetadata
from suluvai.streaming import (
    stream_agent_events,
    stream_tokens_only,
    stream_agent_sync,
    stream_with_callback,
    StreamEvent,
    StreamEventType,
    StreamingCallback
)
from suluvai.tracing import (
    enable_langsmith_tracing,
    disable_langsmith_tracing,
    get_trace_url
)

__version__ = "2.0.0"
__all__ = [
    # Core agent creation
    "create_suluvai_agent",
    "create_enhanced_agent",
    "EnhancedAgentConfig",
    
    # State and configuration
    "SuluvAIAgentState",
    "SubAgent",
    
    # Local storage
    "LocalFileStorage",
    "FileMetadata",
    
    # Streaming
    "stream_agent_events",
    "stream_tokens_only",
    "stream_agent_sync",
    "stream_with_callback",
    "StreamEvent",
    "StreamEventType",
    "StreamingCallback",
    
    # Tracing
    "enable_langsmith_tracing",
    "disable_langsmith_tracing",
    "get_trace_url"
]
