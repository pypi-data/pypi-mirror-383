"""
Example: Local file storage with multi-level folders
Demonstrates file operations across nested directories
"""

from langchain_openai import ChatOpenAI
from suluvai import create_enhanced_agent, EnhancedAgentConfig


def main():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Configure with local storage
    config = EnhancedAgentConfig(
        storage_mode="local",
        storage_path="./my_workspace"
    )
    
    # Create agent
    agent, storage = create_enhanced_agent(
        model=llm,
        tools=[],
        instructions="""You are a file management assistant.
        You can create, read, organize files in nested directories.
        Always use descriptive paths like 'reports/2024/q1/sales.txt'.""",
        config=config
    )
    
    print("📁 Local Storage Demo")
    print("=" * 60)
    
    # Example 1: Create nested directory structure
    print("\n1️⃣  Creating nested directory structure...")
    result = agent.invoke({
        "messages": [("user", """Create the following directory structure:
        - data/sales/2024/q1
        - data/sales/2024/q2
        - reports/monthly
        - reports/quarterly""")]
    })
    print(f"✅ {result['messages'][-1].content}\n")
    
    # Example 2: Write files to different folders
    print("2️⃣  Writing files to nested folders...")
    result = agent.invoke({
        "messages": result["messages"] + [("user", """Write these files:
        1. 'data/sales/2024/q1/january.csv' with content: product,revenue\nA,1000\nB,2000
        2. 'data/sales/2024/q1/february.csv' with content: product,revenue\nA,1500\nB,2500
        3. 'reports/monthly/summary.txt' with content: Q1 sales are strong""")]
    })
    print(f"✅ {result['messages'][-1].content}\n")
    
    # Example 3: List all files recursively
    print("3️⃣  Listing all files...")
    result = agent.invoke({
        "messages": result["messages"] + [("user", "List all files in the workspace")]
    })
    print(f"📋 {result['messages'][-1].content}\n")
    
    # Example 4: Search for specific files
    print("4️⃣  Searching for CSV files...")
    result = agent.invoke({
        "messages": result["messages"] + [("user", "Find all CSV files")]
    })
    print(f"🔍 {result['messages'][-1].content}\n")
    
    # Example 5: Get directory tree
    print("5️⃣  Getting directory tree structure...")
    result = agent.invoke({
        "messages": result["messages"] + [("user", "Show me the directory tree")]
    })
    print(f"🌳 {result['messages'][-1].content}\n")
    
    # Example 6: Direct storage operations (without agent)
    print("6️⃣  Direct storage operations:")
    print(f"   Total files: {len(storage.list_files())}")
    print(f"   Total directories: {len(storage.list_directories())}")
    info = storage.get_storage_info()
    print(f"   Storage size: {info['total_size_mb']} MB")
    print(f"   Base path: {info['base_path']}")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()
