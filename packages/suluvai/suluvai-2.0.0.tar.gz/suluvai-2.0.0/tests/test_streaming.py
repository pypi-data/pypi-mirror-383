"""
Tests for streaming functionality
"""

import pytest
from suluvai.streaming import (
    StreamEvent,
    StreamEventType,
    StreamingCallback
)


def test_stream_event_creation():
    """Test StreamEvent creation"""
    event = StreamEvent(
        event_type=StreamEventType.TOKEN,
        data="Hello",
        metadata={"run_id": "123"}
    )
    
    assert event.event_type == StreamEventType.TOKEN
    assert event.data == "Hello"
    assert event.metadata["run_id"] == "123"


def test_stream_event_to_dict():
    """Test StreamEvent to_dict conversion"""
    event = StreamEvent(
        event_type=StreamEventType.TOOL_START,
        data={"tool_name": "test_tool", "input": {"arg": "value"}},
        metadata={}
    )
    
    event_dict = event.to_dict()
    assert event_dict["event_type"] == StreamEventType.TOOL_START
    assert event_dict["data"]["tool_name"] == "test_tool"


def test_stream_event_to_json():
    """Test StreamEvent to_json conversion"""
    event = StreamEvent(
        event_type=StreamEventType.TOKEN,
        data="test",
        metadata={}
    )
    
    json_str = event.to_json()
    assert isinstance(json_str, str)
    assert "test" in json_str


def test_streaming_callback():
    """Test StreamingCallback base class"""
    
    class TestCallback(StreamingCallback):
        def __init__(self):
            self.tokens = []
            self.tools = []
        
        def on_token(self, token: str, **kwargs):
            self.tokens.append(token)
        
        def on_tool_start(self, tool_name: str, tool_input: dict, **kwargs):
            self.tools.append(tool_name)
    
    callback = TestCallback()
    
    # Simulate callbacks
    callback.on_token("Hello")
    callback.on_token(" World")
    callback.on_tool_start("test_tool", {"arg": "value"})
    
    assert len(callback.tokens) == 2
    assert callback.tokens == ["Hello", " World"]
    assert len(callback.tools) == 1
    assert callback.tools[0] == "test_tool"


def test_stream_event_types():
    """Test all StreamEventType values"""
    assert hasattr(StreamEventType, "TOKEN")
    assert hasattr(StreamEventType, "TOOL_START")
    assert hasattr(StreamEventType, "TOOL_END")
    assert hasattr(StreamEventType, "AGENT_ACTION")
    assert hasattr(StreamEventType, "AGENT_FINISH")
    assert hasattr(StreamEventType, "ERROR")
    assert hasattr(StreamEventType, "METADATA")


@pytest.mark.asyncio
async def test_stream_agent_events_mock():
    """Test streaming with mock agent (requires implementation)"""
    # This would test the actual streaming with a mock agent
    # Placeholder for integration test
    pass


@pytest.mark.asyncio
async def test_stream_tokens_only_mock():
    """Test token-only streaming (requires implementation)"""
    # Placeholder for integration test
    pass
