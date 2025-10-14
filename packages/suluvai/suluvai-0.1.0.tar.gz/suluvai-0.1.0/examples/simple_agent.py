"""
Simple Agent Example - DeepAgents style
Run: python examples/simple_agent.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from suluvai import create_agent

# Load environment variables
load_dotenv()

# Define a simple tool
@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print("=" * 60)
    print("Simple SuluvAI Agent Example")
    print("=" * 60)
    print()
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Create agent with user-controlled prompt
    agent = create_agent(
        tools=[calculate],
        instructions="""You are a helpful math assistant.

When given math problems:
1. Use the planning tool to break down complex problems
2. Use the calculate tool to compute results
3. Show your work clearly
4. Save calculations to files if needed

Be precise and explain your reasoning.""",
        model=llm
    )
    
    # Use the agent
    print("Task: Calculate (15 + 27) * 3 - 10\n")
    print("Agent working...")
    print("-" * 60)
    
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Calculate (15 + 27) * 3 - 10"}]
    })
    
    print(result["messages"][-1].content)
    print("-" * 60)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
