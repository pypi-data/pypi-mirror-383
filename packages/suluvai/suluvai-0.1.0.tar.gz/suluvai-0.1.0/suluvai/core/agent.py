"""
Core agent creation module for SuluvAI
Main API: create_agent() - DeepAgents style with enhancements
"""

from typing import List, Optional, Any, Sequence, Dict, Union
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END

from suluvai.core.config import AgentConfig
from suluvai.core.state import SuluvAIState
from suluvai.core.subagent import SubAgent
from suluvai.storage.virtual import VirtualStorage
from suluvai.storage.local import LocalStorage
from suluvai.storage.hybrid import HybridStorage
from suluvai.tools import filesystem, planning


def create_agent(
    tools: Sequence[BaseTool],
    instructions: str,
    subagents: Optional[List[Union[SubAgent, Dict]]] = None,
    config: Optional[AgentConfig] = None,
    model: Optional[Any] = None,
    state_schema: type = SuluvAIState
):
    """
    Create a SuluvAI agent (DeepAgents compatible + enhanced).
    
    Args:
        tools: List of tool objects the agent can use
        instructions: System prompt (full control to user)
        subagents: Optional list of SubAgent configs or dicts
        config: Optional AgentConfig for advanced features
        model: Optional LLM model (required if not in config)
        state_schema: Custom state schema (defaults to SuluvAIState)
    
    Returns:
        Compiled LangGraph agent
        
    Example:
        # Simple agent
        agent = create_agent(
            tools=[search_tool],
            instructions="You are a researcher...",
            model=ChatOpenAI(model="gpt-4")
        )
        
        # With subagents
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
        
        # With config
        agent = create_agent(
            tools=[search_tool],
            instructions="You are an analyst...",
            config=AgentConfig(
                storage_mode="local",
                memory_type="conversation",
                enable_streaming=True
            ),
            model=ChatOpenAI(model="gpt-4")
        )
    """
    if config is None:
        config = AgentConfig()
    
    # Use model from config or provided model
    if model is None and config.model is None:
        raise ValueError("Must provide model either as argument or in config")
    agent_model = config.model if config.model is not None else model
    
    # Initialize storage based on mode
    storage = _initialize_storage(config)
    
    # Collect all tools
    all_tools = list(tools)
    
    # Add built-in filesystem tools
    if config.include_filesystem:
        fs_tools = _create_filesystem_tools(storage, config.storage_mode)
        all_tools.extend(fs_tools)
    
    # Add planning/todo tools
    if config.include_planning:
        all_tools.extend([
            planning.write_todos,
            planning.get_todos,
            planning.mark_todo_done
        ])
    
    # Create subagent tools if provided
    if subagents:
        subagent_tools = _create_subagent_tools(subagents, agent_model)
        all_tools.extend(subagent_tools)
        
        # Add subagent descriptions to instructions
        subagent_desc = "\n\n**Available Sub-Agents:**\n"
        for sa in subagents:
            sa_dict = sa if isinstance(sa, dict) else {
                "name": sa.name,
                "description": sa.description
            }
            subagent_desc += f"- **{sa_dict['name']}**: {sa_dict['description']}\n"
        instructions = instructions + subagent_desc
    
    # Create the ReAct agent
    agent = create_react_agent(
        model=agent_model,
        tools=all_tools,
        prompt=SystemMessage(content=instructions),
        state_schema=state_schema
    )
    
    # Store config and storage as attributes for later access
    agent.suluvai_config = config
    agent.suluvai_storage = storage
    
    return agent


def _initialize_storage(config: AgentConfig):
    """Initialize storage backend based on config"""
    if config.storage_mode == "local":
        from suluvai.storage.local_storage import LocalFileStorage
        return LocalFileStorage(config.local_storage_path)
    elif config.storage_mode == "hybrid":
        from suluvai.storage.local_storage import LocalFileStorage
        return LocalFileStorage(config.local_storage_path)  # Will add virtual layer
    else:  # virtual
        return None  # Virtual storage is handled in state


def _create_filesystem_tools(storage, storage_mode: str) -> List[BaseTool]:
    """Create filesystem tools based on storage mode"""
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field
    
    # Define schemas
    class WriteFileInput(BaseModel):
        filepath: str = Field(description="Path to file (e.g., 'data/sales.csv')")
        content: str = Field(description="Content to write")
    
    class ReadFileInput(BaseModel):
        filepath: str = Field(description="Path to file to read")
    
    class ListFilesInput(BaseModel):
        directory: str = Field(default="", description="Directory path")
        recursive: bool = Field(default=True, description="List recursively")
    
    class DeleteFileInput(BaseModel):
        filepath: str = Field(description="Path to file to delete")
    
    class SearchFilesInput(BaseModel):
        pattern: str = Field(description="Glob pattern (e.g., '*.csv')")
        directory: str = Field(default="", description="Directory to search")
    
    class GetTreeInput(BaseModel):
        directory: str = Field(default="", description="Starting directory")
        max_depth: int = Field(default=3, description="Maximum depth")
    
    class CopyMoveInput(BaseModel):
        src_path: str = Field(description="Source file path")
        dst_path: str = Field(description="Destination file path")
    
    if storage_mode == "local" and storage:
        # Local storage - actual file operations
        tools = [
            StructuredTool.from_function(
                func=lambda filepath, content: storage.write_file(filepath, content) and f"✅ File '{filepath}' written",
                name="write_file",
                description="Write content to a file (supports nested directories)",
                args_schema=WriteFileInput
            ),
            StructuredTool.from_function(
                func=lambda filepath: storage.read_file(filepath),
                name="read_file",
                description="Read content from a file",
                args_schema=ReadFileInput
            ),
            StructuredTool.from_function(
                func=lambda directory="", recursive=True: "\n".join(storage.list_files(directory, recursive)),
                name="list_files",
                description="List files in a directory",
                args_schema=ListFilesInput
            ),
            StructuredTool.from_function(
                func=lambda filepath: storage.delete_file(filepath) and f"✅ Deleted '{filepath}'",
                name="delete_file",
                description="Delete a file",
                args_schema=DeleteFileInput
            ),
            StructuredTool.from_function(
                func=lambda pattern, directory="": "\n".join(storage.search_files(pattern, directory)),
                name="search_files",
                description="Search for files matching a pattern",
                args_schema=SearchFilesInput
            ),
            StructuredTool.from_function(
                func=lambda directory="", max_depth=3: _format_tree(storage.get_tree(directory, max_depth)),
                name="get_file_tree",
                description="Get directory tree structure",
                args_schema=GetTreeInput
            ),
            StructuredTool.from_function(
                func=lambda src_path, dst_path: storage.copy_file(src_path, dst_path) and f"✅ Copied",
                name="copy_file",
                description="Copy a file",
                args_schema=CopyMoveInput
            ),
            StructuredTool.from_function(
                func=lambda src_path, dst_path: storage.move_file(src_path, dst_path) and f"✅ Moved",
                name="move_file",
                description="Move a file",
                args_schema=CopyMoveInput
            )
        ]
    else:
        # Virtual mode - use base tools (state-based)
        tools = [
            filesystem.write_file,
            filesystem.read_file,
            filesystem.list_files,
            filesystem.delete_file,
            filesystem.search_files,
            filesystem.get_file_tree,
            filesystem.copy_file,
            filesystem.move_file
        ]
    
    return tools


def _format_tree(tree_dict: dict, indent: int = 0) -> str:
    """Format tree dictionary as string"""
    result = ""
    for key, value in sorted(tree_dict.items()):
        if key == "_files":
            for file in sorted(value):
                result += "  " * indent + f"📄 {file}\n"
        else:
            result += "  " * indent + f"📁 {key}/\n"
            if isinstance(value, dict):
                result += _format_tree(value, indent + 1)
    return result.strip()


def _create_subagent_tools(subagents: List[Union[SubAgent, Dict]], default_model: Any) -> List[BaseTool]:
    """Create subagent tools (DeepAgents compatible)"""
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field
    
    subagent_tools = []
    
    for subagent in subagents:
        # Handle both SubAgent objects and dict format (deepagents style)
        if isinstance(subagent, dict):
            sa_name = subagent["name"]
            sa_description = subagent["description"]
            sa_prompt = subagent["prompt"]
            sa_tools = subagent.get("tools", [])
            sa_model = subagent.get("model", default_model)
            sa_graph = subagent.get("graph")  # Custom graph support
        else:
            sa_name = subagent.name
            sa_description = subagent.description
            sa_prompt = subagent.instructions
            sa_tools = subagent.tools
            sa_model = subagent.model if subagent.model else default_model
            sa_graph = None
        
        # Use custom graph if provided, otherwise create ReAct agent
        if sa_graph:
            sub_agent = sa_graph
        else:
            # Create subagent with proper configuration
            sub_agent = create_react_agent(
                model=sa_model,
                tools=sa_tools if sa_tools else [],
                prompt=SystemMessage(content=sa_prompt)
            )
        
        # Create tool for this subagent
        def make_tool(name, agent, desc):
            class SubAgentInput(BaseModel):
                task: str = Field(description="Task description for the subagent")
            
            def subagent_caller(task: str) -> str:
                try:
                    # Invoke subagent with recursion limit
                    result = agent.invoke(
                        {"messages": [("user", task)]},
                        {"recursion_limit": 10}
                    )
                    last_message = result["messages"][-1]
                    if hasattr(last_message, 'content'):
                        return last_message.content
                    return str(last_message)
                except Exception as e:
                    return f"Subagent error: {str(e)}"
            
            return StructuredTool.from_function(
                func=subagent_caller,
                name=f"call_{name.replace('-', '_')}",
                description=f"Delegate task to {name}: {desc}",
                args_schema=SubAgentInput
            )
        
        tool_func = make_tool(sa_name, sub_agent, sa_description)
        subagent_tools.append(tool_func)
    
    return subagent_tools
