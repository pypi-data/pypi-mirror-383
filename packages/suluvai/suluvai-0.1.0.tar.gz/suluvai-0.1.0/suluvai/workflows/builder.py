"""
Workflow builder - fluent API for creating workflows
"""

from typing import Any, Dict, Callable, Optional
from suluvai.workflows.base import BaseWorkflow
from suluvai.workflows.sequential import SequentialWorkflow
from suluvai.workflows.parallel import ParallelWorkflow
from suluvai.workflows.conditional import ConditionalWorkflow


class WorkflowBuilder:
    """
    Fluent builder for creating workflows.
    
    Examples:
        # Sequential workflow
        workflow = WorkflowBuilder() \\
            .sequential() \\
            .add_step("fetch", fetcher) \\
            .add_step("analyze", analyzer) \\
            .build()
        
        # Parallel workflow
        workflow = WorkflowBuilder() \\
            .parallel() \\
            .add_branch("web", web_agent) \\
            .add_branch("db", db_agent) \\
            .add_sync_step("merge", merger) \\
            .build()
        
        # Conditional workflow
        workflow = WorkflowBuilder() \\
            .conditional() \\
            .add_condition("check", lambda s: s['size'] > 100) \\
            .if_true(agent=large_agent) \\
            .if_false(agent=small_agent) \\
            .build()
    """
    
    def __init__(self):
        self._workflow: Optional[BaseWorkflow] = None
        self._workflow_type: Optional[str] = None
    
    def sequential(self):
        """Start building a sequential workflow"""
        self._workflow = SequentialWorkflow()
        self._workflow_type = "sequential"
        return self
    
    def parallel(self):
        """Start building a parallel workflow"""
        self._workflow = ParallelWorkflow()
        self._workflow_type = "parallel"
        return self
    
    def conditional(self):
        """Start building a conditional workflow"""
        self._workflow = ConditionalWorkflow()
        self._workflow_type = "conditional"
        return self
    
    def map_reduce(self):
        """Start building a map-reduce workflow"""
        # Simplified map-reduce using sequential
        self._workflow = SequentialWorkflow()
        self._workflow_type = "map_reduce"
        return self
    
    def custom_graph(self):
        """Start building a custom graph workflow"""
        from suluvai.workflows.custom import CustomGraphWorkflow
        self._workflow = CustomGraphWorkflow()
        self._workflow_type = "custom"
        return self
    
    # Sequential workflow methods
    def add_step(self, name: str, agent: Any):
        """Add a step (for sequential workflows)"""
        if isinstance(self._workflow, SequentialWorkflow):
            self._workflow.add_step(name, agent)
        return self
    
    # Parallel workflow methods
    def add_branch(self, name: str, agent: Any):
        """Add a parallel branch (for parallel workflows)"""
        if isinstance(self._workflow, ParallelWorkflow):
            self._workflow.add_branch(name, agent)
        return self
    
    def add_sync_step(self, name: str, agent: Any):
        """Add sync step after parallel branches"""
        if isinstance(self._workflow, ParallelWorkflow):
            self._workflow.add_sync_step(name, agent)
        return self
    
    # Conditional workflow methods
    def add_condition(self, name: str, condition: Callable[[Dict], bool]):
        """Add condition (for conditional workflows)"""
        if isinstance(self._workflow, ConditionalWorkflow):
            self._workflow.add_condition(name, condition)
        return self
    
    def if_true(self, agent: Any = None, workflow: BaseWorkflow = None):
        """Set true branch"""
        if isinstance(self._workflow, ConditionalWorkflow):
            self._workflow.if_true(agent=agent, workflow=workflow)
        return self
    
    def if_false(self, agent: Any = None, workflow: BaseWorkflow = None):
        """Set false branch"""
        if isinstance(self._workflow, ConditionalWorkflow):
            self._workflow.if_false(agent=agent, workflow=workflow)
        return self
    
    # Map-reduce methods
    def map_step(self, agent: Any, split_fn: Callable):
        """Add map step (splits and processes)"""
        if self._workflow_type == "map_reduce":
            self._workflow.map_agent = agent
            self._workflow.split_fn = split_fn
        return self
    
    def reduce_step(self, agent: Any, combine_fn: Callable):
        """Add reduce step (aggregates results)"""
        if self._workflow_type == "map_reduce":
            self._workflow.reduce_agent = agent
            self._workflow.combine_fn = combine_fn
        return self
    
    # Custom graph methods
    def add_node(self, name: str, agent: Any):
        """Add node to custom graph"""
        if self._workflow_type == "custom":
            self._workflow.add_node(name, agent)
        return self
    
    def add_edge(self, from_node: str, to_node: str):
        """Add edge to custom graph"""
        if self._workflow_type == "custom":
            self._workflow.add_edge(from_node, to_node)
        return self
    
    def set_entry_point(self, node: str):
        """Set entry point for custom graph"""
        if self._workflow_type == "custom":
            self._workflow.set_entry_point(node)
        return self
    
    def set_finish_point(self, node: str):
        """Set finish point for custom graph"""
        if self._workflow_type == "custom":
            self._workflow.set_finish_point(node)
        return self
    
    # Nested workflows
    def add_workflow_step(self, name: str, workflow: BaseWorkflow):
        """Add a nested workflow as a step"""
        if isinstance(self._workflow, SequentialWorkflow):
            # Wrap workflow in a callable that executes it
            def workflow_executor(state):
                result = workflow.execute(state)
                return result.final_output
            
            # Create a mock agent-like object
            class WorkflowAgent:
                def invoke(self, state):
                    return workflow_executor(state)
            
            self._workflow.add_step(name, WorkflowAgent())
        return self
    
    def build(self) -> BaseWorkflow:
        """Build and return the workflow"""
        if self._workflow is None:
            raise ValueError("Must call sequential(), parallel(), or conditional() first")
        return self._workflow
