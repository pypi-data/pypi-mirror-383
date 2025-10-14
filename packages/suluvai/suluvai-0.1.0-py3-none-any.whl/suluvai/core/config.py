"""
Configuration for SuluvAI agents
"""

from typing import Literal, Optional, Any
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """
    Configuration for SuluvAI agents.
    
    Storage Options:
        - virtual: In-memory filesystem (isolated per run)
        - local: Persistent filesystem on disk
        - hybrid: Both virtual + local
    
    Memory Options:
        - conversation: Short-term conversation memory
        - semantic: Long-term vector-based memory
        - working: Scratchpad for intermediate results
        - none: No memory (stateless)
    
    Example:
        config = AgentConfig(
            storage_mode="local",
            local_storage_path="./workspace",
            memory_type="conversation",
            enable_streaming=True
        )
    """
    
    # Storage configuration
    storage_mode: Literal["virtual", "local", "hybrid"] = Field(
        default="virtual",
        description="Storage mode for files"
    )
    local_storage_path: str = Field(
        default="./agent_workspace",
        description="Path for local storage"
    )
    
    # Memory configuration
    memory_type: Literal["conversation", "semantic", "working", "none"] = Field(
        default="conversation",
        description="Type of memory to use"
    )
    memory_max_messages: int = Field(
        default=50,
        description="Maximum messages to keep in conversation memory"
    )
    
    # Feature toggles
    enable_streaming: bool = Field(
        default=True,
        description="Enable streaming support"
    )
    include_planning: bool = Field(
        default=True,
        description="Include planning/todo tools"
    )
    include_filesystem: bool = Field(
        default=True,
        description="Include filesystem tools"
    )
    
    # Execution configuration
    max_iterations: int = Field(
        default=25,
        description="Maximum agent iterations"
    )
    timeout: Optional[int] = Field(
        default=None,
        description="Timeout in seconds (None for no timeout)"
    )
    
    # Model configuration
    model: Optional[Any] = Field(
        default=None,
        description="LLM model to use (defaults to provided model)"
    )
    
    class Config:
        arbitrary_types_allowed = True
