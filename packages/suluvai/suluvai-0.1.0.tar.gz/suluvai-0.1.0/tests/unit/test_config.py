"""
Unit Tests: Configuration
Tests AgentConfig and SubAgent dataclasses
Developed by SagaraGlobal
"""
import pytest
from langchain_core.tools import tool
from suluvai import AgentConfig, SubAgent


class TestAgentConfig:
    """Test AgentConfig dataclass"""
    
    def test_defaults(self):
        """Test default configuration values"""
        config = AgentConfig()
        
        assert config.storage_mode == "virtual"
        assert config.local_storage_path == "./agent_workspace"
        assert config.memory_type == "conversation"
        assert config.enable_streaming is True
        assert config.include_planning is True
        assert config.include_filesystem is True
    
    def test_custom_values(self):
        """Test custom configuration values"""
        config = AgentConfig(
            storage_mode="local",
            local_storage_path="./custom_path",
            memory_type="working",
            enable_streaming=False,
            include_planning=False,
            include_filesystem=False
        )
        
        assert config.storage_mode == "local"
        assert config.local_storage_path == "./custom_path"
        assert config.memory_type == "working"
        assert config.enable_streaming is False
        assert config.include_planning is False
        assert config.include_filesystem is False
    
    def test_hybrid_storage(self):
        """Test hybrid storage configuration"""
        config = AgentConfig(storage_mode="hybrid")
        assert config.storage_mode == "hybrid"
    
    def test_memory_types(self):
        """Test different memory type configurations"""
        config1 = AgentConfig(memory_type="conversation")
        config2 = AgentConfig(memory_type="working")
        config3 = AgentConfig(memory_type="none")
        
        assert config1.memory_type == "conversation"
        assert config2.memory_type == "working"
        assert config3.memory_type == "none"


class TestSubAgent:
    """Test SubAgent dataclass"""
    
    @tool
    def dummy_tool(x: str) -> str:
        """A dummy tool for testing"""
        return f"processed: {x}"
    
    def test_create(self):
        """Test SubAgent creation"""
        subagent = SubAgent(
            name="test_agent",
            description="Test subagent",
            tools=[self.dummy_tool],
            instructions="Test instructions"
        )
        
        assert subagent.name == "test_agent"
        assert subagent.description == "Test subagent"
        assert len(subagent.tools) == 1
        assert subagent.instructions == "Test instructions"
        assert subagent.model is None
    
    def test_with_model(self):
        """Test SubAgent with custom model"""
        from unittest.mock import Mock
        mock_model = Mock()
        
        subagent = SubAgent(
            name="test",
            description="Test",
            tools=[],
            instructions="Test",
            model=mock_model
        )
        
        assert subagent.model is mock_model
    
    def test_empty_tools(self):
        """Test SubAgent with no tools"""
        subagent = SubAgent(
            name="test",
            description="Test",
            tools=[],
            instructions="Test"
        )
        
        assert subagent.tools == []
    
    def test_multiple_tools(self):
        """Test SubAgent with multiple tools"""
        @tool
        def tool1(x: str) -> str:
            """Tool 1"""
            return x
        
        @tool
        def tool2(x: str) -> str:
            """Tool 2"""
            return x
        
        subagent = SubAgent(
            name="test",
            description="Test",
            tools=[tool1, tool2],
            instructions="Test"
        )
        
        assert len(subagent.tools) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
