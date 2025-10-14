"""
Enhanced streaming utilities for SuluvAI agents
"""

from typing import AsyncIterator, Dict, Any
from langchain_core.runnables import RunnableConfig
from suluvai.utils.streaming import StreamEvent, StreamEventType


async def stream_agent(agent, input_data: Dict[str, Any]) -> AsyncIterator[StreamEvent]:
    """
    Stream events from agent execution with enhanced tracking.
    
    Args:
        agent: The compiled SuluvAI agent
        input_data: Input dictionary with messages, files, etc.
        
    Yields:
        StreamEvent objects for each event during execution
        
    Example:
        async for event in stream_agent(agent, {"messages": [{"role": "user", "content": "Hello"}]}):
            if event.type == "token":
                print(event.data, end="", flush=True)
            elif event.type == "tool_call":
                print(f"\\n[Using: {event.data['tool']}]")
            elif event.type == "file_created":
                print(f"\\n[Created: {event.data['filepath']}]")
    """
    config = RunnableConfig(
        callbacks=[],
        recursion_limit=25
    )
    
    try:
        # Stream events from the agent
        async for event in agent.astream_events(input_data, config=config, version="v2"):
            event_kind = event.get("event")
            
            # Handle different event types
            if event_kind == "on_chat_model_stream":
                # Token streaming from LLM
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield StreamEvent(
                        event_type=StreamEventType.TOKEN,
                        data=chunk.content,
                        metadata={"run_id": event.get("run_id")}
                    )
                    
            elif event_kind == "on_tool_start":
                # Tool execution starting
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                
                # Enhanced: Detect file operations
                if "write_file" in tool_name or "read_file" in tool_name:
                    yield StreamEvent(
                        event_type="file_operation",
                        data={
                            "operation": tool_name,
                            "details": tool_input
                        },
                        metadata={"run_id": event.get("run_id")}
                    )
                
                # Detect planning
                if "write_todos" in tool_name or "todo" in tool_name.lower():
                    yield StreamEvent(
                        event_type="planning",
                        data={"todos": tool_input},
                        metadata={"run_id": event.get("run_id")}
                    )
                
                # Detect subagent calls
                if tool_name.startswith("call_"):
                    subagent_name = tool_name.replace("call_", "")
                    yield StreamEvent(
                        event_type="subagent_start",
                        data={
                            "name": subagent_name,
                            "task": tool_input.get("task", "")
                        },
                        metadata={"run_id": event.get("run_id")}
                    )
                
                yield StreamEvent(
                    event_type=StreamEventType.TOOL_START,
                    data={
                        "tool_name": tool_name,
                        "input": tool_input
                    },
                    metadata={"run_id": event.get("run_id")}
                )
                
            elif event_kind == "on_tool_end":
                # Tool execution completed
                tool_name = event.get("name", "unknown")
                tool_output = event.get("data", {}).get("output")
                
                # Detect file creation
                if "write_file" in tool_name and tool_output:
                    yield StreamEvent(
                        event_type="file_write",
                        data={"filepath": "file", "output": tool_output},
                        metadata={"run_id": event.get("run_id")}
                    )
                
                # Detect subagent completion
                if tool_name.startswith("call_"):
                    subagent_name = tool_name.replace("call_", "")
                    yield StreamEvent(
                        event_type="subagent_end",
                        data={
                            "subagent": subagent_name,
                            "output": tool_output
                        },
                        metadata={"run_id": event.get("run_id")}
                    )
                
                yield StreamEvent(
                    event_type=StreamEventType.TOOL_END,
                    data={
                        "tool_name": tool_name,
                        "output": tool_output
                    },
                    metadata={"run_id": event.get("run_id")}
                )
                
            elif event_kind == "on_chain_end":
                # Check if this is the final agent output
                if event.get("name") == "LangGraph":
                    output = event.get("data", {}).get("output", {})
                    yield StreamEvent(
                        event_type=StreamEventType.AGENT_FINISH,
                        data=output,
                        metadata={"run_id": event.get("run_id")}
                    )
                    
    except Exception as e:
        yield StreamEvent(
            event_type=StreamEventType.ERROR,
            data={"error": str(e), "error_type": type(e).__name__},
            metadata={}
        )


async def stream_tokens_only(agent, input_data: Dict[str, Any]) -> AsyncIterator[str]:
    """
    Stream only tokens from the agent (simpler interface).
    
    Args:
        agent: The compiled SuluvAI agent
        input_data: Input dictionary
        
    Yields:
        String tokens as they are generated
        
    Example:
        async for token in stream_tokens_only(agent, {"messages": [{"role": "user", "content": "Hello"}]}):
            print(token, end="", flush=True)
    """
    async for event in stream_agent(agent, input_data):
        if event.event_type == StreamEventType.TOKEN:
            yield event.data
