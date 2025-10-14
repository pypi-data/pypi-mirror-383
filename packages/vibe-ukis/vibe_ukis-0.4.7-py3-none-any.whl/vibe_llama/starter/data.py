import os
from typing import Literal
from pathlib import Path
from importlib.resources import files

from vibe_llama.constants import BASE_URL

agent_rules = {
    "Cursor": ".cursor/rules/cursor_instructions.mdc",
    "Claude Code": "CLAUDE.md",
    "Claude Code (Subagents)": ".claude/agents/",  # Directory for subagents
    "GitHub Copilot": ".github/copilot-instructions.md",
    "Windsurf": ".windsurf/rules/windsurf_instructions.md",
}

# Internal agents used by the system (not shown in UI)
_internal_agent_rules = {
    "vibe-llama docuflows": ".vibe-llama/rules/AGENTS.md",
}

# Combine for programmatic access
all_agent_rules = {**agent_rules, **_internal_agent_rules}

LibraryName = Literal[
    "LlamaIndex", "llama-index-workflows", "Chainlit"
]

# Use importlib.resources to locate documentation files
# This works both in development and when the package is installed
def _get_doc_path(filename: str) -> str:
    """Get the path to a documentation file, handling both dev and installed modes."""
    # Try installed package location first
    try:
        doc_path = files("vibe_llama").joinpath("documentation", filename)
        path_str = str(doc_path)
        if os.path.exists(path_str):
            return path_str
    except (TypeError, FileNotFoundError, AttributeError):
        pass

    # Fallback to development location (project root)
    package_root = Path(__file__).parent.parent.parent.parent
    dev_path = package_root / "documentation" / filename
    if dev_path.exists():
        return str(dev_path)

    # If neither exists, return the dev path (will be caught by error handling later)
    return str(dev_path)

services: dict[LibraryName, str] = {
    "LlamaIndex": _get_doc_path("llamaindex.md"),
    "llama-index-workflows": _get_doc_path("llama-index-workflows.md"),
    "Chainlit": _get_doc_path("chainlit.md"),
}
