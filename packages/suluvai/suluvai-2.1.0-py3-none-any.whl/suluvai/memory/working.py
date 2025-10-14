"""
Working memory (scratchpad) for agents
"""

from typing import Dict, Any, List


class WorkingMemory:
    """
    Working memory for intermediate calculations and temporary data.
    Like a scratchpad for the agent.
    
    Example:
        memory = WorkingMemory()
        memory.set("step1_result", 42)
        memory.set("intermediate_data", [1, 2, 3])
        
        result = memory.get("step1_result")  # 42
        all_data = memory.get_all()  # All scratchpad data
    """
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any):
        """Set a value in working memory"""
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from working memory"""
        return self.data.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all working memory data"""
        return self.data.copy()
    
    def delete(self, key: str):
        """Delete a value from working memory"""
        if key in self.data:
            del self.data[key]
    
    def clear(self):
        """Clear all working memory"""
        self.data.clear()
    
    def keys(self) -> List[str]:
        """Get all keys in working memory"""
        return list(self.data.keys())
