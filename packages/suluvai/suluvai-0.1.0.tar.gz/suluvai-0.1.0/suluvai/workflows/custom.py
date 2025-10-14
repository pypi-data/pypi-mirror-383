"""
Custom graph workflow implementation
Allows defining arbitrary DAG structures
"""

from typing import Dict, Any, List, Set
from suluvai.workflows.base import BaseWorkflow


class CustomGraphWorkflow(BaseWorkflow):
    """
    Custom graph workflow for arbitrary DAG structures.
    
    Example:
        workflow = CustomGraphWorkflow()
        workflow.add_node("fetch", fetcher)
        workflow.add_node("clean", cleaner)
        workflow.add_node("analyze", analyzer)
        workflow.add_edge("fetch", "clean")
        workflow.add_edge("clean", "analyze")
        workflow.set_entry_point("fetch")
        workflow.set_finish_point("analyze")
    """
    
    def __init__(self):
        super().__init__()
        self.nodes: Dict[str, Any] = {}
        self.edges: List[tuple] = []
        self.entry_point: str = ""
        self.finish_point: str = ""
    
    def add_node(self, name: str, agent: Any):
        """Add a node to the graph"""
        self.nodes[name] = agent
        return self
    
    def add_edge(self, from_node: str, to_node: str):
        """Add an edge between nodes"""
        self.edges.append((from_node, to_node))
        return self
    
    def set_entry_point(self, node: str):
        """Set the entry point"""
        self.entry_point = node
        return self
    
    def set_finish_point(self, node: str):
        """Set the finish point"""
        self.finish_point = node
        return self
    
    def _execute_internal(self, input: Dict[str, Any], config: Dict) -> Any:
        """Execute custom graph using topological sort"""
        current_state = input.copy()
        current_state.setdefault("messages", [])
        current_state.setdefault("files", {})
        current_state.setdefault("todos", [])
        current_state.setdefault("metadata", {})
        
        # Simple execution: follow edges from entry to finish
        # In production, you'd use proper topological sort
        visited: Set[str] = set()
        
        def execute_node(node_name: str, state: Dict) -> Dict:
            if node_name in visited:
                return state
            visited.add(node_name)
            
            # Execute current node
            agent = self.nodes[node_name]
            result = agent.invoke(state)
            
            # Update state
            state["messages"] = result.get("messages", state["messages"])
            state["files"] = result.get("files", state["files"])
            state["todos"] = result.get("todos", state["todos"])
            state["metadata"].update(result.get("metadata", {}))
            state["metadata"][f"node_{node_name}_output"] = result
            
            # If this is finish point, return
            if node_name == self.finish_point:
                return state
            
            # Execute next nodes
            for from_node, to_node in self.edges:
                if from_node == node_name:
                    state = execute_node(to_node, state)
            
            return state
        
        return execute_node(self.entry_point, current_state)
