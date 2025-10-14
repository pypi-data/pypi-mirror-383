"""
SuluvAI - Production-ready Agentic Framework
DeepAgents compatible with enhanced workflows, memory, and storage

Features:
- 🎯 DeepAgents-style API (user controls prompts)
- 🔄 Workflow orchestration (sequential, parallel, conditional, map-reduce)
- 🧠 Multi-type memory systems (conversation, semantic, working)
- 💾 Virtual/Local/Hybrid storage with multi-level directories
- 📡 Enhanced streaming (tokens, events, progress tracking)
- 🤖 Dynamic sub-agents with specialized roles
- 📋 Built-in planning tools
- 🏭 Production-ready on stable LangGraph

Usage:
    from suluvai import create_agent, AgentConfig, WorkflowBuilder

    # Simple agent (deepagents style)
    agent = create_agent(
        tools=[search_tool],
        instructions="You are a researcher. Use search_tool to find information.",
        model=ChatOpenAI(model="gpt-4")
    )

    # With configuration
    agent = create_agent(
        tools=[search_tool],
        instructions="You are an analyst...",
        config=AgentConfig(
            storage_mode="local",          # Save files to disk
            local_storage_path="./workspace",
            memory_type="conversation",    # Remember context
            enable_streaming=True          # Stream responses
        ),
        model=ChatOpenAI(model="gpt-4")
    )

    # With subagents (deepagents compatible)
    agent = create_agent(
        tools=[search_tool],
        instructions="You coordinate research...",
        subagents=[
            {
                "name": "researcher",
                "description": "Searches the web",
                "prompt": "You are a research specialist...",
                "tools": ["internet_search"]
            }
        ],
        model=ChatOpenAI(model="gpt-4")
    )

    # Workflows
    workflow = WorkflowBuilder() \\
        .sequential() \\
        .add_step("fetch", fetcher_agent) \\
        .add_step("analyze", analyzer_agent) \\
        .build()

    result = workflow.execute({"task": "..."})

    # Streaming
    from suluvai import stream_agent

    async for event in stream_agent(agent, {"messages": [{"role": "user", "content": "Hello"}]}):
        if event.type == "token":
            print(event.data, end="")
"""

# Disable LangSmith tracing by default unless explicitly enabled
import os
if "LANGCHAIN_TRACING_V2" not in os.environ:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Core API
from suluvai.core import create_agent, AgentConfig, SuluvAIState, SubAgent

# Workflows
from suluvai.workflows import WorkflowBuilder, BaseWorkflow, WorkflowResult

# Storage
from suluvai.storage.local_storage import LocalFileStorage, FileMetadata
from suluvai.storage import VirtualStorage, LocalStorage, HybridStorage

# Memory
from suluvai.memory import ConversationMemory, WorkingMemory

# Streaming & Utils
from suluvai.utils import (
    stream_agent,
    stream_tokens_only,
    stream_agent_events,
    stream_agent_sync,
    stream_with_callback,
    StreamEvent,
    StreamEventType,
    StreamingCallback,
    enable_langsmith_tracing,
    disable_langsmith_tracing,
    get_trace_url
)

__version__ = "2.1.0"
__all__ = [
    # Core API
    "create_agent",
    "AgentConfig",
    "SuluvAIState",
    "SubAgent",

    # Workflows
    "WorkflowBuilder",
    "BaseWorkflow",
    "WorkflowResult",

    # Storage
    "LocalFileStorage",
    "FileMetadata",
    "VirtualStorage",
    "LocalStorage",
    "HybridStorage",

    # Memory
    "ConversationMemory",
    "WorkingMemory",

    # Streaming
    "stream_agent",
    "stream_tokens_only",
    "stream_agent_events",
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
