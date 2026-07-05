"""
LangGraph workflow construction: wires together the query analysis, retrieval,
grading, rewrite, web search, general LLM, and generation nodes into the
Adaptive RAG state graph.
"""
from functools import lru_cache

from langgraph.graph import END, StateGraph

from src.models.state import GraphState
from src.rag.nodes import (
    generate_node,
    general_llm_node,
    grade_node,
    query_analysis,
    retriever_node,
    rewrite_node,
    verify_node,
    web_search_node,
)
from src.tools.graph_tools import grade_decision, route_decision, verify_decision
from src.core.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("query_analysis", query_analysis)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("grade", grade_node)
    workflow.add_node("rewrite", rewrite_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("general_llm", general_llm_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("verify", verify_node)

    workflow.set_entry_point("query_analysis")

    workflow.add_conditional_edges(
        "query_analysis",
        route_decision,
        {
            "index": "retriever",
            "general": "general_llm",
            "search": "web_search",
        },
    )

    workflow.add_edge("retriever", "grade")

    workflow.add_conditional_edges(
        "grade",
        grade_decision,
        {
            "generate": "generate",
            "rewrite": "rewrite",
            "web_search": "web_search",
        },
    )

    workflow.add_edge("rewrite", "retriever")
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("general_llm", END)
    workflow.add_edge("generate", "verify")

    workflow.add_conditional_edges(
        "verify",
        verify_decision,
        {
            "rewrite": "rewrite",
            "end": END,
        },
    )

    compiled = workflow.compile()
    logger.info("LangGraph Adaptive RAG workflow compiled.")
    return compiled
