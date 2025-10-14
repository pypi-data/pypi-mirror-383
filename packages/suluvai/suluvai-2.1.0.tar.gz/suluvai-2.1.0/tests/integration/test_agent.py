"""
Integration Tests: Agent Creation and Execution
Tests complete agent functionality with LLM
Developed by SagaraGlobal
"""
import pytest
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import create_agent, AgentConfig, SubAgent

load_dotenv()

skip_if_no_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


@tool
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b


@tool
def get_weather(city: str) -> str:
    """Get weather for a city (mock)"""
    return f"Weather in {city}: Sunny, 72°F"


class TestAgentCreation:
    """Test agent creation with various configurations"""
    
    @skip_if_no_key
    def test_simple_agent(self):
        """Test creating a simple agent"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="You are a calculator. Use add_numbers to add.",
            model=llm
        )
        
        assert agent is not None
        assert hasattr(agent, 'suluvai_config')
        assert hasattr(agent, 'suluvai_storage')
    
    @skip_if_no_key
    def test_agent_with_config(self):
        """Test agent with custom configuration"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        config = AgentConfig(
            storage_mode="virtual",
            include_planning=False,
            include_filesystem=False
        )
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="Test agent",
            config=config,
            model=llm
        )
        
        assert agent is not None
        assert agent.suluvai_config.storage_mode == "virtual"
        assert agent.suluvai_config.include_planning is False
    
    @skip_if_no_key
    def test_agent_with_multiple_tools(self):
        """Test agent with multiple tools"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent = create_agent(
            tools=[add_numbers, multiply_numbers, get_weather],
            instructions="You have math and weather tools.",
            model=llm
        )
        
        assert agent is not None
    
    @skip_if_no_key
    def test_agent_with_subagent_dict(self):
        """Test agent with subagent in dict format"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        calculator = {
            "name": "calculator",
            "description": "Performs calculations",
            "prompt": "You are a calculator. Use tools to calculate.",
            "tools": [add_numbers]
        }
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="Delegate math to calculator.",
            subagents=[calculator],
            model=llm
        )
        
        assert agent is not None
    
    @skip_if_no_key
    def test_agent_with_subagent_object(self):
        """Test agent with SubAgent object"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        calculator = SubAgent(
            name="calculator",
            description="Performs calculations",
            tools=[add_numbers],
            instructions="You are a calculator."
        )
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="Delegate math to calculator.",
            subagents=[calculator],
            model=llm
        )
        
        assert agent is not None


class TestAgentExecution:
    """Test agent execution and responses"""
    
    @skip_if_no_key
    def test_simple_execution(self):
        """Test basic agent execution"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="You are a calculator. Use add_numbers to add numbers.",
            model=llm
        )
        
        result = agent.invoke({
            "messages": [("user", "What is 5 + 3?")]
        })
        
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) > 0
        
        # Check that answer contains 8
        final_message = str(result["messages"][-1].content)
        assert "8" in final_message
    
    @skip_if_no_key
    def test_tool_execution(self):
        """Test that tools are actually called"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent = create_agent(
            tools=[multiply_numbers],
            instructions="You are a calculator. Use multiply_numbers to multiply.",
            model=llm
        )
        
        result = agent.invoke({
            "messages": [("user", "Multiply 6 by 7")]
        })
        
        final_message = str(result["messages"][-1].content)
        assert "42" in final_message
    
    @skip_if_no_key
    def test_multiple_turns(self):
        """Test multi-turn conversation"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="You are a calculator.",
            model=llm
        )
        
        # First turn
        result1 = agent.invoke({
            "messages": [("user", "Add 2 and 3")]
        })
        
        # Second turn with history
        result2 = agent.invoke({
            "messages": result1["messages"] + [("user", "Now add 10 to that")]
        })
        
        assert result2 is not None
        final_message = str(result2["messages"][-1].content)
        assert "15" in final_message
    
    @skip_if_no_key
    def test_subagent_delegation(self):
        """Test that subagents can be called"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        calculator = {
            "name": "calc",
            "description": "Does math",
            "prompt": "You are a calculator. Use add_numbers and return just the number.",
            "tools": [add_numbers]
        }
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="When asked to add, use call_calc subagent. Be brief.",
            subagents=[calculator],
            model=llm
        )
        
        result = agent.invoke(
            {"messages": [("user", "Add 4 and 5")]},
            {"recursion_limit": 10}
        )
        
        assert result is not None
        final_message = str(result["messages"][-1].content)
        assert "9" in final_message


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
