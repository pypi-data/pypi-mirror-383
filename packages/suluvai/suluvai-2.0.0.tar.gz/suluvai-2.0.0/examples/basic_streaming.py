"""
Example: Basic streaming with token-by-token output
Demonstrates real-time streaming of agent responses
"""

import asyncio
from langchain_openai import ChatOpenAI
from suluvai import (
    create_enhanced_agent,
    EnhancedAgentConfig,
    stream_agent_events,
    StreamEventType
)


async def main():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Configure agent with streaming enabled
    config = EnhancedAgentConfig(
        storage_mode="local",
        storage_path="./workspace",
        enable_streaming=True
    )
    
    # Create enhanced agent
    agent, storage = create_enhanced_agent(
        model=llm,
        tools=[],
        instructions="""You are a helpful AI assistant. 
        Answer questions clearly and concisely.""",
        config=config
    )
    
    print("🤖 Streaming Agent Demo")
    print("=" * 50)
    
    # Stream the agent's response
    print("\n👤 User: Tell me a short story about AI\n")
    print("🤖 Assistant: ", end="", flush=True)
    
    async for event in stream_agent_events(
        agent,
        {"messages": [("user", "Tell me a short story about AI")]}
    ):
        if event.event_type == StreamEventType.TOKEN:
            # Print each token as it arrives
            print(event.data, end="", flush=True)
        
        elif event.event_type == StreamEventType.TOOL_START:
            print(f"\n\n🔧 Using tool: {event.data['tool_name']}")
            print(f"   Input: {event.data['input']}")
        
        elif event.event_type == StreamEventType.TOOL_END:
            print(f"   Output: {event.data['output']}\n")
        
        elif event.event_type == StreamEventType.AGENT_FINISH:
            print("\n\n✅ Agent finished")


if __name__ == "__main__":
    asyncio.run(main())
