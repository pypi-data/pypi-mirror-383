"""
Example: Research agent with streaming and file storage
A complete example similar to DeepAgents research example
"""

import asyncio
import os
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import (
    create_enhanced_agent,
    EnhancedAgentConfig,
    SubAgent,
    stream_agent_events,
    StreamEventType
)


# Define research tools
@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for information.
    
    Args:
        query: Search query
        max_results: Maximum number of results
    """
    # Simulated search results
    return f"""Search results for '{query}':
    1. LangChain is a framework for developing LLM applications
    2. It provides abstractions for working with language models
    3. Key features: chains, agents, memory, callbacks
    4. Integrates with OpenAI, Anthropic, and other providers
    5. Used for building chatbots, question-answering, and more"""


@tool
def analyze_data(data: str, analysis_type: str = "summary") -> str:
    """
    Analyze data and provide insights.
    
    Args:
        data: Data to analyze
        analysis_type: Type of analysis (summary, trends, statistics)
    """
    return f"Analysis ({analysis_type}): The data shows consistent growth patterns."


async def main():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # Configure with local storage and streaming
    config = EnhancedAgentConfig(
        storage_mode="local",
        storage_path="./research_workspace",
        enable_streaming=True
    )
    
    # Define a research subagent
    research_subagent = SubAgent(
        name="web_researcher",
        description="Searches the web and gathers information",
        tools=[search_web],
        instructions="""You are a web research specialist.
        Use the search_web tool to find information.
        Provide detailed and accurate findings."""
    )
    
    # Define an analysis subagent
    analysis_subagent = SubAgent(
        name="data_analyst",
        description="Analyzes data and provides insights",
        tools=[analyze_data],
        instructions="""You are a data analyst.
        Analyze information and identify key insights.
        Present findings clearly and concisely."""
    )
    
    # Create main agent with subagents
    agent, storage = create_enhanced_agent(
        model=llm,
        tools=[],
        subagents=[research_subagent, analysis_subagent],
        instructions="""You are an expert research assistant.
        
        Your workflow:
        1. Use write_todos to create a research plan
        2. Delegate research tasks to web_researcher subagent
        3. Save research findings to files (e.g., 'research/sources.txt')
        4. Delegate analysis to data_analyst subagent
        5. Save final report to 'research/report.md'
        
        Be thorough and organized.""",
        config=config
    )
    
    print("🔬 Research Agent with Streaming Demo")
    print("=" * 70)
    
    # Research task
    task = "Research LangChain and write a comprehensive report"
    
    print(f"\n📋 Task: {task}\n")
    print("🤖 Agent: ", end="", flush=True)
    
    current_section = "response"
    
    async for event in stream_agent_events(
        agent,
        {"messages": [("user", task)]}
    ):
        if event.event_type == StreamEventType.TOKEN:
            print(event.data, end="", flush=True)
        
        elif event.event_type == StreamEventType.TOOL_START:
            tool_name = event.data['tool_name']
            print(f"\n\n🔧 [{tool_name}]", end=" ")
            if tool_name.startswith("call_"):
                subagent = tool_name.replace("call_", "")
                print(f"Delegating to {subagent} subagent...")
            elif tool_name == "write_file":
                print(f"Saving file: {event.data['input'].get('filepath', 'unknown')}")
            elif tool_name == "write_todos":
                print("Creating task plan...")
        
        elif event.event_type == StreamEventType.TOOL_END:
            print("✅", flush=True)
        
        elif event.event_type == StreamEventType.AGENT_FINISH:
            print("\n\n" + "=" * 70)
            print("✅ Research Complete!\n")
    
    # Show created files
    print("📁 Files created:")
    files = storage.list_files()
    for file in files:
        metadata = storage.get_metadata(file)
        print(f"  • {file} ({metadata.size} bytes)")
    
    # Show directory tree
    print("\n🌳 Directory structure:")
    tree = storage.get_tree()
    print(f"  {tree}")
    
    print("\n✨ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
