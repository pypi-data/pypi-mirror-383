"""
Streaming Example - Real-time token and event streaming
Run: python examples/streaming_example.py
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import create_agent, stream_agent, AgentConfig

# Load environment variables
load_dotenv()

@tool
def research_topic(topic: str) -> str:
    """Research a topic and return information"""
    return f"Research findings on {topic}: [Detailed information about {topic}]"

async def main():
    print("=" * 60)
    print("Streaming Example")
    print("=" * 60)
    print()
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Create agent with streaming enabled
    agent = create_agent(
        tools=[research_topic],
        instructions="""You are a storytelling researcher.

When given a topic:
1. Use planning tool to organize your approach
2. Research the topic using research_topic tool
3. Write an engaging story or explanation
4. Save your work to story.md

Be creative and engaging!""",
        config=AgentConfig(
            enable_streaming=True,
            storage_mode="local",
            local_storage_path="./streaming_output"
        ),
        model=llm
    )
    
    print("Task: Write a short story about AI\n")
    print("=" * 60)
    print("STREAMING OUTPUT:")
    print("=" * 60)
    print()
    
    full_response = ""
    
    # Stream agent execution
    async for event in stream_agent(
        agent,
        {"messages": [{"role": "user", "content": "Write a short story about AI and humanity"}]}
    ):
        if event.event_type == "token":
            # Stream tokens in real-time
            print(event.data, end="", flush=True)
            full_response += event.data
            
        elif event.event_type == "tool_start":
            # Show tool usage
            tool_name = event.data.get("tool_name", "unknown")
            print(f"\n\n[Using tool: {tool_name}]", flush=True)
            
        elif event.event_type == "tool_end":
            # Show tool completion
            print(f" [Done]\n", flush=True)
            
        elif event.event_type == "planning":
            # Show when agent creates a plan
            print(f"\n\n[Planning created]\n", flush=True)
            
        elif event.event_type == "file_write":
            # Show file operations
            filepath = event.data.get("filepath", "file")
            print(f"\n\n[File saved: {filepath}]\n", flush=True)
            
        elif event.event_type == "subagent_start":
            # Show subagent delegation
            name = event.data.get("name", "unknown")
            print(f"\n\n[Delegating to: {name}]\n", flush=True)
            
        elif event.event_type == "agent_finish":
            # Final completion
            print(f"\n\n [Complete!]")
    
    print("\n" + "=" * 60)
    print(f"Total characters streamed: {len(full_response)}")
    print("=" * 60)
    
    print("\n\n" + "=" * 60)
    print("Streaming complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
