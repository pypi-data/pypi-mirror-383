"""
Workflow Example - Sequential and Parallel workflows
Run: python examples/workflow_example.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import create_agent, WorkflowBuilder, AgentConfig

# Load environment variables
load_dotenv()

# Define tools for different stages
@tool
def fetch_data(source: str) -> str:
    """Fetch data from a source"""
    return f"Data fetched from {source}: [Sample data]"

@tool
def clean_data(data: str) -> str:
    """Clean and normalize data"""
    return f"Cleaned data: {data} [normalized]"

@tool
def analyze(data: str) -> str:
    """Analyze data"""
    return f"Analysis: {data} shows 25% growth"

@tool
def visualize(data: str) -> str:
    """Create visualizations"""
    return f"Chart created for: {data}"

def main():
    print("=" * 60)
    print("Workflow Example")
    print("=" * 60)
    print()
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Create agents for each stage
    fetcher = create_agent(
        tools=[fetch_data],
        instructions="You fetch data from sources. Use fetch_data tool and save results to data.txt",
        model=llm
    )
    
    cleaner = create_agent(
        tools=[clean_data],
        instructions="You clean and normalize data. Read data files, clean them, save to clean_data.txt",
        model=llm
    )
    
    analyzer = create_agent(
        tools=[analyze],
        instructions="You analyze data and find insights. Read clean data, analyze it, save to analysis.txt",
        model=llm
    )
    
    visualizer = create_agent(
        tools=[visualize],
        instructions="You create visualizations. Read analysis, create charts, save to charts.txt",
        model=llm
    )
    
    reporter = create_agent(
        tools=[],
        instructions="You write reports. Read all files and create a comprehensive report in report.md",
        model=llm
    )
    
    # Build sequential workflow
    print("=" * 60)
    print("SEQUENTIAL WORKFLOW")
    print("=" * 60)
    
    sequential_workflow = WorkflowBuilder() \
        .sequential() \
        .add_step("fetch", fetcher) \
        .add_step("clean", cleaner) \
        .add_step("analyze", analyzer) \
        .add_step("report", reporter) \
        .build()
    
    print("\nExecuting: fetch -> clean -> analyze -> report")
    result = sequential_workflow.execute(
        input={"task": "Analyze Q4 sales data"}
    )
    
    print(f"\n[OK] Sequential workflow complete!")
    print(f"   Steps: {' -> '.join(result.steps_executed)}")
    print(f"   Time: {result.execution_time:.2f}s")
    
    # Build parallel workflow
    print("\n" + "=" * 60)
    print("PARALLEL WORKFLOW")
    print("=" * 60)
    
    # Create multiple data sources
    web_fetcher = create_agent(
        tools=[fetch_data],
        instructions="Fetch data from web sources",
        model=llm
    )
    
    db_fetcher = create_agent(
        tools=[fetch_data],
        instructions="Fetch data from database",
        model=llm
    )
    
    file_fetcher = create_agent(
        tools=[fetch_data],
        instructions="Fetch data from files",
        model=llm
    )
    
    merger = create_agent(
        tools=[],
        instructions="Merge data from all sources into combined_data.txt",
        model=llm
    )
    
    parallel_workflow = WorkflowBuilder() \
        .parallel() \
        .add_branch("web", web_fetcher) \
        .add_branch("database", db_fetcher) \
        .add_branch("files", file_fetcher) \
        .add_sync_step("merge", merger) \
        .build()
    
    print("\nExecuting: [web || database || files] -> merge")
    result = parallel_workflow.execute(
        input={"task": "Gather data from all sources"}
    )
    
    print(f"\n[OK] Parallel workflow complete!")
    print(f"   Branches executed in parallel: 3")
    print(f"   Time: {result.execution_time:.2f}s")
    
    # Build conditional workflow
    print("\n" + "=" * 60)
    print("CONDITIONAL WORKFLOW")
    print("=" * 60)
    
    quick_processor = create_agent(
        tools=[analyze],
        instructions="Quick analysis for small datasets",
        model=llm
    )
    
    batch_processor = create_agent(
        tools=[analyze],
        instructions="Batch processing for large datasets",
        model=llm
    )
    
    conditional_workflow = WorkflowBuilder() \
        .conditional() \
        .add_condition(
            "check_size",
            lambda state: state.get("data_size", 0) > 1000
        ) \
        .if_true(agent=batch_processor) \
        .if_false(agent=quick_processor) \
        .build()
    
    print("\nExecuting: if data_size > 1000 then batch else quick")
    
    # Test with small data
    result = conditional_workflow.execute(
        input={"data_size": 500, "task": "Process data"}
    )
    print(f"[OK] Small data -> quick processor used")
    
    # Test with large data
    result = conditional_workflow.execute(
        input={"data_size": 5000, "task": "Process data"}
    )
    print(f"[OK] Large data -> batch processor used")
    
    print("\n" + "=" * 60)
    print("\n" + "=" * 60)
    print("Workflow complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
