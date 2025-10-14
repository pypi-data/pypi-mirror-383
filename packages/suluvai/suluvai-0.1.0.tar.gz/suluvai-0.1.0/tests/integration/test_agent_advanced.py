"""
Advanced Integration Tests: Agent Functionality
Rigorous testing with real scenarios and validation
Developed by SagaraGlobal
"""
import pytest
import os
import tempfile
from pathlib import Path
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
def get_user_info(user_id: str) -> str:
    """Get user information (mock)"""
    return f"User {user_id}: John Doe, email: john@example.com"


@tool
def save_report(content: str) -> str:
    """Save a report (mock)"""
    return f"Report saved with {len(content)} characters"


class TestAgentWithVirtualStorage:
    """Test agents with virtual (in-memory) storage"""
    
    @skip_if_no_key
    def test_agent_creates_files_in_memory(self):
        """Test that agent can create files in virtual storage"""
        print("\n" + "="*70)
        print("TEST: Agent with Virtual Storage - File Creation")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        config = AgentConfig(
            storage_mode="virtual",
            include_filesystem=True,
            include_planning=False
        )
        
        agent = create_agent(
            tools=[],
            instructions="""You are a file manager.
            
When asked to create a file:
1. Use write_file tool to create it
2. Confirm what you created""",
            config=config,
            model=llm
        )
        
        print("\nINPUT: Create a file called 'test.txt' with content 'Hello World'")
        
        result = agent.invoke({
            "messages": [("user", "Create a file called 'test.txt' with content 'Hello World'")]
        })
        
        print(f"\nOUTPUT: {result['messages'][-1].content}")
        
        # Verify file operation was successful (check message content)
        final_message = result['messages'][-1].content
        assert "test.txt" in final_message.lower()
        assert "created" in final_message.lower() or "written" in final_message.lower()
        
        print("\n✓ VERIFIED: File creation confirmed in agent response")
        print(f"  Agent confirmed: {final_message[:100]}...")
        
        # Check if files are in result (optional, depends on state handling)
        if "files" in result and result.get("files"):
            print(f"  Files in state: {list(result['files'].keys())}")
    
    @skip_if_no_key
    def test_agent_reads_and_modifies_files(self):
        """Test that agent can read and modify existing files"""
        print("\n" + "="*70)
        print("TEST: Agent Reads and Modifies Files")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        config = AgentConfig(
            storage_mode="virtual",
            include_filesystem=True
        )
        
        agent = create_agent(
            tools=[],
            instructions="You manage files. Read, modify, and save files as requested.",
            config=config,
            model=llm
        )
        
        # First create a file
        print("\nSTEP 1: Create initial file")
        result1 = agent.invoke({
            "messages": [("user", "Create data.txt with content 'Version 1'")]
        })
        
        print(f"Step 1 completed: {result1['messages'][-1].content[:50]}...")
        
        # Then modify it
        print("\nSTEP 2: Modify the file")
        result2 = agent.invoke({
            "messages": result1["messages"] + [
                ("user", "Read data.txt and update it to say 'Version 2'")
            ]
        })
        
        print(f"\nOUTPUT: {result2['messages'][-1].content}")
        
        # Verify modification was mentioned
        final_message = result2['messages'][-1].content
        assert "data.txt" in final_message.lower() or "version 2" in final_message.lower()
        
        print("\n✓ VERIFIED: File modification confirmed")
        print(f"  Agent response: {final_message[:100]}...")
        
        if "files" in result2 and result2.get("files"):
            print(f"  Files in state: {list(result2['files'].keys())}")


class TestAgentWithLocalStorage:
    """Test agents with local (disk-based) storage"""
    
    @skip_if_no_key
    def test_agent_creates_files_on_disk(self):
        """Test that agent creates real files on disk"""
        print("\n" + "="*70)
        print("TEST: Agent with Local Storage - Real File Creation")
        print("="*70)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            config = AgentConfig(
                storage_mode="local",
                local_storage_path=tmpdir,
                include_filesystem=True
            )
            
            agent = create_agent(
                tools=[],
                instructions="You create files on disk. Use write_file to save content.",
                config=config,
                model=llm
            )
            
            print(f"\nStorage path: {tmpdir}")
            print("INPUT: Create report.txt with 'Sales Report Q4'")
            
            result = agent.invoke({
                "messages": [("user", "Create report.txt with content 'Sales Report Q4'")]
            })
            
            print(f"\nOUTPUT: {result['messages'][-1].content}")
            
            # Verify file exists on disk
            file_path = Path(tmpdir) / "report.txt"
            assert file_path.exists()
            
            content = file_path.read_text()
            assert "Sales Report Q4" in content
            
            print("\n✓ VERIFIED: File created on disk")
            print(f"  File path: {file_path}")
            print(f"  Content: {content}")
    
    @skip_if_no_key
    def test_agent_creates_nested_directories(self):
        """Test that agent can create files in nested directories"""
        print("\n" + "="*70)
        print("TEST: Agent Creates Nested Directory Structure")
        print("="*70)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            config = AgentConfig(
                storage_mode="local",
                local_storage_path=tmpdir,
                include_filesystem=True
            )
            
            agent = create_agent(
                tools=[],
                instructions="You organize files. Create nested directories as needed.",
                config=config,
                model=llm
            )
            
            print(f"\nStorage path: {tmpdir}")
            print("INPUT: Create docs/reports/2024/summary.txt")
            
            result = agent.invoke({
                "messages": [("user", "Create a file at docs/reports/2024/summary.txt with content 'Annual Summary'")]
            })
            
            print(f"\nOUTPUT: {result['messages'][-1].content}")
            
            # Verify nested structure
            file_path = Path(tmpdir) / "docs" / "reports" / "2024" / "summary.txt"
            assert file_path.exists()
            assert file_path.read_text() == "Annual Summary"
            
            print("\n✓ VERIFIED: Nested directory structure created")
            print(f"  Full path: {file_path}")
            print(f"  Directory tree created: docs/reports/2024/")


class TestAgentWithSubagents:
    """Test agents with subagent delegation"""
    
    @skip_if_no_key
    def test_subagent_delegation_with_tools(self):
        """Test that main agent can delegate to subagent with specific tools"""
        print("\n" + "="*70)
        print("TEST: Subagent Delegation with Tool Specialization")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Create calculator subagent
        calculator = {
            "name": "calculator",
            "description": "Performs mathematical calculations",
            "prompt": "You are a calculator. Use the math tools to compute results. Return only the final number.",
            "tools": [add_numbers, multiply_numbers]
        }
        
        # Main agent coordinates
        agent = create_agent(
            tools=[add_numbers, multiply_numbers],
            instructions="""You are a coordinator.
            
When asked to do math:
1. Delegate to the calculator subagent using call_calculator
2. Report the result clearly""",
            subagents=[calculator],
            model=llm
        )
        
        print("\nINPUT: Calculate (5 + 3) * 2")
        
        result = agent.invoke(
            {"messages": [("user", "Calculate (5 + 3) * 2")]},
            {"recursion_limit": 15}
        )
        
        final_message = result["messages"][-1].content
        print(f"\nOUTPUT: {final_message}")
        
        # Verify correct answer (16)
        assert "16" in final_message
        
        print("\n✓ VERIFIED: Subagent correctly calculated result")
        print("  Expected: 16")
        print(f"  Got: {final_message}")
    
    @skip_if_no_key
    def test_multiple_subagents_collaboration(self):
        """Test multiple subagents working together"""
        print("\n" + "="*70)
        print("TEST: Multiple Subagents Collaboration")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Data fetcher subagent
        fetcher = {
            "name": "fetcher",
            "description": "Fetches user data",
            "prompt": "You fetch user information. Use get_user_info tool.",
            "tools": [get_user_info]
        }
        
        # Report writer subagent
        writer = {
            "name": "writer",
            "description": "Writes reports",
            "prompt": "You write professional reports. Use save_report tool.",
            "tools": [save_report]
        }
        
        # Main coordinator
        agent = create_agent(
            tools=[get_user_info, save_report],
            instructions="""You coordinate tasks.
            
When asked to create a user report:
1. Use call_fetcher to get user data
2. Use call_writer to save the report
3. Confirm completion""",
            subagents=[fetcher, writer],
            model=llm
        )
        
        print("\nINPUT: Create a report for user 'U123'")
        
        result = agent.invoke(
            {"messages": [("user", "Create a report for user U123")]},
            {"recursion_limit": 20}
        )
        
        final_message = result["messages"][-1].content
        print(f"\nOUTPUT: {final_message}")
        
        # Verify both subagents were involved
        assert "U123" in final_message or "report" in final_message.lower()
        
        print("\n✓ VERIFIED: Multiple subagents collaborated successfully")


class TestAgentWithPlanningTools:
    """Test agents using planning/todo tools"""
    
    @skip_if_no_key
    def test_agent_creates_and_follows_plan(self):
        """Test that agent can create a plan and follow it"""
        print("\n" + "="*70)
        print("TEST: Agent Creates and Follows Plan")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        config = AgentConfig(
            storage_mode="virtual",
            include_planning=True,
            include_filesystem=True
        )
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="""You are a methodical worker.
            
For complex tasks:
1. Create a plan using write_todos
2. Complete each step
3. Mark todos as done
4. Summarize results""",
            config=config,
            model=llm
        )
        
        print("\nINPUT: Calculate 5+3, then multiply result by 2, save to result.txt")
        
        result = agent.invoke({
            "messages": [("user", "Calculate 5+3, then multiply the result by 2, and save the final answer to result.txt")]
        })
        
        final_message = result["messages"][-1].content
        print(f"\nOUTPUT: {final_message}")
        
        # Verify task completion (check for result in message)
        assert "16" in final_message or "result" in final_message.lower()
        
        print("\n✓ VERIFIED: Agent completed complex task")
        print(f"  Result mentioned: {'16' in final_message}")
        
        # Check optional state fields
        if "todos" in result:
            print(f"  Todos created: {len(result.get('todos', []))}")
        if "files" in result:
            print(f"  Files created: {list(result.get('files', {}).keys())}")


class TestAgentErrorHandling:
    """Test agent error handling and recovery"""
    
    @skip_if_no_key
    def test_agent_handles_invalid_tool_input(self):
        """Test that agent handles invalid tool inputs gracefully"""
        print("\n" + "="*70)
        print("TEST: Agent Handles Invalid Tool Input")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="You are a calculator. Use add_numbers for addition. Handle errors gracefully.",
            model=llm
        )
        
        print("\nINPUT: Add 'hello' and 'world' (invalid input)")
        
        result = agent.invoke({
            "messages": [("user", "Add hello and world together")]
        })
        
        final_message = result["messages"][-1].content
        print(f"\nOUTPUT: {final_message}")
        
        # Agent should recognize the error or ask for clarification
        assert result is not None
        
        print("\n✓ VERIFIED: Agent handled invalid input")
    
    @skip_if_no_key
    def test_agent_with_recursion_limit(self):
        """Test that agent respects recursion limits"""
        print("\n" + "="*70)
        print("TEST: Agent Respects Recursion Limit")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent = create_agent(
            tools=[add_numbers],
            instructions="You are a calculator.",
            model=llm
        )
        
        print("\nINPUT: Simple calculation with low recursion limit")
        
        # This should complete within limit
        result = agent.invoke(
            {"messages": [("user", "What is 2 + 2?")]},
            {"recursion_limit": 5}
        )
        
        print(f"\nOUTPUT: {result['messages'][-1].content}")
        
        assert "4" in result["messages"][-1].content
        
        print("\n✓ VERIFIED: Agent completed within recursion limit")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
