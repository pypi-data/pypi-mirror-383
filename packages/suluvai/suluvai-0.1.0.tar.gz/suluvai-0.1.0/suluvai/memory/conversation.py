"""
Conversation memory for agents
"""

from typing import List, Dict, Any
from collections import deque


class ConversationMemory:
    """
    Conversation memory that keeps track of recent messages.
    
    Example:
        memory = ConversationMemory(max_messages=50)
        memory.add_message({"role": "user", "content": "Hello"})
        memory.add_message({"role": "assistant", "content": "Hi!"})
        
        messages = memory.get_messages()  # Get all messages
        recent = memory.get_recent(10)  # Get last 10
    """
    
    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self.messages = deque(maxlen=max_messages)
    
    def add_message(self, message: Dict[str, Any]):
        """Add a message to memory"""
        self.messages.append(message)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages"""
        return list(self.messages)
    
    def get_recent(self, n: int) -> List[Dict[str, Any]]:
        """Get last n messages"""
        return list(self.messages)[-n:]
    
    def clear(self):
        """Clear all messages"""
        self.messages.clear()
    
    def get_summary(self) -> str:
        """Get a summary of the conversation"""
        return f"{len(self.messages)} messages in memory"
