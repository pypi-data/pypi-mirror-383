"""
Integration Tests: Workflows
Tests workflow orchestration (sequential, parallel, conditional)
Developed by SagaraGlobal
"""
import pytest
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import create_agent, WorkflowBuilder, BaseWorkflow

load_dotenv()

skip_if_no_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


@tool
def process_data(data: str) -> str:
    """Process some data"""
    return f"Processed: {data}"


class TestWorkflowBuilder:
    """Test WorkflowBuilder functionality"""
    
    def test_builder_create(self):
        """Test WorkflowBuilder creation"""
        builder = WorkflowBuilder()
        assert builder is not None
    
    def test_builder_chaining(self):
        """Test that builder methods return self for chaining"""
        builder = WorkflowBuilder()
        result = builder.sequential()
        assert result is builder


class TestSequentialWorkflow:
    """Test Sequential Workflow"""
    
    @skip_if_no_key
    def test_build_sequential(self):
        """Test building a sequential workflow"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent1 = create_agent(
            tools=[process_data],
            instructions="You are step 1. Say 'Step 1 complete'.",
            model=llm
        )
        agent2 = create_agent(
            tools=[process_data],
            instructions="You are step 2. Say 'Step 2 complete'.",
            model=llm
        )
        
        workflow = WorkflowBuilder() \
            .sequential() \
            .add_step("step1", agent1) \
            .add_step("step2", agent2) \
            .build()
        
        assert workflow is not None
        assert isinstance(workflow, BaseWorkflow)
    
    @skip_if_no_key
    def test_execute_sequential(self):
        """Test executing a sequential workflow"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent1 = create_agent(
            tools=[],
            instructions="Say 'First step done' and nothing else.",
            model=llm
        )
        agent2 = create_agent(
            tools=[],
            instructions="Say 'Second step done' and nothing else.",
            model=llm
        )
        
        workflow = WorkflowBuilder() \
            .sequential() \
            .add_step("step1", agent1) \
            .add_step("step2", agent2) \
            .build()
        
        result = workflow.execute({"task": "test"})
        
        # Just verify execution completes without error
        assert result is not None


class TestParallelWorkflow:
    """Test Parallel Workflow"""
    
    @skip_if_no_key
    def test_build_parallel(self):
        """Test building a parallel workflow"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent1 = create_agent(
            tools=[],
            instructions="Branch 1",
            model=llm
        )
        agent2 = create_agent(
            tools=[],
            instructions="Branch 2",
            model=llm
        )
        merger = create_agent(
            tools=[],
            instructions="Merge results",
            model=llm
        )
        
        workflow = WorkflowBuilder() \
            .parallel() \
            .add_branch("branch1", agent1) \
            .add_branch("branch2", agent2) \
            .add_sync_step("merge", merger) \
            .build()
        
        assert workflow is not None
        assert isinstance(workflow, BaseWorkflow)


class TestConditionalWorkflow:
    """Test Conditional Workflow"""
    
    @skip_if_no_key
    def test_build_conditional(self):
        """Test building a conditional workflow"""
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent_true = create_agent(
            tools=[],
            instructions="True path",
            model=llm
        )
        agent_false = create_agent(
            tools=[],
            instructions="False path",
            model=llm
        )
        
        def condition(state):
            return len(state.get("data", "")) > 5
        
        workflow = WorkflowBuilder() \
            .conditional() \
            .add_condition("check", condition) \
            .if_true(agent=agent_true) \
            .if_false(agent=agent_false) \
            .build()
        
        assert workflow is not None
        assert isinstance(workflow, BaseWorkflow)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
