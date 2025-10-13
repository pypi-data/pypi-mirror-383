"""
Enhanced agent builder with streaming and local storage support
"""

from typing import List, Optional, Any, Sequence, Literal
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from suluvai.state import SuluvAIAgentState
from suluvai.subagent import SubAgent
from suluvai.local_storage import LocalFileStorage
from suluvai import filesystem_tools, todo_tools


class EnhancedAgentConfig(BaseModel):
    """Configuration for enhanced agent"""
    storage_mode: Literal["local", "virtual", "hybrid"] = "local"
    storage_path: str = "./agent_workspace"
    enable_streaming: bool = True
    include_filesystem: bool = True
    include_todos: bool = True
    include_advanced_tools: bool = True


def create_enhanced_agent(
    model: Any,
    tools: Sequence[BaseTool],
    subagents: Optional[List[SubAgent]] = None,
    instructions: str = "You are a helpful assistant.",
    config: Optional[EnhancedAgentConfig] = None,
    state_schema: type = SuluvAIAgentState
):
    """
    Create an enhanced SuluvAI Agent with streaming and local storage.
    
    Args:
        model: LLM model to use (e.g., ChatOpenAI)
        tools: List of tool objects for the main agent
        subagents: Optional list of SubAgent configurations
        instructions: System prompt for the main agent
        config: EnhancedAgentConfig object (defaults to local storage)
        state_schema: Custom state schema (defaults to SuluvAIAgentState)
    
    Returns:
        Tuple of (agent, storage) where agent is the compiled LangGraph agent
        and storage is the LocalFileStorage instance (if using local storage)
        
    Example:
        from suluvai import create_enhanced_agent, EnhancedAgentConfig
        
        config = EnhancedAgentConfig(
            storage_mode="local",
            storage_path="./my_workspace",
            enable_streaming=True
        )
        
        agent, storage = create_enhanced_agent(
            model=llm,
            tools=[my_tool],
            instructions="You are a data analyst...",
            config=config
        )
        
        # Use with streaming
        async for event in stream_agent_events(agent, {"messages": [("user", "Hello")]}):
            if event.event_type == "token":
                print(event.data, end="")
    """
    if config is None:
        config = EnhancedAgentConfig()
    
    # Initialize storage if using local mode
    storage = None
    if config.storage_mode in ["local", "hybrid"]:
        storage = LocalFileStorage(config.storage_path)
    
    # Collect all tools
    all_tools = list(tools)
    
    # Add filesystem tools with storage binding
    if config.include_filesystem:
        fs_tools = _create_filesystem_tools(storage, config.storage_mode)
        all_tools.extend(fs_tools)
    
    # Add TODO tools
    if config.include_todos:
        all_tools.extend([
            todo_tools.write_todos,
            todo_tools.get_todos,
            todo_tools.mark_todo_done
        ])
    
    # Create subagent tools if provided
    if subagents:
        subagent_tools = _create_subagent_tools(subagents, model)
        all_tools.extend(subagent_tools)
        
        # Add subagent descriptions to instructions
        subagent_desc = "\n\n**Available Sub-Agents:**\n"
        for sa in subagents:
            subagent_desc += f"- **{sa.name}**: {sa.description}\n"
        instructions = instructions + subagent_desc
    
    # Create the main ReAct agent
    agent = create_react_agent(
        model=model,
        tools=all_tools,
        prompt=SystemMessage(content=instructions),
        state_schema=state_schema
    )
    
    return agent, storage


def _create_filesystem_tools(
    storage: Optional[LocalFileStorage],
    storage_mode: str
) -> List[BaseTool]:
    """Create filesystem tools bound to local storage"""
    
    # Define input schemas
    class WriteFileInput(BaseModel):
        filepath: str = Field(description="Path to file (e.g., 'data/sales/2024.csv')")
        content: str = Field(description="Content to write to the file")
    
    class ReadFileInput(BaseModel):
        filepath: str = Field(description="Path to file to read")
    
    class ListFilesInput(BaseModel):
        directory: str = Field(default="", description="Directory path (empty for root)")
        recursive: bool = Field(default=True, description="List recursively")
    
    class DeleteFileInput(BaseModel):
        filepath: str = Field(description="Path to file to delete")
    
    class CreateDirectoryInput(BaseModel):
        dirpath: str = Field(description="Path to directory to create")
    
    class SearchFilesInput(BaseModel):
        pattern: str = Field(description="Glob pattern (e.g., '*.csv')")
        directory: str = Field(default="", description="Directory to search in")
    
    class GetFileTreeInput(BaseModel):
        directory: str = Field(default="", description="Starting directory")
        max_depth: int = Field(default=3, description="Maximum depth")
    
    class CopyMoveFileInput(BaseModel):
        src_path: str = Field(description="Source file path")
        dst_path: str = Field(description="Destination file path")
    
    # Create tools based on storage mode
    if storage_mode == "local" and storage:
        # Local storage mode - use actual file operations
        tools = [
            StructuredTool.from_function(
                func=lambda filepath, content: _write_file_local(storage, filepath, content),
                name="write_file",
                description="Write content to a file (supports nested directories)",
                args_schema=WriteFileInput
            ),
            StructuredTool.from_function(
                func=lambda filepath: _read_file_local(storage, filepath),
                name="read_file",
                description="Read content from a file",
                args_schema=ReadFileInput
            ),
            StructuredTool.from_function(
                func=lambda directory="", recursive=True: _list_files_local(storage, directory, recursive),
                name="list_files",
                description="List files in a directory (supports multi-level folders)",
                args_schema=ListFilesInput
            ),
            StructuredTool.from_function(
                func=lambda filepath: _delete_file_local(storage, filepath),
                name="delete_file",
                description="Delete a file",
                args_schema=DeleteFileInput
            ),
            StructuredTool.from_function(
                func=lambda dirpath: _create_directory_local(storage, dirpath),
                name="create_directory",
                description="Create a directory (including parent directories)",
                args_schema=CreateDirectoryInput
            ),
            StructuredTool.from_function(
                func=lambda directory="", recursive=True: _list_directories_local(storage, directory, recursive),
                name="list_directories",
                description="List all directories",
                args_schema=ListFilesInput
            ),
            StructuredTool.from_function(
                func=lambda pattern, directory="": _search_files_local(storage, pattern, directory),
                name="search_files",
                description="Search for files matching a pattern",
                args_schema=SearchFilesInput
            ),
            StructuredTool.from_function(
                func=lambda directory="", max_depth=3: _get_file_tree_local(storage, directory, max_depth),
                name="get_file_tree",
                description="Get a tree view of the directory structure",
                args_schema=GetFileTreeInput
            ),
            StructuredTool.from_function(
                func=lambda src_path, dst_path: _copy_file_local(storage, src_path, dst_path),
                name="copy_file",
                description="Copy a file to a new location",
                args_schema=CopyMoveFileInput
            ),
            StructuredTool.from_function(
                func=lambda src_path, dst_path: _move_file_local(storage, src_path, dst_path),
                name="move_file",
                description="Move a file to a new location",
                args_schema=CopyMoveFileInput
            )
        ]
    else:
        # Virtual mode - use the base tools
        tools = [
            filesystem_tools.write_file,
            filesystem_tools.read_file,
            filesystem_tools.list_files,
            filesystem_tools.delete_file,
            filesystem_tools.create_directory,
            filesystem_tools.list_directories,
            filesystem_tools.search_files,
            filesystem_tools.get_file_tree,
            filesystem_tools.copy_file,
            filesystem_tools.move_file
        ]
    
    return tools


# Local storage implementation functions
def _write_file_local(storage: LocalFileStorage, filepath: str, content: str) -> str:
    """Write file to local storage"""
    try:
        metadata = storage.write_file(filepath, content)
        return f"✅ File '{filepath}' written successfully ({metadata.size} bytes)"
    except Exception as e:
        return f"❌ Error writing file: {str(e)}"


def _read_file_local(storage: LocalFileStorage, filepath: str) -> str:
    """Read file from local storage"""
    try:
        content = storage.read_file(filepath)
        return content
    except FileNotFoundError:
        return f"❌ File not found: {filepath}"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


def _list_files_local(storage: LocalFileStorage, directory: str = "", recursive: bool = True) -> str:
    """List files in local storage"""
    try:
        files = storage.list_files(directory, recursive)
        if not files:
            return f"No files found in '{directory or 'root'}'"
        
        result = f"📁 Files in '{directory or 'root'}' ({len(files)} files):\n"
        for file in files:
            metadata = storage.get_metadata(file)
            size_str = f"{metadata.size} bytes" if metadata else "unknown size"
            result += f"  • {file} ({size_str})\n"
        return result.strip()
    except Exception as e:
        return f"❌ Error listing files: {str(e)}"


def _delete_file_local(storage: LocalFileStorage, filepath: str) -> str:
    """Delete file from local storage"""
    try:
        success = storage.delete_file(filepath)
        if success:
            return f"✅ File '{filepath}' deleted successfully"
        else:
            return f"❌ File not found: {filepath}"
    except Exception as e:
        return f"❌ Error deleting file: {str(e)}"


def _create_directory_local(storage: LocalFileStorage, dirpath: str) -> str:
    """Create directory in local storage"""
    try:
        storage.create_directory(dirpath)
        return f"✅ Directory '{dirpath}' created successfully"
    except Exception as e:
        return f"❌ Error creating directory: {str(e)}"


def _list_directories_local(storage: LocalFileStorage, directory: str = "", recursive: bool = True) -> str:
    """List directories in local storage"""
    try:
        directories = storage.list_directories(directory, recursive)
        if not directories:
            return f"No directories found in '{directory or 'root'}'"
        
        result = f"📂 Directories in '{directory or 'root'}' ({len(directories)} dirs):\n"
        for dir in directories:
            result += f"  • {dir}/\n"
        return result.strip()
    except Exception as e:
        return f"❌ Error listing directories: {str(e)}"


def _search_files_local(storage: LocalFileStorage, pattern: str, directory: str = "") -> str:
    """Search files in local storage"""
    try:
        files = storage.search_files(pattern, directory)
        if not files:
            return f"No files matching '{pattern}' found"
        
        result = f"🔍 Files matching '{pattern}' ({len(files)} files):\n"
        for file in files:
            result += f"  • {file}\n"
        return result.strip()
    except Exception as e:
        return f"❌ Error searching files: {str(e)}"


def _get_file_tree_local(storage: LocalFileStorage, directory: str = "", max_depth: int = 3) -> str:
    """Get file tree from local storage"""
    try:
        tree = storage.get_tree(directory, max_depth)
        
        def format_tree(tree_dict: dict, indent: int = 0) -> str:
            result = ""
            for key, value in sorted(tree_dict.items()):
                if key == "_files":
                    for file in sorted(value):
                        result += "  " * indent + f"📄 {file}\n"
                else:
                    result += "  " * indent + f"📁 {key}/\n"
                    if isinstance(value, dict):
                        result += format_tree(value, indent + 1)
            return result
        
        formatted = format_tree(tree)
        return f"🌳 Directory tree:\n{formatted}" if formatted else "Empty directory"
    except Exception as e:
        return f"❌ Error getting file tree: {str(e)}"


def _copy_file_local(storage: LocalFileStorage, src_path: str, dst_path: str) -> str:
    """Copy file in local storage"""
    try:
        storage.copy_file(src_path, dst_path)
        return f"✅ File copied from '{src_path}' to '{dst_path}'"
    except Exception as e:
        return f"❌ Error copying file: {str(e)}"


def _move_file_local(storage: LocalFileStorage, src_path: str, dst_path: str) -> str:
    """Move file in local storage"""
    try:
        storage.move_file(src_path, dst_path)
        return f"✅ File moved from '{src_path}' to '{dst_path}'"
    except Exception as e:
        return f"❌ Error moving file: {str(e)}"


def _create_subagent_tools(subagents: List[SubAgent], default_model: Any) -> List[BaseTool]:
    """Create subagent tools"""
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field
    
    subagent_tools = []
    
    for subagent in subagents:
        sub_model = subagent.model if subagent.model else default_model
        sub_agent = create_react_agent(
            model=sub_model,
            tools=subagent.tools,
            prompt=SystemMessage(content=subagent.instructions)
        )
        
        def make_tool(name, agent, desc):
            class SubAgentInput(BaseModel):
                task: str = Field(description="Task description for the subagent")
            
            def subagent_caller(task: str) -> str:
                result = agent.invoke({"messages": [("user", task)]})
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
