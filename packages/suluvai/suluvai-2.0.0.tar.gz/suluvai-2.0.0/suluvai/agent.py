"""
Main agent builder for SuluvAI
Creates deep agents with subagents, filesystem, and TODO support
"""

from typing import List, Optional, Any, Sequence
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END

from suluvai.state import SuluvAIAgentState
from suluvai.subagent import SubAgent
from suluvai.filesystem_tools import write_file, read_file, list_files, delete_file
from suluvai.todo_tools import write_todos, get_todos, mark_todo_done
from suluvai.tool_wrappers import create_stateful_tools


def create_suluvai_agent(
    model: Any,
    tools: Sequence[BaseTool],
    subagents: Optional[List[SubAgent]] = None,
    instructions: str = "You are a helpful assistant.",
    include_filesystem: bool = True,
    include_todos: bool = True,
    state_schema: type = SuluvAIAgentState
):
    """
    Create a SuluvAI Agent with sub-agents, filesystem, and TODO support.
    
    Args:
        model: LLM model to use (e.g., ChatOpenAI)
        tools: List of tool objects for the main agent
        subagents: Optional list of SubAgent configurations
        instructions: System prompt for the main agent
        include_filesystem: Whether to include file management tools
        include_todos: Whether to include TODO list tools
        state_schema: Custom state schema (defaults to SuluvAIAgentState)
    
    Returns:
        Compiled LangGraph agent
        
    Example:
        from suluvai import create_suluvai_agent, SubAgent
        
        # Define subagents
        data_fetcher = SubAgent(
            name="data_fetcher",
            description="Fetches data from database",
            tools=[get_schema, execute_query],
            instructions="You are a data fetcher..."
        )
        
        # Create main agent
        agent = create_suluvai_agent(
            model=llm,
            tools=[analyze_tool],
            subagents=[data_fetcher],
            instructions="You are an AI assistant..."
        )
        
        # Use it
        result = agent.invoke({
            "messages": [("user", "Show me sales data")],
            "files": {},
            "todos": [],
            "metadata": {}
        })
    """
    
    # Collect all tools
    all_tools = list(tools)
    
    # Add built-in filesystem tools
    if include_filesystem:
        all_tools.extend([write_file, read_file, list_files, delete_file])
    
    # Add TODO tools
    if include_todos:
        all_tools.extend([write_todos, get_todos, mark_todo_done])
    
    # Create subagent tools if provided
    if subagents:
        subagent_tools = _create_subagent_tools(subagents, model)
        all_tools.extend(subagent_tools)
        
        # Add subagent descriptions to instructions
        subagent_desc = "\n\n**Available Sub-Agents:**\n"
        for sa in subagents:
            subagent_desc += f"- **{sa.name}**: {sa.description}\n"
        instructions = instructions + subagent_desc
    
    # Wrap tools to be state-aware
    stateful_tools = create_stateful_tools(all_tools)
    
    # Create the main ReAct agent
    agent = create_react_agent(
        model=model,
        tools=stateful_tools,
        prompt=SystemMessage(content=instructions),
        state_schema=state_schema
    )
    
    return agent


def _create_subagent_tools(subagents: List[SubAgent], default_model: Any) -> List[BaseTool]:
    """
    Convert SubAgent configurations into callable tools for the main agent.
    
    Each subagent becomes a tool that the main agent can invoke.
    """
    from langchain_core.tools import tool
    
    subagent_tools = []
    
    for subagent in subagents:
        # Create the subagent's ReAct agent
        sub_model = subagent.model if subagent.model else default_model
        sub_agent = create_react_agent(
            model=sub_model,
            tools=subagent.tools,
            prompt=SystemMessage(content=subagent.instructions)
        )
        
        # Create a tool that calls this subagent using StructuredTool
        def make_tool(name, agent, desc):
            from langchain_core.tools import StructuredTool
            from pydantic import BaseModel, Field
            
            class SubAgentInput(BaseModel):
                task: str = Field(description="Description of what you want the subagent to do")
            
            def subagent_caller(task: str) -> str:
                """Execute a task using a specialized subagent."""
                # Invoke the subagent
                result = agent.invoke({"messages": [("user", task)]})
                
                # Extract the response
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                return str(last_message)
            
            return StructuredTool.from_function(
                func=subagent_caller,
                name=f"call_{name}",
                description=f"Delegate task to {name}: {desc}",
                args_schema=SubAgentInput
            )
        
        tool_func = make_tool(subagent.name, sub_agent, subagent.description)
        subagent_tools.append(tool_func)
    
    return subagent_tools
