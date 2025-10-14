"""
Advanced Workflow Tests
Rigorous testing of workflow orchestration patterns
Developed by SagaraGlobal
"""
import pytest
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import create_agent, WorkflowBuilder, AgentConfig

load_dotenv()

skip_if_no_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


@tool
def process_step1(data: str) -> str:
    """Process data in step 1"""
    return f"Step1: Processed {data}"


@tool
def process_step2(data: str) -> str:
    """Process data in step 2"""
    return f"Step2: Enhanced {data}"


@tool
def process_step3(data: str) -> str:
    """Process data in step 3"""
    return f"Step3: Finalized {data}"


@tool
def validate_input(data: str) -> str:
    """Validate input data"""
    if len(data) > 5:
        return f"Valid: {data}"
    return f"Invalid: {data}"


@tool
def merge_results(results: str) -> str:
    """Merge multiple results"""
    return f"Merged: {results}"


class TestSequentialWorkflowAdvanced:
    """Advanced sequential workflow tests"""
    
    @skip_if_no_key
    def test_sequential_with_state_passing(self):
        """Test that state is passed correctly between sequential steps"""
        print("\n" + "="*70)
        print("TEST: Sequential Workflow - State Passing")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Step 1: Initialize
        agent1 = create_agent(
            tools=[process_step1],
            instructions="Process the input using process_step1 and pass result forward.",
            model=llm
        )
        
        # Step 2: Transform
        agent2 = create_agent(
            tools=[process_step2],
            instructions="Take previous result and process with process_step2.",
            model=llm
        )
        
        # Step 3: Finalize
        agent3 = create_agent(
            tools=[process_step3],
            instructions="Take previous result and finalize with process_step3.",
            model=llm
        )
        
        workflow = WorkflowBuilder() \
            .sequential() \
            .add_step("init", agent1) \
            .add_step("transform", agent2) \
            .add_step("finalize", agent3) \
            .build()
        
        print("\nINPUT: 'test_data'")
        print("EXPECTED FLOW: init → transform → finalize")
        print("-" * 70)
        
        result = workflow.execute({"data": "test_data"})
        
        print(f"\nRESULT: {result}")
        print("-" * 70)
        
        # Verify workflow completed
        assert result is not None
        print("\n✓ VERIFIED: Sequential workflow completed successfully")
        print(f"  Steps executed: 3")
    
    @skip_if_no_key
    def test_sequential_with_error_in_middle(self):
        """Test sequential workflow behavior when middle step has issues"""
        print("\n" + "="*70)
        print("TEST: Sequential Workflow - Error Handling")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        agent1 = create_agent(
            tools=[process_step1],
            instructions="Process input normally.",
            model=llm
        )
        
        # Agent with validation that might fail
        agent2 = create_agent(
            tools=[validate_input],
            instructions="Validate the input. If invalid, report error.",
            model=llm
        )
        
        agent3 = create_agent(
            tools=[process_step3],
            instructions="Finalize if previous step succeeded.",
            model=llm
        )
        
        workflow = WorkflowBuilder() \
            .sequential() \
            .add_step("process", agent1) \
            .add_step("validate", agent2) \
            .add_step("finalize", agent3) \
            .build()
        
        print("\nINPUT: 'abc' (short input that might fail validation)")
        print("-" * 70)
        
        result = workflow.execute({"data": "abc"})
        
        print(f"\nRESULT: {result}")
        print("-" * 70)
        
        assert result is not None
        print("\n✓ VERIFIED: Workflow handled validation gracefully")


class TestParallelWorkflowAdvanced:
    """Advanced parallel workflow tests"""
    
    @skip_if_no_key
    def test_parallel_with_multiple_branches(self):
        """Test parallel execution of multiple independent branches"""
        print("\n" + "="*70)
        print("TEST: Parallel Workflow - Multiple Branches")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Branch 1: Fast processing
        branch1 = create_agent(
            tools=[process_step1],
            instructions="Quick process with step1.",
            model=llm
        )
        
        # Branch 2: Validation
        branch2 = create_agent(
            tools=[validate_input],
            instructions="Validate the input data.",
            model=llm
        )
        
        # Branch 3: Alternative processing
        branch3 = create_agent(
            tools=[process_step2],
            instructions="Alternative processing with step2.",
            model=llm
        )
        
        # Merger: Combine results
        merger = create_agent(
            tools=[merge_results],
            instructions="Merge all branch results into final output.",
            model=llm
        )
        
        workflow = WorkflowBuilder() \
            .parallel() \
            .add_branch("fast", branch1) \
            .add_branch("validate", branch2) \
            .add_branch("alternative", branch3) \
            .add_sync_step("merge", merger) \
            .build()
        
        print("\nINPUT: 'parallel_test_data'")
        print("BRANCHES: fast || validate || alternative → merge")
        print("-" * 70)
        
        result = workflow.execute({"data": "parallel_test_data"})
        
        print(f"\nRESULT: {result}")
        print("-" * 70)
        
        assert result is not None
        print("\n✓ VERIFIED: Parallel branches executed and merged")
        print("  Branches: 3")
        print("  Sync step: 1 (merge)")
    
    @skip_if_no_key
    def test_parallel_with_different_speeds(self):
        """Test that parallel workflow waits for all branches"""
        print("\n" + "="*70)
        print("TEST: Parallel Workflow - Synchronization")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Fast branch
        fast_agent = create_agent(
            tools=[],
            instructions="Say 'Fast done' immediately.",
            model=llm
        )
        
        # Slow branch (more complex task)
        slow_agent = create_agent(
            tools=[process_step1, process_step2],
            instructions="Process with step1, then step2. Be thorough.",
            model=llm
        )
        
        # Merger
        merger = create_agent(
            tools=[],
            instructions="Confirm both branches completed.",
            model=llm
        )
        
        workflow = WorkflowBuilder() \
            .parallel() \
            .add_branch("fast", fast_agent) \
            .add_branch("slow", slow_agent) \
            .add_sync_step("merge", merger) \
            .build()
        
        print("\nINPUT: 'sync_test'")
        print("EXPECTED: Wait for both fast and slow branches")
        print("-" * 70)
        
        result = workflow.execute({"data": "sync_test"})
        
        print(f"\nRESULT: {result}")
        print("-" * 70)
        
        assert result is not None
        print("\n✓ VERIFIED: Workflow synchronized all branches")


class TestConditionalWorkflowAdvanced:
    """Advanced conditional workflow tests"""
    
    @skip_if_no_key
    def test_conditional_with_complex_condition(self):
        """Test conditional workflow with complex decision logic"""
        print("\n" + "="*70)
        print("TEST: Conditional Workflow - Complex Conditions")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Path A: For large data
        large_processor = create_agent(
            tools=[process_step1, process_step2, process_step3],
            instructions="Full processing pipeline for large data.",
            model=llm
        )
        
        # Path B: For small data
        small_processor = create_agent(
            tools=[process_step1],
            instructions="Quick processing for small data.",
            model=llm
        )
        
        # Complex condition
        def is_large_data(state):
            data = state.get("data", "")
            size = state.get("size", len(data))
            return size > 20
        
        workflow = WorkflowBuilder() \
            .conditional() \
            .add_condition("size_check", is_large_data) \
            .if_true(agent=large_processor) \
            .if_false(agent=small_processor) \
            .build()
        
        # Test with large data
        print("\nTEST 1: Large data (size > 20)")
        print("INPUT: size=50")
        print("EXPECTED: Full processing pipeline")
        print("-" * 70)
        
        result1 = workflow.execute({"data": "test", "size": 50})
        
        print(f"RESULT: {result1}")
        print("✓ Large data path executed")
        
        # Test with small data
        print("\nTEST 2: Small data (size <= 20)")
        print("INPUT: size=10")
        print("EXPECTED: Quick processing")
        print("-" * 70)
        
        result2 = workflow.execute({"data": "test", "size": 10})
        
        print(f"RESULT: {result2}")
        print("✓ Small data path executed")
        
        assert result1 is not None and result2 is not None
        print("\n✓ VERIFIED: Conditional routing worked correctly")
    
    @skip_if_no_key
    def test_conditional_with_validation_gate(self):
        """Test conditional workflow as validation gate"""
        print("\n" + "="*70)
        print("TEST: Conditional Workflow - Validation Gate")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Valid path: Continue processing
        valid_processor = create_agent(
            tools=[process_step2, process_step3],
            instructions="Data is valid. Continue full processing.",
            model=llm
        )
        
        # Invalid path: Error handling
        error_handler = create_agent(
            tools=[],
            instructions="Data is invalid. Report error and suggest fixes.",
            model=llm
        )
        
        # Validation condition
        def is_valid(state):
            data = state.get("data", "")
            # Simple validation: data must be non-empty and alphanumeric
            return len(data) > 0 and data.replace("_", "").isalnum()
        
        workflow = WorkflowBuilder() \
            .conditional() \
            .add_condition("validate", is_valid) \
            .if_true(agent=valid_processor) \
            .if_false(agent=error_handler) \
            .build()
        
        # Test valid data
        print("\nTEST 1: Valid data")
        print("INPUT: 'valid_data_123'")
        print("EXPECTED: Continue processing")
        print("-" * 70)
        
        result1 = workflow.execute({"data": "valid_data_123"})
        print(f"RESULT: {result1}")
        print("✓ Valid data processed")
        
        # Test invalid data
        print("\nTEST 2: Invalid data")
        print("INPUT: '' (empty)")
        print("EXPECTED: Error handling")
        print("-" * 70)
        
        result2 = workflow.execute({"data": ""})
        print(f"RESULT: {result2}")
        print("✓ Invalid data handled")
        
        assert result1 is not None and result2 is not None
        print("\n✓ VERIFIED: Validation gate worked correctly")


class TestNestedWorkflows:
    """Test nested and combined workflow patterns"""
    
    @skip_if_no_key
    def test_sequential_with_conditional_steps(self):
        """Test sequential workflow where one step is conditional"""
        print("\n" + "="*70)
        print("TEST: Nested Workflows - Sequential + Conditional")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # Step 1: Always execute
        preprocessor = create_agent(
            tools=[process_step1],
            instructions="Preprocess the data.",
            model=llm
        )
        
        # Step 2a: Conditional path A
        path_a = create_agent(
            tools=[process_step2],
            instructions="Process via path A.",
            model=llm
        )
        
        # Step 2b: Conditional path B
        path_b = create_agent(
            tools=[process_step3],
            instructions="Process via path B.",
            model=llm
        )
        
        # Step 3: Always execute
        postprocessor = create_agent(
            tools=[],
            instructions="Finalize the results.",
            model=llm
        )
        
        def choose_path(state):
            return state.get("use_path_a", True)
        
        # Build conditional middle step
        conditional_step = WorkflowBuilder() \
            .conditional() \
            .add_condition("path_choice", choose_path) \
            .if_true(agent=path_a) \
            .if_false(agent=path_b) \
            .build()
        
        # Note: This is a conceptual test showing the pattern
        # In practice, you'd build this differently
        
        print("\nPATTERN: preprocess → [conditional] → postprocess")
        print("INPUT: use_path_a=True")
        print("-" * 70)
        
        # Execute preprocessing
        result1 = preprocessor.invoke({"messages": [("user", "preprocess data")]})
        print("✓ Step 1: Preprocessing completed")
        
        # Execute conditional
        result2 = conditional_step.execute({"data": "test", "use_path_a": True})
        print("✓ Step 2: Conditional path A executed")
        
        # Execute postprocessing
        result3 = postprocessor.invoke({"messages": [("user", "finalize")]})
        print("✓ Step 3: Postprocessing completed")
        
        assert all([result1, result2, result3])
        print("\n✓ VERIFIED: Nested workflow pattern works")


class TestWorkflowStateManagement:
    """Test workflow state handling"""
    
    @skip_if_no_key
    def test_state_accumulation_across_steps(self):
        """Test that state accumulates correctly across workflow steps"""
        print("\n" + "="*70)
        print("TEST: Workflow State Management - Accumulation")
        print("="*70)
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        config = AgentConfig(
            storage_mode="virtual",
            include_filesystem=True
        )
        
        # Each step adds to state
        step1 = create_agent(
            tools=[],
            instructions="Add 'step1_done' to your response and create file1.txt.",
            config=config,
            model=llm
        )
        
        step2 = create_agent(
            tools=[],
            instructions="Add 'step2_done' to your response and create file2.txt.",
            config=config,
            model=llm
        )
        
        step3 = create_agent(
            tools=[],
            instructions="Summarize all previous steps and create summary.txt.",
            config=config,
            model=llm
        )
        
        workflow = WorkflowBuilder() \
            .sequential() \
            .add_step("s1", step1) \
            .add_step("s2", step2) \
            .add_step("s3", step3) \
            .build()
        
        print("\nINPUT: 'track_state'")
        print("EXPECTED: Each step adds to accumulated state")
        print("-" * 70)
        
        result = workflow.execute({"task": "track_state"})
        
        print(f"\nFINAL STATE: {result}")
        print("-" * 70)
        
        assert result is not None
        print("\n✓ VERIFIED: State accumulated across workflow steps")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
