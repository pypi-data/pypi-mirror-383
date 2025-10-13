"""
Tests for agent functionality
"""

import pytest
from unittest.mock import MagicMock, patch
from suluvai import (
    create_suluvai_agent,
    create_enhanced_agent,
    EnhancedAgentConfig,
    SubAgent,
    SuluvAIAgentState
)


def test_enhanced_agent_config():
    """Test EnhancedAgentConfig creation"""
    config = EnhancedAgentConfig(
        storage_mode="local",
        storage_path="./test_workspace",
        enable_streaming=True
    )
    
    assert config.storage_mode == "local"
    assert config.storage_path == "./test_workspace"
    assert config.enable_streaming is True


def test_enhanced_agent_config_defaults():
    """Test EnhancedAgentConfig default values"""
    config = EnhancedAgentConfig()
    
    assert config.storage_mode == "local"
    assert config.storage_path == "./agent_workspace"
    assert config.enable_streaming is True
    assert config.include_filesystem is True
    assert config.include_todos is True


def test_subagent_creation():
    """Test SubAgent creation"""
    subagent = SubAgent(
        name="test_agent",
        description="Test subagent",
        tools=[],
        instructions="Test instructions"
    )
    
    assert subagent.name == "test_agent"
    assert subagent.description == "Test subagent"
    assert subagent.instructions == "Test instructions"
    assert subagent.tools == []


@pytest.mark.skip(reason="Requires LLM configuration")
def test_create_basic_agent(mock_llm):
    """Test basic agent creation"""
    agent = create_suluvai_agent(
        model=mock_llm,
        tools=[],
        instructions="Test agent"
    )
    
    assert agent is not None


@pytest.mark.skip(reason="Requires LLM configuration")
def test_create_enhanced_agent_with_config(mock_llm, temp_storage_path):
    """Test enhanced agent creation with config"""
    config = EnhancedAgentConfig(
        storage_mode="local",
        storage_path=temp_storage_path
    )
    
    agent, storage = create_enhanced_agent(
        model=mock_llm,
        tools=[],
        instructions="Test agent",
        config=config
    )
    
    assert agent is not None
    assert storage is not None
    assert storage.base_path.exists()


@pytest.mark.skip(reason="Requires LLM configuration")
def test_agent_with_subagents(mock_llm):
    """Test agent creation with subagents"""
    subagent = SubAgent(
        name="helper",
        description="Helper agent",
        tools=[],
        instructions="Help with tasks"
    )
    
    agent = create_suluvai_agent(
        model=mock_llm,
        tools=[],
        subagents=[subagent],
        instructions="Main agent"
    )
    
    assert agent is not None


def test_suluvai_agent_state():
    """Test SuluvAIAgentState structure"""
    # This tests that the state schema has the expected structure
    # Actual instantiation would require LangGraph setup
    assert hasattr(SuluvAIAgentState, '__annotations__')
    annotations = SuluvAIAgentState.__annotations__
    
    assert 'files' in annotations
    assert 'todos' in annotations
    assert 'metadata' in annotations
