"""
Shared utility functions used across the RAG pipeline.
"""
import os
from typing import Any, Dict

import yaml


def load_prompts(path: str = None) -> Dict[str, Any]:
    """Loads the prompts.yaml file into a dict."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "config", "prompts.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_docs(docs) -> str:
    """Formats a list of LangChain Document objects (or strings) into a single context string."""
    parts = []
    for d in docs:
        content = getattr(d, "page_content", d)
        parts.append(str(content))
    return "\n\n---\n\n".join(parts)


def truncate(text: str, max_chars: int = 4000) -> str:
    return text if len(text) <= max_chars else text[:max_chars] + "..."
