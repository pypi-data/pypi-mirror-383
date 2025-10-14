# Changelog

All notable changes to SuluvAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2025-10-13

### 🎉 Major Update - Production Ready Release

**Developed by SagaraGlobal**

This is the official production-ready release with comprehensive testing and documentation.

### ✨ What's New in 2.1.0

### 🎉 Initial Release

**Developed by SagaraGlobal**

This is the first production-ready release of SuluvAI, a comprehensive AI agent framework built on LangGraph.

### ✨ Added

#### Core Features
- **Agent Creation** - `create_agent()` function for building AI agents with custom tools and instructions
- **Streaming Support** - Real-time token streaming with `stream_agent()` async generator
- **Storage Systems** - Three storage modes:
  - Virtual (in-memory) storage for temporary data
  - Local (disk-based) storage for persistent files
  - Hybrid storage combining both approaches
- **Memory Management** - Two memory types:
  - ConversationMemory for chat history
  - WorkingMemory for scratchpad data
- **Configuration** - Type-safe `AgentConfig` with Pydantic validation

#### Advanced Features
- **Multi-Agent Systems** - Subagent delegation and collaboration
  - Define subagents with specialized tools and prompts
  - Automatic tool creation for calling subagents
  - Support for both dict and `SubAgent` object formats
- **Workflow Orchestration** - `WorkflowBuilder` for complex workflows:
  - Sequential workflows (step-by-step execution)
  - Parallel workflows (concurrent branch execution)
  - Conditional workflows (dynamic routing)
- **Built-in Tools**:
  - Filesystem tools (read, write, list, search files)
  - Planning tools (create and manage TODO lists)
  - Extensible tool system

#### Developer Experience
- **Type Safety** - Full type hints and Pydantic models
- **Optional Tracing** - LangSmith integration (opt-in)
- **Comprehensive Examples** - 4 complete working examples
- **Extensive Documentation** - README, QUICKSTART, and inline docs

### 🧪 Testing

- **82 Comprehensive Tests**:
  - 40 Unit tests (Storage, Memory, Config)
  - 32 Integration tests (Agents, Workflows, Subagents)
  - 10 End-to-End tests (Real-world scenarios)
- **Test Coverage**: High coverage across all modules
- **Pytest Configuration**: Industry-standard testing setup
- **CI/CD Ready**: All tests passing

### 📦 Package Structure

```
suluvai/
├── core/           # Core agent functionality
│   ├── agent.py    # Agent creation and management
│   ├── config.py   # Configuration classes
│   └── state.py    # State management
├── storage/        # Storage systems
│   ├── virtual.py  # In-memory storage
│   ├── local.py    # Disk-based storage
│   └── hybrid.py   # Combined storage
├── memory/         # Memory systems
│   ├── conversation.py  # Chat history
│   └── working.py       # Scratchpad memory
├── workflows/      # Workflow orchestration
│   ├── builder.py       # Workflow builder
│   ├── sequential.py    # Sequential workflows
│   ├── parallel.py      # Parallel workflows
│   └── conditional.py   # Conditional workflows
├── tools/          # Built-in tools
│   ├── filesystem.py    # File operations
│   └── planning.py      # TODO management
└── utils/          # Utilities
    ├── stream_agent.py  # Streaming support
    └── tracing.py       # Optional tracing
```

### 📚 Examples

- `simple_agent.py` - Basic agent with calculator tool
- `streaming_example.py` - Real-time streaming demonstration
- `workflow_example.py` - Sequential, parallel, and conditional workflows
- `agent_with_subagents.py` - Multi-agent collaboration

### 🔧 Dependencies

**Core Dependencies:**
- langchain-core >= 0.3.0
- langgraph >= 0.2.0
- pydantic >= 2.0.0
- typing-extensions >= 4.0.0

**Optional Dependencies:**
- langchain-openai >= 0.2.0 (for OpenAI models)
- langchain-anthropic >= 0.2.0 (for Anthropic models)
- langsmith >= 0.1.0 (for tracing)

### 🎯 Compatibility

- **Python**: 3.9, 3.10, 3.11, 3.12
- **Operating Systems**: Windows, macOS, Linux
- **LangChain**: Compatible with latest LangChain ecosystem
- **DeepAgents**: Inspired by and compatible with DeepAgents architecture

### 📝 Documentation

- Comprehensive README with quick start guide
- QUICKSTART guide for new users
- API documentation in docstrings
- Example code for common use cases
- Testing documentation

### 🔒 Security

- No hardcoded credentials
- Environment variable support via python-dotenv
- Optional tracing (disabled by default)
- Safe file operations with path validation

### 🏗️ Architecture

- Built on LangGraph for robust agent orchestration
- Modular design for easy extension
- Clean separation of concerns
- Type-safe interfaces
- Production-ready error handling

### 🙏 Acknowledgments

- Built on LangChain and LangGraph
- Inspired by DeepAgents architecture
- Developed by SagaraGlobal

---

## [Unreleased]

### Planned Features
- Additional workflow patterns
- More built-in tools
- Enhanced memory systems
- Performance optimizations
- Extended documentation

---

**For detailed usage instructions, see [README.md](README.md)**

**Developed by SagaraGlobal** - https://sagaraglobal.com
