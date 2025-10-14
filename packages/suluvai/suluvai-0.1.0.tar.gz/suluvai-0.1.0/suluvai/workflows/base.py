"""
Base workflow classes for SuluvAI
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time


@dataclass
class WorkflowResult:
    """Result from workflow execution"""
    final_output: Any
    steps_executed: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    total_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_step_output(self, step_name: str) -> Any:
        """Get output from a specific step"""
        return self.metadata.get(f"step_{step_name}_output")


class BaseWorkflow:
    """
    Base class for all workflows.
    
    Workflows orchestrate multiple agents in various patterns:
    - Sequential: A -> B -> C
    - Parallel: A || B || C -> Merge
    - Conditional: If X then A else B
    - Map-Reduce: Split -> Process[] -> Aggregate
    - Custom: Arbitrary DAG
    """
    
    def __init__(self):
        self.steps = []
        self.config = {}
    
    def execute(self, input: Dict[str, Any], config: Optional[Dict] = None) -> WorkflowResult:
        """
        Execute the workflow.
        
        Args:
            input: Input data for the workflow
            config: Optional configuration (timeout, streaming, etc.)
        
        Returns:
            WorkflowResult with outputs and metadata
        """
        start_time = time.time()
        steps_executed = []
        
        try:
            result = self._execute_internal(input, config or {})
            execution_time = time.time() - start_time
            
            return WorkflowResult(
                final_output=result,
                steps_executed=steps_executed,
                execution_time=execution_time,
                metadata={"success": True}
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return WorkflowResult(
                final_output=None,
                steps_executed=steps_executed,
                execution_time=execution_time,
                metadata={"success": False, "error": str(e)}
            )
    
    def _execute_internal(self, input: Dict[str, Any], config: Dict) -> Any:
        """Internal execution logic (implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement _execute_internal")
    
    def stream(self, input: Dict[str, Any], config: Optional[Dict] = None):
        """Stream workflow execution (for real-time updates)"""
        # Default implementation - subclasses can override
        result = self.execute(input, config)
        yield result
