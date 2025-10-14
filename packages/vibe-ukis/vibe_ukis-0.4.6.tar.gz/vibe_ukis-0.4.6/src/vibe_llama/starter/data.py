import os
from typing import Literal
from pathlib import Path

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

# Get the package root directory (where documentation folder is)
PACKAGE_ROOT = Path(__file__).parent.parent.parent.parent

services: dict[LibraryName, str] = {
    "LlamaIndex": str(PACKAGE_ROOT / "documentation" / "llamaindex.md"),
    "llama-index-workflows": str(PACKAGE_ROOT / "documentation" / "llama-index-workflows.md"),
    "Chainlit": str(PACKAGE_ROOT / "documentation" / "chainlit.md"),
}
