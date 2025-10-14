"""
Parallel workflow implementation
Executes multiple agents concurrently
"""

from typing import Dict, Any, List, Tuple
import asyncio
from suluvai.workflows.base import BaseWorkflow


class ParallelWorkflow(BaseWorkflow):
    """
    Parallel workflow that executes agents concurrently.
    
    Example:
        workflow = ParallelWorkflow()
        workflow.add_branch("web", web_agent)
        workflow.add_branch("db", db_agent)
        workflow.add_sync_step("merge", merger_agent)
        
        result = workflow.execute({"task": "..."})
    """
    
    def __init__(self):
        super().__init__()
        self.branches: List[Tuple[str, Any]] = []
        self.sync_step: Tuple[str, Any] = None
    
    def add_branch(self, name: str, agent: Any):
        """Add a parallel branch"""
        self.branches.append((name, agent))
        return self
    
    def add_sync_step(self, name: str, agent: Any):
        """Add synchronization step after parallel execution"""
        self.sync_step = (name, agent)
        return self
    
    def _execute_internal(self, input: Dict[str, Any], config: Dict) -> Any:
        """Execute branches in parallel"""
        # For synchronous execution, we run sequentially (async version would use asyncio)
        # In production, you'd use asyncio.gather() for true parallelism
        
        base_state = input.copy()
        base_state.setdefault("messages", [])
        base_state.setdefault("files", {})
        base_state.setdefault("todos", [])
        base_state.setdefault("metadata", {})
        
        # Execute all branches (simulated parallel - would use asyncio in production)
        branch_results = {}
        for branch_name, agent in self.branches:
            branch_state = base_state.copy()
            result = agent.invoke(branch_state)
            branch_results[branch_name] = result
        
        # Merge results
        merged_state = base_state.copy()
        all_files = {}
        all_messages = base_state.get("messages", [])
        
        for branch_name, result in branch_results.items():
            all_files.update(result.get("files", {}))
            # Add branch-specific messages
            branch_messages = result.get("messages", [])
            if len(branch_messages) > len(all_messages):
                all_messages.extend(branch_messages[len(all_messages):])
            merged_state["metadata"][f"branch_{branch_name}_output"] = result
        
        merged_state["files"] = all_files
        merged_state["messages"] = all_messages
        
        # Execute sync step if provided
        if self.sync_step:
            sync_name, sync_agent = self.sync_step
            final_result = sync_agent.invoke(merged_state)
            return final_result
        
        return merged_state
