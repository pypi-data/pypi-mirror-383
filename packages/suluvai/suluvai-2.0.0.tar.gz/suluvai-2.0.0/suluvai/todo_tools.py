"""
TODO list tools for Zita Agents
Helps agents plan and track tasks
"""

from langchain_core.tools import tool
from typing import List


@tool
def write_todos(tasks: List[str]) -> str:
    """
    Create or update the TODO list for the current task.
    Use this to plan your approach before executing.
    
    Args:
        tasks: List of tasks to complete (in order)
    
    Returns:
        Confirmation message with the TODO list
        
    Example:
        write_todos([
            "1. Fetch sales data from database",
            "2. Aggregate by region",
            "3. Analyze trends",
            "4. Present findings"
        ])
    
    Best Practice:
    - Break complex tasks into clear steps
    - Mark completed steps when revisiting
    - Update the list as you learn more
    """
    # This will be bound to state in the agent
    tasks_str = "\n".join(f"{'✅' if '✓' in task or 'DONE' in task.upper() else '☐'} {task}" 
                          for task in tasks)
    return f"TODO List Created:\n{tasks_str}"


@tool
def get_todos() -> str:
    """
    Retrieve the current TODO list.
    
    Returns:
        Current TODO list with completion status
        
    Example:
        todos = get_todos()
    """
    # This will be bound to state in the agent
    return "Current TODO list"


@tool
def mark_todo_done(task_number: int) -> str:
    """
    Mark a specific TODO item as completed.
    
    Args:
        task_number: The number of the task to mark as done (1-indexed)
    
    Returns:
        Confirmation message
    """
    # This will be bound to state in the agent
    return f"Task #{task_number} marked as done"
