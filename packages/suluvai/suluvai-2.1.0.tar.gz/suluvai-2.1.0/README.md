# SuluvAI - Production-Ready AI Agent Framework

**Developed by SagaraGlobal**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-82%20passing-brightgreen.svg)]()

A powerful, production-ready AI agent framework built on LangGraph with comprehensive support for streaming, storage, memory management, and multi-agent orchestration.

---

## 🚀 Features

### Core Capabilities
- **🤖 Intelligent Agents** - Create AI agents with custom tools, instructions, and behaviors
- **📊 Real-time Streaming** - Stream agent responses token-by-token for better UX
- **💾 Flexible Storage** - Virtual (in-memory), Local (disk), or Hybrid storage modes
- **🧠 Memory Systems** - Conversation history and working memory support
- **🔧 Planning Tools** - Built-in TODO/planning capabilities for complex tasks
- **📁 File Operations** - Integrated filesystem tools for reading/writing files

### Advanced Features
- **👥 Multi-Agent Systems** - Subagent delegation and collaboration
- **🔄 Workflow Orchestration** - Sequential, Parallel, and Conditional workflows
- **🎯 Type-Safe Configuration** - Pydantic-based configuration management
- **📡 Optional Tracing** - LangSmith integration for debugging (optional)
- **🔌 Extensible** - Easy to add custom tools and behaviors

---

## 📦 Installation

### Basic Installation
```bash
pip install suluvai
```

### With OpenAI Support
```bash
pip install suluvai[openai]
```

### With Anthropic Support
```bash
pip install suluvai[anthropic]
```

### Full Installation (All Features)
```bash
pip install suluvai[openai,anthropic,tracing]
```

### Development Installation
```bash
pip install suluvai[dev]
```

---

## 🎯 Quick Start

### Simple Agent

```python
from suluvai import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Define a custom tool
@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression"""
    return str(eval(expression))

# Create an agent
llm = ChatOpenAI(model="gpt-4o-mini")

agent = create_agent(
    tools=[calculate],
    instructions="You are a helpful math assistant. Use the calculate tool for math problems.",
    model=llm
)

# Use the agent
result = agent.invoke({
    "messages": [("user", "What is 25 * 4 + 10?")]
})

print(result["messages"][-1].content)
# Output: The result is 110.
```

### Agent with File Storage

```python
from suluvai import create_agent, AgentConfig

config = AgentConfig(
    storage_mode="local",  # or "virtual" or "hybrid"
    local_storage_path="./my_workspace",
    include_filesystem=True
)

agent = create_agent(
    tools=[],
    instructions="You can create and manage files. Save important information.",
    config=config,
    model=llm
)

result = agent.invoke({
    "messages": [("user", "Create a file called notes.txt with 'Hello World'")]
})
```

### Streaming Agent

```python
from suluvai import stream_agent
import asyncio

async def main():
    async for event in stream_agent(
        agent,
        {"messages": [("user", "Write a short story about AI")]}
    ):
        if event.event_type == "token":
            print(event.data, end="", flush=True)

asyncio.run(main())
```

### Multi-Agent System

```python
# Define specialized subagents
researcher = {
    "name": "researcher",
    "description": "Searches and gathers information",
    "prompt": "You are a research specialist. Gather comprehensive information.",
    "tools": [search_tool]
}

writer = {
    "name": "writer",
    "description": "Writes professional reports",
    "prompt": "You are a professional writer. Create clear, well-structured content.",
    "tools": [write_tool]
}

# Create coordinator agent
coordinator = create_agent(
    tools=[search_tool, write_tool],
    instructions="Delegate research to researcher and writing to writer.",
    subagents=[researcher, writer],
    model=llm
)

result = coordinator.invoke({
    "messages": [("user", "Research AI trends and write a report")]
})
```

### Workflow Orchestration

```python
from suluvai import WorkflowBuilder

# Create agents for each step
fetcher = create_agent(tools=[fetch_data], instructions="Fetch data", model=llm)
analyzer = create_agent(tools=[analyze], instructions="Analyze data", model=llm)
reporter = create_agent(tools=[report], instructions="Create report", model=llm)

# Build sequential workflow
workflow = WorkflowBuilder() \
    .sequential() \
    .add_step("fetch", fetcher) \
    .add_step("analyze", analyzer) \
    .add_step("report", reporter) \
    .build()

# Execute workflow
result = workflow.execute({"task": "Analyze Q4 sales"})
```

---

## 📚 Configuration Options

### AgentConfig

```python
from suluvai import AgentConfig

config = AgentConfig(
    storage_mode="hybrid",           # "virtual", "local", or "hybrid"
    local_storage_path="./workspace", # Path for local storage
    memory_type="conversation",       # "conversation", "working", or "none"
    enable_streaming=True,            # Enable streaming support
    include_planning=True,            # Include TODO/planning tools
    include_filesystem=True           # Include file operation tools
)
```

### Storage Modes

- **Virtual**: In-memory storage (fast, temporary)
- **Local**: Disk-based storage (persistent, real files)
- **Hybrid**: Virtual for temp files, local for outputs

---

## 🧪 Testing

SuluvAI comes with a comprehensive test suite (82 tests):

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=suluvai tests/
```

**Test Coverage:**
- ✅ 40 Unit Tests (Storage, Memory, Config)
- ✅ 32 Integration Tests (Agents, Workflows, Subagents)
- ✅ 10 End-to-End Tests (Real scenarios)

---

## 📖 Documentation

### Core Components

- **`create_agent()`** - Create an AI agent with tools and configuration
- **`AgentConfig`** - Configure agent behavior and features
- **`SubAgent`** - Define specialized subagents
- **`WorkflowBuilder`** - Build complex multi-step workflows
- **`stream_agent()`** - Stream agent responses in real-time

### Storage Systems

- **`VirtualStorage`** - In-memory file storage
- **`LocalStorage`** - Disk-based file storage
- **`HybridStorage`** - Combined virtual + local storage

### Memory Systems

- **`ConversationMemory`** - Track conversation history
- **`WorkingMemory`** - Scratchpad for temporary data

---

## 🔧 Advanced Usage

### Custom Tools

```python
from langchain_core.tools import tool

@tool
def custom_tool(param: str) -> str:
    """Description of what the tool does"""
    # Your logic here
    return result

agent = create_agent(
    tools=[custom_tool],
    instructions="Use custom_tool when needed",
    model=llm
)
```

### Error Handling

```python
try:
    result = agent.invoke(
        {"messages": [("user", "task")]},
        {"recursion_limit": 10}
    )
except Exception as e:
    print(f"Agent error: {e}")
```

### Planning and Organization

```python
config = AgentConfig(include_planning=True)

agent = create_agent(
    tools=[],
    instructions="""For complex tasks:
    1. Create a plan using write_todos
    2. Execute each step
    3. Mark todos as done
    4. Summarize results""",
    config=config,
    model=llm
)
```

---

## 🌟 Examples

Check out the `examples/` directory for complete working examples:

- **`simple_agent.py`** - Basic agent with tools
- **`streaming_example.py`** - Real-time streaming
- **`workflow_example.py`** - Workflow orchestration
- **`agent_with_subagents.py`** - Multi-agent collaboration

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/sagaraglobal/suluvai.git
cd suluvai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev,openai]"

# Run tests
pytest
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🏢 About SagaraGlobal

SuluvAI is developed and maintained by **SagaraGlobal**, committed to building production-ready AI solutions.

- **Website**: https://sagaraglobal.com
- **Email**: info@sagaraglobal.com

---

## 🙏 Acknowledgments

Built on top of:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- Inspired by DeepAgents architecture

---

## 📊 Project Status

- **Version**: 0.1.0
- **Status**: Beta (Production-Ready)
- **Python**: 3.9+
- **Tests**: 82 passing
- **Coverage**: High

---

## 🔗 Links

- [GitHub Repository](https://github.com/sagaraglobal/suluvai)
- [Issue Tracker](https://github.com/sagaraglobal/suluvai/issues)
- [PyPI Package](https://pypi.org/project/suluvai/)

---

**Made with ❤️ by SagaraGlobal**
