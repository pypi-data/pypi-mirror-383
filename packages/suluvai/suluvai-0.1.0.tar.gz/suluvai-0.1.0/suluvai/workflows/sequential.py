"""
Sequential workflow implementation
Executes agents one after another: A -> B -> C
"""

from typing import Dict, Any, List, Tuple
from suluvai.workflows.base import BaseWorkflow


class SequentialWorkflow(BaseWorkflow):
    """
    Sequential workflow that executes agents in order.
    Each agent receives the output from the previous agent.
    
    Example:
        workflow = SequentialWorkflow()
        workflow.add_step("fetch", fetcher_agent)
        workflow.add_step("analyze", analyzer_agent)
        workflow.add_step("report", reporter_agent)
        
        result = workflow.execute({"task": "..."})
    """
    
    def __init__(self):
        super().__init__()
        self.steps: List[Tuple[str, Any]] = []
    
    def add_step(self, name: str, agent: Any):
        """Add a step to the workflow"""
        self.steps.append((name, agent))
        return self
    
    def _execute_internal(self, input: Dict[str, Any], config: Dict) -> Any:
        """Execute steps sequentially"""
        current_state = input.copy()
        current_state.setdefault("messages", [])
        current_state.setdefault("files", {})
        current_state.setdefault("todos", [])
        current_state.setdefault("metadata", {})
        
        for step_name, agent in self.steps:
            # Execute agent
            result = agent.invoke(current_state)
            
            # Update state for next step
            current_state["messages"] = result.get("messages", current_state["messages"])
            current_state["files"] = result.get("files", current_state["files"])
            current_state["todos"] = result.get("todos", current_state["todos"])
            current_state["metadata"].update(result.get("metadata", {}))
            
            # Store step output
            current_state["metadata"][f"step_{step_name}_output"] = result
        
        return current_state
