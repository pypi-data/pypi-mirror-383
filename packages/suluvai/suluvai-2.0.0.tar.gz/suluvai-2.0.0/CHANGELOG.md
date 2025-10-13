# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-12

### Added
- **Streaming Support**: Real-time token and event streaming
  - `stream_agent_events()` for comprehensive event streaming
  - `stream_tokens_only()` for simple token streaming
  - `StreamingCallback` for custom event handling
  - Support for async streaming with `astream_events`

- **Local File Storage**: Persistent file storage with multi-level folders
  - `LocalFileStorage` class for disk-based storage
  - Support for nested directory structures (unlimited depth)
  - File metadata tracking (size, timestamps, checksums)
  - Search functionality with glob patterns
  - Copy/move file operations
  - Directory tree visualization
  - Security validation to prevent path traversal

- **Enhanced Agent**: `create_enhanced_agent()` with advanced features
  - Configurable storage modes: local, virtual, or hybrid
  - Integration with streaming and storage
  - `EnhancedAgentConfig` for flexible configuration

- **Advanced Filesystem Tools**:
  - `create_directory()` - Create nested directories
  - `list_directories()` - List directory structure
  - `search_files()` - Search with glob patterns
  - `get_file_tree()` - Visual directory tree
  - `copy_file()` / `move_file()` - File operations

- **Comprehensive Examples**:
  - Basic streaming example
  - Local storage demo
  - Research agent with streaming
  - Advanced multi-level folder operations
  - Complete example with all features

- **Testing**:
  - Full test suite with pytest
  - Tests for storage, streaming, and agents
  - Mock fixtures for testing without API calls

- **Documentation**:
  - Complete package structure guide
  - Multiple requirements files for different use cases
  - Publishing instructions

### Changed
- Updated `filesystem_tools.py` to support multi-level paths
- Enhanced `__init__.py` with new exports
- Version bumped to 2.0.0

### Improved
- Better error handling in storage operations
- Security validation for file paths
- More descriptive tool documentation

## [1.0.0] - 2024-12-XX

### Added
- Initial release
- Basic agent creation with `create_zita_agent()`
- Sub-agent support
- Virtual filesystem (in-state)
- TODO list tools
- LangSmith tracing integration
- ReAct pattern implementation

### Features
- Sub-agents with specialized roles
- Virtual filesystem for large data
- TODO list for task planning
- Multi-turn conversations with state
- Production-ready implementation on LangGraph 0.6.10

---

## Future Plans

### [2.1.0] - Planned
- [ ] Memory/persistence layer for conversation history
- [ ] Support for binary files (images, PDFs)
- [ ] File compression for large storage
- [ ] Webhooks for streaming events
- [ ] Advanced caching strategies

### [3.0.0] - Planned
- [ ] Distributed agent execution
- [ ] Cloud storage backends (S3, Azure Blob)
- [ ] Vector database integration
- [ ] Multi-modal support (vision, audio)
- [ ] Agent marketplace/templates
