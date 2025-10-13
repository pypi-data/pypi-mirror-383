"""
Example: Advanced multi-level folder operations
Demonstrates complex file operations across deep directory structures
"""

from langchain_openai import ChatOpenAI
from suluvai import create_enhanced_agent, EnhancedAgentConfig, LocalFileStorage


def direct_storage_demo():
    """Demonstrate direct storage API usage"""
    print("📦 Direct Storage API Demo")
    print("=" * 60)
    
    storage = LocalFileStorage("./file_system_demo")
    
    # Create complex directory structure
    print("\n1️⃣  Creating multi-level directory structure...")
    dirs = [
        "projects/ai/models",
        "projects/ai/datasets",
        "projects/web/frontend",
        "projects/web/backend",
        "documents/reports/2024/q1",
        "documents/reports/2024/q2",
        "temp/cache"
    ]
    for dir_path in dirs:
        storage.create_directory(dir_path)
        print(f"   ✓ Created: {dir_path}")
    
    # Write files to various locations
    print("\n2️⃣  Writing files to nested folders...")
    files = {
        "projects/ai/models/gpt4.txt": "GPT-4 model configuration",
        "projects/ai/models/claude.txt": "Claude model configuration",
        "projects/ai/datasets/training.csv": "id,text,label\n1,hello,positive",
        "projects/web/frontend/index.html": "<html><body>Hello</body></html>",
        "projects/web/backend/server.py": "# FastAPI server\nfrom fastapi import FastAPI",
        "documents/reports/2024/q1/sales.md": "# Q1 Sales Report\n\nRevenue: $1M",
        "documents/reports/2024/q2/sales.md": "# Q2 Sales Report\n\nRevenue: $1.5M",
        "temp/cache/session.json": '{"user": "admin", "token": "xyz"}',
    }
    
    for filepath, content in files.items():
        storage.write_file(filepath, content)
        print(f"   ✓ Written: {filepath}")
    
    # List files in specific directories
    print("\n3️⃣  Listing files by directory...")
    print("\n   AI Models:")
    for file in storage.list_files("projects/ai/models", recursive=False):
        print(f"     • {file}")
    
    print("\n   All reports (recursive):")
    for file in storage.list_files("documents/reports", recursive=True):
        print(f"     • {file}")
    
    # Search operations
    print("\n4️⃣  Search operations...")
    print("\n   All Markdown files:")
    md_files = storage.search_files("*.md")
    for file in md_files:
        print(f"     • {file}")
    
    print("\n   Python files in projects:")
    py_files = storage.search_files("*.py", "projects")
    for file in py_files:
        print(f"     • {file}")
    
    print("\n   All text files:")
    txt_files = storage.search_files("*.txt")
    for file in txt_files:
        print(f"     • {file}")
    
    # Display directory tree
    print("\n5️⃣  Complete directory tree:")
    tree = storage.get_tree(max_depth=None)
    
    def print_tree(tree_dict, indent=0):
        for key, value in sorted(tree_dict.items()):
            if key == "_files":
                for file in sorted(value):
                    print("  " * indent + f"📄 {file}")
            else:
                print("  " * indent + f"📁 {key}/")
                if isinstance(value, dict):
                    print_tree(value, indent + 1)
    
    print_tree(tree)
    
    # Copy and move operations
    print("\n6️⃣  File operations...")
    storage.copy_file(
        "documents/reports/2024/q1/sales.md",
        "documents/reports/2024/q1/sales_backup.md"
    )
    print("   ✓ Copied: sales.md → sales_backup.md")
    
    storage.move_file(
        "temp/cache/session.json",
        "projects/web/backend/session.json"
    )
    print("   ✓ Moved: temp/cache/session.json → projects/web/backend/session.json")
    
    # Storage statistics
    print("\n7️⃣  Storage statistics:")
    info = storage.get_storage_info()
    print(f"   • Base path: {info['base_path']}")
    print(f"   • Total files: {info['total_files']}")
    print(f"   • Total directories: {info['directories']}")
    print(f"   • Total size: {info['total_size_bytes']} bytes ({info['total_size_mb']} MB)")
    
    # List all directories
    print("\n8️⃣  All directories:")
    all_dirs = storage.list_directories()
    for dir_path in all_dirs[:10]:  # Show first 10
        print(f"   • {dir_path}/")
    if len(all_dirs) > 10:
        print(f"   ... and {len(all_dirs) - 10} more")
    
    print("\n✅ Demo complete!")


def agent_with_folders():
    """Demonstrate agent working with folders"""
    print("\n\n🤖 Agent with Multi-Level Folders")
    print("=" * 60)
    
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    config = EnhancedAgentConfig(
        storage_mode="local",
        storage_path="./agent_file_system"
    )
    
    agent, storage = create_enhanced_agent(
        model=llm,
        tools=[],
        instructions="""You are a file organization expert.
        Help users organize files in logical directory structures.
        Use descriptive paths like 'category/subcategory/year/file.ext'.""",
        config=config
    )
    
    print("\n📝 Task: Organize project files\n")
    
    result = agent.invoke({
        "messages": [("user", """I need to organize my project files. Create:
        
        1. A 'src' directory with subdirectories: 'components', 'utils', 'api'
        2. A 'docs' directory with: 'api', 'guides', 'tutorials'
        3. A 'tests' directory with: 'unit', 'integration', 'e2e'
        
        Then create README.md files in each main directory explaining its purpose.""")]
    })
    
    print(f"🤖 Agent response:\n{result['messages'][-1].content}\n")
    
    # Show what was created
    print("\n📁 Created structure:")
    tree = storage.get_tree()
    
    def print_tree(tree_dict, indent=0):
        for key, value in sorted(tree_dict.items()):
            if key == "_files":
                for file in sorted(value):
                    print("  " * indent + f"📄 {file}")
            else:
                print("  " * indent + f"📁 {key}/")
                if isinstance(value, dict):
                    print_tree(value, indent + 1)
    
    print_tree(tree)
    
    print("\n✅ Organization complete!")


if __name__ == "__main__":
    # Run direct storage demo
    direct_storage_demo()
    
    # Run agent demo
    agent_with_folders()
