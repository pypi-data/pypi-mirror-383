"""
Subagent generation for Claude Code
"""
import os
from pathlib import Path
from typing import Optional


# Mapping of service names to subagent configurations
SUBAGENT_CONFIGS = {
    "LlamaIndex": {
        "name": "llamaindex-expert",
        "description": "Expert in LlamaIndex framework for building data-backed LLM applications. Use when building agentic workflows, RAG pipelines, multi-agent systems, query engines, and chat engines.",
        "tools": "Read, Write, Grep, Glob, Bash, Edit",
        "model": "sonnet",
    },
    "llama-index-workflows": {
        "name": "workflows-expert",
        "description": "Expert in building event-driven async-first workflows using llama-index-workflows. Use proactively when building deterministic workflows for document processing, invoice extraction, etc.",
        "tools": "Read, Write, Grep, Glob, Bash, Edit",
        "model": "sonnet",
    },
    "Chainlit": {
        "name": "chainlit-expert",
        "description": "Expert in Chainlit framework for building conversational AI interfaces. Use when creating chat UIs, interactive AI applications, and user-facing interfaces.",
        "tools": "Read, Write, Grep, Glob, Bash, Edit",
        "model": "sonnet",
    },
}


def create_subagent_file(
    agents_dir: str,
    service_name: str,
    documentation_content: str,
    overwrite: bool = False,
) -> Optional[str]:
    """
    Create a subagent markdown file based on service documentation.
    
    Args:
        agents_dir: Directory where subagent files will be created (.claude/agents/)
        service_name: Name of the service (LlamaIndex, llama-index-workflows, etc.)
        documentation_content: The documentation content to embed in the subagent
        overwrite: Whether to overwrite existing files
        
    Returns:
        Path to created file or None if skipped
    """
    if service_name not in SUBAGENT_CONFIGS:
        return None
    
    config = SUBAGENT_CONFIGS[service_name]
    
    # Create agents directory if it doesn't exist
    Path(agents_dir).mkdir(parents=True, exist_ok=True)
    
    # Create subagent file path
    subagent_file = os.path.join(agents_dir, f"{config['name']}.md")
    
    # Check if file exists and overwrite is False
    if not overwrite and Path(subagent_file).exists():
        return None
    
    # Create subagent content with frontmatter
    content = f"""---
name: {config['name']}
description: "{config['description']}"
model: {config['model']}
---

You are an expert in {service_name}. You have deep knowledge from the official documentation embedded below.

## Your Role

Provide expert guidance on {service_name} based on the documentation context. 

When users ask questions or need help with {service_name}, use this knowledge to:

1. Look at the information available bellow
2. Suggest to the user that you want to use the web search tool to fetch the relevant links to be able to get the latest documentation
3. After fetching the relevant information continue with the user's request

## Documentation Context

{documentation_content}

## Guidelines

Answer in the following way:

1. Look at the information available above
2. Suggest to the user that you want to use the web search tool to fetch the relevant links to be able to get the latest documentation
3. After fetching the relevant information continue with the user's request

- Always base your answers on the documentation above
- Explain the reasoning behind recommendations
- Ask clarifying questions if the user's requirements are unclear

"""
    
    # Write the subagent file
    with open(subagent_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    return subagent_file


def create_subagents_from_services(
    agents_dir: str,
    services_content: dict[str, str],
    overwrite: bool = False,
    verbose: bool = False,
) -> list[str]:
    """
    Create multiple subagent files from service documentation.
    
    Args:
        agents_dir: Directory for subagents (.claude/agents/)
        services_content: Dict mapping service names to their documentation content
        overwrite: Whether to overwrite existing files
        verbose: Whether to print verbose output
        
    Returns:
        List of created file paths
    """
    created_files = []
    
    for service_name, doc_content in services_content.items():
        file_path = create_subagent_file(
            agents_dir=agents_dir,
            service_name=service_name,
            documentation_content=doc_content,
            overwrite=overwrite,
        )
        if file_path:
            created_files.append(file_path)
            if verbose:
                print(f"Created subagent: {file_path}")
    
    return created_files

