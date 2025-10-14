"""
Conditional workflow implementation
Routes execution based on conditions
"""

from typing import Dict, Any, Callable, Optional
from suluvai.workflows.base import BaseWorkflow


class ConditionalWorkflow(BaseWorkflow):
    """
    Conditional workflow that branches based on conditions.
    
    Example:
        workflow = ConditionalWorkflow()
        workflow.add_condition(
            "check_size",
            lambda state: len(state['data']) > 1000
        )
        workflow.if_true(large_data_agent)
        workflow.if_false(small_data_agent)
        
        result = workflow.execute({"data": [...]})
    """
    
    def __init__(self):
        super().__init__()
        self.condition_name: str = ""
        self.condition_fn: Optional[Callable] = None
        self.true_agent: Optional[Any] = None
        self.false_agent: Optional[Any] = None
        self.true_workflow: Optional[BaseWorkflow] = None
        self.false_workflow: Optional[BaseWorkflow] = None
    
    def add_condition(self, name: str, condition: Callable[[Dict], bool]):
        """Add condition function"""
        self.condition_name = name
        self.condition_fn = condition
        return self
    
    def if_true(self, agent: Any = None, workflow: BaseWorkflow = None):
        """Set agent/workflow for true branch"""
        self.true_agent = agent
        self.true_workflow = workflow
        return self
    
    def if_false(self, agent: Any = None, workflow: BaseWorkflow = None):
        """Set agent/workflow for false branch"""
        self.false_agent = agent
        self.false_workflow = workflow
        return self
    
    def _execute_internal(self, input: Dict[str, Any], config: Dict) -> Any:
        """Execute conditional logic"""
        base_state = input.copy()
        base_state.setdefault("messages", [])
        base_state.setdefault("files", {})
        base_state.setdefault("todos", [])
        base_state.setdefault("metadata", {})
        
        # Evaluate condition
        condition_result = self.condition_fn(base_state)
        
        # Execute appropriate branch
        if condition_result:
            if self.true_workflow:
                return self.true_workflow.execute(base_state, config).final_output
            elif self.true_agent:
                return self.true_agent.invoke(base_state)
        else:
            if self.false_workflow:
                return self.false_workflow.execute(base_state, config).final_output
            elif self.false_agent:
                return self.false_agent.invoke(base_state)
        
        return base_state
