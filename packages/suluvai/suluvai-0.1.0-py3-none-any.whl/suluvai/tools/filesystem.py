"""
Built-in filesystem tools for Zita Agents
Supports both virtual (in-state) and local (on-disk) filesystems
"""

from langchain_core.tools import tool
from typing import Optional, List


@tool
def write_file(filepath: str, content: str) -> str:
    """
    Write content to a file (supports nested directories).
    
    Args:
        filepath: Path to the file (e.g., "data/sales/2024.csv", "notes.txt")
        content: Content to write to the file
    
    Returns:
        Success message with filepath
        
    Example:
        write_file("reports/q1/summary.txt", "Q1 Summary: Revenue up 20%")
        write_file("data.csv", "product,revenue\\nA,1000\\nB,2000")
    
    Note: Creates parent directories automatically if they don't exist.
    """
    # This will be bound to state/storage in the agent
    return f"File '{filepath}' written successfully"


@tool
def read_file(filepath: str) -> str:
    """
    Read content from a file.
    
    Args:
        filepath: Path to the file to read (e.g., "data/sales.csv")
    
    Returns:
        File content as string
        
    Example:
        content = read_file("reports/q1/summary.txt")
    """
    # This will be bound to state/storage in the agent
    return f"Content of '{filepath}'"


@tool
def list_files(directory: str = "", recursive: bool = True) -> str:
    """
    List files in a directory (supports multi-level folders).
    
    Args:
        directory: Directory path (empty for root, e.g., "data/sales")
        recursive: Whether to list files in subdirectories
    
    Returns:
        Formatted string with list of files
        
    Example:
        # List all files recursively
        files = list_files()
        
        # List only files in 'data' directory
        files = list_files("data", recursive=False)
    """
    # This will be bound to state/storage in the agent
    return "Files in filesystem"


@tool
def delete_file(filepath: str) -> str:
    """
    Delete a file.
    
    Args:
        filepath: Path to the file to delete
    
    Returns:
        Success message
        
    Example:
        delete_file("temp/cache.txt")
    """
    # This will be bound to state/storage in the agent
    return f"File '{filepath}' deleted successfully"


@tool
def create_directory(dirpath: str) -> str:
    """
    Create a directory (including parent directories).
    
    Args:
        dirpath: Path to the directory to create (e.g., "data/reports/2024")
    
    Returns:
        Success message
        
    Example:
        create_directory("data/sales/2024/q1")
    """
    return f"Directory '{dirpath}' created successfully"


@tool
def list_directories(directory: str = "", recursive: bool = True) -> str:
    """
    List all directories.
    
    Args:
        directory: Starting directory (empty for root)
        recursive: Whether to list recursively
    
    Returns:
        Formatted list of directories
        
    Example:
        dirs = list_directories("data")
    """
    return "Directories in filesystem"


@tool
def search_files(pattern: str, directory: str = "") -> str:
    """
    Search for files matching a pattern.
    
    Args:
        pattern: Glob pattern (e.g., "*.csv", "**/*.json", "report_*.txt")
        directory: Directory to search in (empty for root)
    
    Returns:
        List of matching file paths
        
    Example:
        # Find all CSV files
        csv_files = search_files("*.csv")
        
        # Find all JSON files in data directory
        json_files = search_files("**/*.json", "data")
    """
    return f"Files matching '{pattern}'"


@tool
def get_file_tree(directory: str = "", max_depth: int = 3) -> str:
    """
    Get a tree view of the directory structure.
    
    Args:
        directory: Starting directory (empty for root)
        max_depth: Maximum depth to show (default: 3)
    
    Returns:
        Tree structure as formatted string
        
    Example:
        tree = get_file_tree()
        # Returns formatted tree like:
        # data/
        #   sales/
        #     2024.csv
        #     2023.csv
        #   reports/
        #     summary.txt
    """
    return "Directory tree structure"


@tool
def copy_file(src_path: str, dst_path: str) -> str:
    """
    Copy a file to a new location.
    
    Args:
        src_path: Source file path
        dst_path: Destination file path
    
    Returns:
        Success message
        
    Example:
        copy_file("data/template.csv", "data/2024/sales.csv")
    """
    return f"File copied from '{src_path}' to '{dst_path}'"


@tool
def move_file(src_path: str, dst_path: str) -> str:
    """
    Move a file to a new location.
    
    Args:
        src_path: Source file path
        dst_path: Destination file path
    
    Returns:
        Success message
        
    Example:
        move_file("temp/data.csv", "archive/data.csv")
    """
    return f"File moved from '{src_path}' to '{dst_path}'"
