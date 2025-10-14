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
uv build
```

Regular installation:

```bash
uv pip install dist/*.whl
```

Editable installation (for development):

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Unix/macOS
# .venv\Scripts\activate  # On Windows

# Install in editable mode
uv pip install -e .
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

### docuflows

Build and edit intelligent document processing workflows with an interactive CLI agent. Powered by LlamaIndex workflows and Claude Code subagents.

**Setup**

Set your API keys as environment variables:

**MacOS/Linux:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export LLAMA_CLOUD_API_KEY="your-llama-cloud-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"  # Optional
```

**Windows (PowerShell):**
```powershell
$Env:OPENAI_API_KEY="your-openai-api-key"
$Env:LLAMA_CLOUD_API_KEY="your-llama-cloud-api-key"
$Env:ANTHROPIC_API_KEY="your-anthropic-api-key"  # Optional
```

**Usage:**

```bash
vibe-ukis docuflows
```

**Features:**
- Interactive workflow creation and editing
- Claude Code subagents for intelligent assistance
- LlamaIndex workflows integration
- Slash commands for configuration:
  - `/configure` - Set up LlamaCloud project settings
  - `/model` - Choose your LLM (GPT-4.1, Claude models, etc.)
- Automatic generation of workflow code and documentation
- Outputs to `generated_workflows/` with `workflow.py` and `runbook.md`

> **Note:** The `starter` command can pre-configure docuflows settings for you.

### scaffold

Generate production-ready workflow examples for various AI use cases with a single command.

**Usage:**

```bash
vibe-ukis scaffold                                           # Interactive UI
vibe-ukis scaffold --use_case document_parsing              # Direct generation
vibe-ukis scaffold -u invoice_extraction -p examples/       # Custom path
```

**Flags:**
- `-u`/`--use_case`: Select use case template
- `-p`/`--path`: Specify output directory (defaults to `.vibe-ukis/scaffold`)

**What you get:**
- `workflow.py` - Complete workflow implementation
- `README.md` - Setup and usage instructions
- `pyproject.toml` - Project configuration with dependencies

**Available Use Cases:**
- Document parsing
- Invoice extraction
- RAG (Retrieval-Augmented Generation)
- Web scraping
- Human-in-the-loop workflows
- Basic workflow templates

## SDK

vibe-ukis provides a Python SDK for programmatic access to all features.

### Quick Start Example

```python
from vibe_llama.sdk import VibeLlamaStarter, VibeLlamaScaffold, VibeLlamaMCPClient

# Set up a new project with starter
starter = VibeLlamaStarter(
    agents=["Claude Code", "Cursor"],
    services=["LlamaIndex", "llama-index-workflows"],
)
await starter.write_instructions(verbose=True)

# Generate a workflow template
scaffolder = VibeLlamaScaffold()
await scaffolder.get_template(
    template_name="invoice_extraction",
    save_path="examples/invoice_extraction/",
)

# Use MCP client for documentation retrieval
client = VibeLlamaMCPClient()
result = await client.retrieve_docs(
    query="LlamaIndex workflows", top_k=5
)
```

### Available SDK Classes

**`VibeLlamaStarter`** - Programmatic project setup
```python
from vibe_llama.sdk import VibeLlamaStarter

starter = VibeLlamaStarter(agents=["Claude Code"], services=["LlamaIndex"])
await starter.write_instructions(verbose=True, max_retries=20)
```

**`VibeLlamaScaffold`** - Template generation
```python
from vibe_llama.sdk import VibeLlamaScaffold

scaffolder = VibeLlamaScaffold(colored_output=True)
await scaffolder.get_template("invoice_extraction", "examples/")
```

**`VibeLlamaMCPClient`** - MCP server interaction
```python
from vibe_llama.sdk import VibeLlamaMCPClient

client = VibeLlamaMCPClient()
await client.list_tools()
await client.retrieve_docs(query="Workflow patterns", top_k=3, parse_xml=True)
```

**`VibeLlamaDocsRetriever`** - Documentation search with BM25
```python
from vibe_llama.sdk import VibeLlamaDocsRetriever

retriever = VibeLlamaDocsRetriever()
await retriever.retrieve(query="LlamaIndex best practices", top_k=10)
```

## Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## License

This project is licensed under the [MIT License](./LICENSE).
