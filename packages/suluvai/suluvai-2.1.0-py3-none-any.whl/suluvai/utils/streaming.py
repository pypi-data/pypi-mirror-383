"""
Streaming support for Zita Agents
Enables real-time streaming of events, tokens, and tool calls
"""

from typing import AsyncIterator, Dict, Any, Literal
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
import json


class StreamEventType:
    """Event types for streaming"""
    TOKEN = "token"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    AGENT_ACTION = "agent_action"
    AGENT_FINISH = "agent_finish"
    ERROR = "error"
    METADATA = "metadata"


class StreamEvent:
    """Represents a streaming event"""
    
    def __init__(
        self,
        event_type: str,
        data: Any,
        metadata: Dict[str, Any] = None
    ):
        self.event_type = event_type
        self.data = data
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_type": self.event_type,
            "data": self.data,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())


async def stream_agent_events(agent, input_data: Dict[str, Any]) -> AsyncIterator[StreamEvent]:
    """
    Stream events from agent execution.
    
    Args:
        agent: The compiled LangGraph agent
        input_data: Input dictionary with messages, files, todos, etc.
        
    Yields:
        StreamEvent objects for each event during execution
        
    Example:
        async for event in stream_agent_events(agent, {"messages": [("user", "Hello")]}):
            if event.event_type == StreamEventType.TOKEN:
                print(event.data, end="", flush=True)
            elif event.event_type == StreamEventType.TOOL_START:
                print(f"\\n[Tool: {event.data['tool_name']}]")
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
        agent: The compiled LangGraph agent
        input_data: Input dictionary with messages, files, todos, etc.
        
    Yields:
        String tokens as they are generated
        
    Example:
        async for token in stream_tokens_only(agent, {"messages": [("user", "Hello")]}):
            print(token, end="", flush=True)
    """
    async for event in stream_agent_events(agent, input_data):
        if event.event_type == StreamEventType.TOKEN:
            yield event.data


def stream_agent_sync(agent, input_data: Dict[str, Any]):
    """
    Synchronous streaming for agents (uses stream method).
    
    Args:
        agent: The compiled LangGraph agent
        input_data: Input dictionary
        
    Yields:
        Tuples of (node_name, state_update) for each step
        
    Example:
        for node_name, state_update in stream_agent_sync(agent, input_data):
            print(f"Node: {node_name}")
            if "messages" in state_update:
                print(f"Messages: {state_update['messages']}")
    """
    for chunk in agent.stream(input_data, stream_mode="updates"):
        for node_name, state_update in chunk.items():
            yield node_name, state_update


class StreamingCallback:
    """
    Callback handler for streaming events.
    Useful for custom handling of streaming events.
    """
    
    def on_token(self, token: str, **kwargs):
        """Called when a new token is generated"""
        pass
    
    def on_tool_start(self, tool_name: str, tool_input: Dict[str, Any], **kwargs):
        """Called when a tool starts executing"""
        pass
    
    def on_tool_end(self, tool_name: str, tool_output: Any, **kwargs):
        """Called when a tool finishes executing"""
        pass
    
    def on_agent_action(self, action: Any, **kwargs):
        """Called when agent takes an action"""
        pass
    
    def on_agent_finish(self, output: Dict[str, Any], **kwargs):
        """Called when agent finishes execution"""
        pass
    
    def on_error(self, error: Exception, **kwargs):
        """Called when an error occurs"""
        pass


async def stream_with_callback(
    agent, 
    input_data: Dict[str, Any],
    callback: StreamingCallback
) -> Dict[str, Any]:
    """
    Stream agent execution and trigger callbacks.
    
    Args:
        agent: The compiled LangGraph agent
        input_data: Input dictionary
        callback: StreamingCallback instance
        
    Returns:
        Final agent output
        
    Example:
        class MyCallback(StreamingCallback):
            def on_token(self, token: str, **kwargs):
                print(token, end="")
        
        result = await stream_with_callback(agent, input_data, MyCallback())
    """
    final_output = None
    
    try:
        async for event in stream_agent_events(agent, input_data):
            if event.event_type == StreamEventType.TOKEN:
                callback.on_token(event.data, **event.metadata)
                
            elif event.event_type == StreamEventType.TOOL_START:
                callback.on_tool_start(
                    event.data["tool_name"],
                    event.data["input"],
                    **event.metadata
                )
                
            elif event.event_type == StreamEventType.TOOL_END:
                callback.on_tool_end(
                    event.data["tool_name"],
                    event.data["output"],
                    **event.metadata
                )
                
            elif event.event_type == StreamEventType.AGENT_FINISH:
                final_output = event.data
                callback.on_agent_finish(event.data, **event.metadata)
                
            elif event.event_type == StreamEventType.ERROR:
                error = Exception(event.data.get("error", "Unknown error"))
                callback.on_error(error, **event.metadata)
                
    except Exception as e:
        callback.on_error(e)
        raise
    
    return final_output
