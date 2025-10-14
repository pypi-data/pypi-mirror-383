# vibe-ukis

**vibe-ukis** is a comprehensive toolkit for building AI-powered applications with ease. Built on top of LlamaIndex and Chainlit, vibe-ukis provides powerful workflow orchestration and intelligent document processing capabilities.

## Features

- **LlamaIndex Integration**: Leverage the full power of LlamaIndex for building intelligent applications
- **Chainlit UI**: Beautiful, interactive user interfaces for your AI applications
- **LlamaIndex Workflows**: Advanced workflow orchestration for complex AI pipelines
- **Claude Code Subagents**: Intelligent coding assistants powered by Claude
- **Quick Starter**: Get up and running in seconds with pre-configured templates

## Installation

**Quick Install**

Install **vibe-ukis** using `uv`:

```bash
uvx vibe-ukis@latest --help
```

Or with `pip`:

```bash
pip install vibe-ukis
```

**Development Setup**

Clone the repository:

```bash
git clone https://github.com/UkisAI/VibeUkis.git
cd vibe-ukis
```

Build and install:

```bash
python -m build
```

Regular installation:

```bash
uv pip install dist/*.whl
```

Editable installation (for development):

```bash
# Create and activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# .venv\Scripts\activate  # On Windows

# Install in editable mode
pip install -e .
```

## Usage

**vibe-ukis** provides a powerful CLI with several commands to help you build AI applications quickly.

### starter

The `starter` command is your quick-start solution for building AI applications with vibe-ukis. It sets up a complete project with all necessary configurations for LlamaIndex, Chainlit, and LlamaIndex workflows integration.

**Features:**
- Interactive terminal UI for easy setup
- Pre-configured templates for common use cases
- Integrated with Claude Code for intelligent development
- Support for multiple coding agents (Cursor, GitHub Copilot, Claude Code)

**Example usage:**

```bash
vibe-ukis starter                    # Launch interactive setup
vibe-ukis starter -a 'Claude Code'   # Quick start with Claude Code
vibe-ukis starter -v                 # Verbose mode for detailed logging
vibe-ukis starter --mcp              # Launch MCP server at http://127.0.0.1:8000/mcp
```

**Flags:**
- `-v`/`--verbose`: Enable detailed logging
- `-w`/`--overwrite`: Overwrite existing files
- `-m`/`--mcp`: Launch MCP server for programmatic access
- `-a`/`--agent`: Specify coding agent (e.g., 'Claude Code', 'Cursor')
- `-s`/`--service`: Specify service to configure

## Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## License

This project is licensed under the [MIT License](./LICENSE).
