"""
Complete Example: All features in one
Demonstrates streaming, local storage, subagents, and multi-level folders
"""

import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import (
    create_enhanced_agent,
    EnhancedAgentConfig,
    SubAgent,
    stream_agent_events,
    StreamEventType,
    StreamingCallback,
    stream_with_callback
)


# Custom tools
@tool
def fetch_sales_data(year: int, quarter: str) -> str:
    """Fetch sales data for a given year and quarter"""
    return f"""Sales data for {year} {quarter}:
Product A: $50,000
Product B: $75,000
Product C: $100,000
Total: $225,000"""


@tool
def calculate_growth(current: float, previous: float) -> str:
    """Calculate growth percentage"""
    growth = ((current - previous) / previous) * 100
    return f"Growth: {growth:.2f}%"


# Custom streaming callback
class CustomCallback(StreamingCallback):
    """Custom callback for handling streaming events"""
    
    def __init__(self):
        self.tool_count = 0
        self.token_count = 0
    
    def on_token(self, token: str, **kwargs):
        """Called for each token"""
        self.token_count += len(token)
        print(token, end="", flush=True)
    
    def on_tool_start(self, tool_name: str, tool_input: dict, **kwargs):
        """Called when a tool starts"""
        self.tool_count += 1
        print(f"\n\n🔧 Tool #{self.tool_count}: {tool_name}")
        print(f"   Input: {tool_input}")
    
    def on_tool_end(self, tool_name: str, tool_output: any, **kwargs):
        """Called when a tool ends"""
        print(f"   ✅ Complete\n")
    
    def on_agent_finish(self, output: dict, **kwargs):
        """Called when agent finishes"""
        print(f"\n\n📊 Statistics:")
        print(f"   • Tokens generated: ~{self.token_count}")
        print(f"   • Tools used: {self.tool_count}")


async def main():
    print("🚀 Complete Zita Agents Demo")
    print("=" * 70)
    print("Features: Streaming + Local Storage + Subagents + Multi-level Folders")
    print("=" * 70)
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # Configure with all features
    config = EnhancedAgentConfig(
        storage_mode="local",  # Use local file storage
        storage_path="./complete_workspace",
        enable_streaming=True,
        include_filesystem=True,
        include_todos=True
    )
    
    # Define specialized subagents
    data_fetcher = SubAgent(
        name="data_fetcher",
        description="Fetches sales data from database",
        tools=[fetch_sales_data],
        instructions="""You are a data fetcher.
        Use fetch_sales_data to retrieve information.
        Always specify year and quarter clearly."""
    )
    
    analyst = SubAgent(
        name="analyst",
        description="Analyzes data and calculates metrics",
        tools=[calculate_growth],
        instructions="""You are a data analyst.
        Calculate growth rates and provide insights.
        Be precise with numbers."""
    )
    
    # Create the main agent
    print("\n🏗️  Creating agent with subagents...")
    agent, storage = create_enhanced_agent(
        model=llm,
        tools=[],  # No direct tools, only subagents
        subagents=[data_fetcher, analyst],
        instructions="""You are a business intelligence assistant.
        
        Your workflow:
        1. Create a TODO list to plan your work
        2. Use data_fetcher to get sales data
        3. Save raw data to 'data/raw/{year}_{quarter}.txt'
        4. Use analyst to calculate growth metrics
        5. Save analysis to 'reports/{year}/analysis.md'
        6. Create a final summary report in 'reports/summary.md'
        
        Always organize files in logical directory structures.""",
        config=config
    )
    
    print("✅ Agent created")
    print(f"📁 Workspace: {storage.base_path}")
    
    # Task for the agent
    task = """Analyze sales performance for Q1 2024 compared to Q4 2023.
    Create a comprehensive report with all findings organized in folders."""
    
    print(f"\n📋 Task: {task}\n")
    print("🤖 Agent Output:")
    print("-" * 70)
    
    # Use custom callback for streaming
    callback = CustomCallback()
    result = await stream_with_callback(agent, {"messages": [("user", task)]}, callback)
    
    print("\n" + "=" * 70)
    print("📂 Workspace Structure")
    print("=" * 70)
    
    # Show the directory tree
    tree = storage.get_tree(max_depth=None)
    
    def print_tree(tree_dict, indent=0):
        for key, value in sorted(tree_dict.items()):
            if key == "_files":
                for file in sorted(value):
                    metadata = storage.get_metadata(file) if indent == 0 else None
                    size = f" ({metadata.size} bytes)" if metadata else ""
                    print("  " * indent + f"📄 {file}{size}")
            else:
                print("  " * indent + f"📁 {key}/")
                if isinstance(value, dict):
                    print_tree(value, indent + 1)
    
    print_tree(tree)
    
    # Storage statistics
    print("\n" + "=" * 70)
    print("💾 Storage Statistics")
    print("=" * 70)
    info = storage.get_storage_info()
    print(f"• Base path: {info['base_path']}")
    print(f"• Total files: {info['total_files']}")
    print(f"• Total directories: {info['directories']}")
    print(f"• Storage size: {info['total_size_bytes']} bytes ({info['total_size_mb']} MB)")
    
    # Show file contents
    print("\n" + "=" * 70)
    print("📖 Sample File Contents")
    print("=" * 70)
    
    all_files = storage.list_files()
    if all_files:
        # Show first file content
        first_file = all_files[0]
        print(f"\n📄 {first_file}:")
        print("-" * 70)
        content = storage.read_file(first_file)
        print(content[:500])  # Show first 500 chars
        if len(content) > 500:
            print("\n... (truncated)")
    
    # Demonstrate search
    print("\n" + "=" * 70)
    print("🔍 File Search Examples")
    print("=" * 70)
    
    print("\n• Markdown files:")
    md_files = storage.search_files("*.md")
    for f in md_files:
        print(f"  - {f}")
    
    print("\n• Files in data directory:")
    data_files = storage.search_files("*", "data")
    for f in data_files:
        print(f"  - {f}")
    
    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("✓ Real-time token streaming")
    print("✓ Event-based callbacks")
    print("✓ Multi-level directory structure")
    print("✓ Local file persistence")
    print("✓ Subagent delegation")
    print("✓ File search and organization")
    print("✓ Metadata tracking")
    print("\n🎉 All features working together!")


if __name__ == "__main__":
    asyncio.run(main())
