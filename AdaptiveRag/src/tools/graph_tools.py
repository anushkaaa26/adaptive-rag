"""
Graph routing and decision helper functions used as conditional edges
in the LangGraph workflow.
"""
from src.models.state import GraphState
from src.core.logger import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 2


def route_decision(state: GraphState) -> str:
    """Reads the classified route and returns the corresponding node name."""
    route = state.get("route", "general")
    logger.info("Routing query to: %s", route)
    if route not in ("index", "general", "search"):
        return "general"
    return route


def grade_decision(state: GraphState) -> str:
    """
    After grading retrieved documents: if any are relevant, proceed to generate.
    Otherwise, rewrite the query and retry (up to MAX_RETRIES), then fall back
    to web search.
    """
    relevant = state.get("relevant_documents", [])
    retries = state.get("retries", 0)

    if relevant:
        return "generate"
    if retries < MAX_RETRIES:
        return "rewrite"
    logger.info("No relevant documents after %d retries -- falling back to web search.", retries)
    return "web_search"


def verify_decision(state: GraphState) -> str:
    """
    After verifying a generated answer against its context: if it's grounded,
    or if retries are exhausted, end the workflow. Otherwise loop back through
    rewrite/retrieval for another attempt.
    """
    if state.get("is_grounded", True):
        return "end"
    if state.get("retries", 0) < MAX_RETRIES:
        return "rewrite"
    return "end"
