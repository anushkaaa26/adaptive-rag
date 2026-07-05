"""
Graph state definition shared across all LangGraph nodes.
"""
from typing import List, Optional, TypedDict


class GraphState(TypedDict, total=False):
    """State object threaded through the LangGraph workflow."""

    query: str                      # Original user query
    rewritten_query: Optional[str]  # Query after rewrite step
    session_id: str                 # Conversation session identifier
    route: Optional[str]            # "index" | "general" | "search"
    documents: List[str]            # Retrieved document chunks (as text)
    relevant_documents: List[str]   # Documents that passed the relevance grade
    web_results: List[str]          # Web search results
    generation: Optional[str]       # Final generated answer
    retries: int                    # Number of rewrite/retry cycles so far
    is_grounded: Optional[bool]     # Whether generation was verified against context
