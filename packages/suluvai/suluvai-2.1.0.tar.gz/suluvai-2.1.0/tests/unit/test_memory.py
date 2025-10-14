"""
Unit Tests: Memory Systems
Tests conversation and working memory implementations
Developed by SagaraGlobal
"""
import pytest
from suluvai.memory import ConversationMemory, WorkingMemory


class TestConversationMemory:
    """Test ConversationMemory for chat history"""
    
    def test_create(self):
        """Test ConversationMemory creation"""
        memory = ConversationMemory(max_messages=10)
        assert memory is not None
        assert memory.max_messages == 10
        assert len(memory.get_messages()) == 0
    
    def test_add_message(self):
        """Test adding messages"""
        memory = ConversationMemory()
        memory.add_message({"role": "user", "content": "Hello"})
        memory.add_message({"role": "assistant", "content": "Hi there!"})
        
        messages = memory.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hi there!"
    
    def test_max_messages_limit(self):
        """Test that memory respects max_messages limit"""
        memory = ConversationMemory(max_messages=3)
        
        memory.add_message({"role": "user", "content": "msg1"})
        memory.add_message({"role": "assistant", "content": "msg2"})
        memory.add_message({"role": "user", "content": "msg3"})
        memory.add_message({"role": "assistant", "content": "msg4"})  # Should push out msg1
        
        messages = memory.get_messages()
        assert len(messages) == 3
        assert messages[0]["content"] == "msg2"  # msg1 should be gone
        assert messages[-1]["content"] == "msg4"
    
    def test_clear(self):
        """Test clearing all messages"""
        memory = ConversationMemory()
        memory.add_message({"role": "user", "content": "test1"})
        memory.add_message({"role": "assistant", "content": "test2"})
        assert len(memory.get_messages()) == 2
        
        memory.clear()
        assert len(memory.get_messages()) == 0
    
    def test_get_recent(self):
        """Test getting recent messages"""
        memory = ConversationMemory()
        memory.add_message({"role": "user", "content": "msg1"})
        memory.add_message({"role": "assistant", "content": "msg2"})
        memory.add_message({"role": "user", "content": "msg3"})
        memory.add_message({"role": "assistant", "content": "msg4"})
        
        recent = memory.get_messages()
        assert len(recent) == 4
        assert recent[-1]["content"] == "msg4"


class TestWorkingMemory:
    """Test WorkingMemory for scratchpad data"""
    
    def test_create(self):
        """Test WorkingMemory creation"""
        memory = WorkingMemory()
        assert memory is not None
        assert memory.data == {}
    
    def test_set_get(self):
        """Test setting and getting values"""
        memory = WorkingMemory()
        memory.set("key1", "value1")
        memory.set("key2", 42)
        memory.set("key3", [1, 2, 3])
        
        assert memory.get("key1") == "value1"
        assert memory.get("key2") == 42
        assert memory.get("key3") == [1, 2, 3]
    
    def test_get_default(self):
        """Test getting with default value"""
        memory = WorkingMemory()
        value = memory.get("nonexistent", "default_value")
        assert value == "default_value"
    
    def test_get_none(self):
        """Test getting nonexistent key returns None"""
        memory = WorkingMemory()
        value = memory.get("nonexistent")
        assert value is None
    
    def test_delete(self):
        """Test deleting keys"""
        memory = WorkingMemory()
        memory.set("key", "value")
        assert memory.get("key") == "value"
        
        memory.delete("key")
        assert memory.get("key") is None
    
    def test_clear(self):
        """Test clearing all data"""
        memory = WorkingMemory()
        memory.set("key1", "value1")
        memory.set("key2", "value2")
        memory.set("key3", "value3")
        
        memory.clear()
        assert len(memory.keys()) == 0
        assert memory.get("key1") is None
    
    def test_keys(self):
        """Test getting all keys"""
        memory = WorkingMemory()
        memory.set("a", 1)
        memory.set("b", 2)
        memory.set("c", 3)
        
        keys = memory.keys()
        assert len(keys) == 3
        assert "a" in keys
        assert "b" in keys
        assert "c" in keys
    
    def test_complex_data(self):
        """Test storing complex data structures"""
        memory = WorkingMemory()
        
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "number": 42,
            "string": "test"
        }
        
        memory.set("complex", complex_data)
        retrieved = memory.get("complex")
        
        assert retrieved == complex_data
        assert retrieved["list"] == [1, 2, 3]
        assert retrieved["dict"]["nested"] == "value"
        assert retrieved["number"] == 42
    
    def test_overwrite(self):
        """Test overwriting existing keys"""
        memory = WorkingMemory()
        memory.set("key", "original")
        assert memory.get("key") == "original"
        
        memory.set("key", "updated")
        assert memory.get("key") == "updated"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
