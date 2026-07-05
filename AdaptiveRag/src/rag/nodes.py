"""
LangGraph node implementations for the Adaptive RAG workflow.
"""
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults

from src.config.settings import settings
from src.llms.groq_llm import get_llm
from src.models.grade import Grade
from src.models.route_identifier import RouteQuery
from src.models.state import GraphState
from src.models.verification_result import VerificationResult
from src.tools.graph_tools import MAX_RETRIES
from src.rag.retriever_setup import get_retriever
from src.tools.common_tools import format_docs, load_prompts
from src.core.logger import get_logger

logger = get_logger(__name__)
_prompts = load_prompts()


def query_analysis(state: GraphState) -> GraphState:
    """Classifies the incoming query into index / general / search."""
    llm = get_llm().with_structured_output(RouteQuery)
    prompt = ChatPromptTemplate.from_template(_prompts["classify_prompt"])
    chain = prompt | llm
    result: RouteQuery = chain.invoke({"query": state["query"]})
    state["route"] = result.route
    state.setdefault("retries", 0)
    return state


def retriever_node(state: GraphState) -> GraphState:
    """Retrieves relevant document chunks from the vector store."""
    query = state.get("rewritten_query") or state["query"]
    retriever = get_retriever()
    docs = retriever.invoke(query)
    state["documents"] = [d.page_content for d in docs]
    return state


def grade_node(state: GraphState) -> GraphState:
    """Grades each retrieved document for relevance to the question."""
    llm = get_llm().with_structured_output(Grade)
    prompt = ChatPromptTemplate.from_template(_prompts["grading_prompt"])
    chain = prompt | llm

    relevant: List[str] = []
    for doc in state.get("documents", []):
        result: Grade = chain.invoke({"document": doc, "question": state["query"]})
        if result.binary_score.strip().lower().startswith("y"):
            relevant.append(doc)

    state["relevant_documents"] = relevant
    return state


def rewrite_node(state: GraphState) -> GraphState:
    """Rewrites the query to improve retrieval quality, then increments retry count."""
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(_prompts["rewrite_prompt"])
    chain = prompt | llm
    result = chain.invoke({"query": state.get("rewritten_query") or state["query"]})
    state["rewritten_query"] = result.content if hasattr(result, "content") else str(result)
    state["retries"] = state.get("retries", 0) + 1
    return state


def web_search_node(state: GraphState) -> GraphState:
    """Performs a real-time web search via Tavily."""
    search = TavilySearchResults(k=4, tavily_api_key=settings.TAVILY_API_KEY)
    query = state.get("rewritten_query") or state["query"]
    results = search.invoke({"query": query})
    texts = [r.get("content", "") for r in results] if isinstance(results, list) else [str(results)]
    state["web_results"] = texts
    return state


def general_llm_node(state: GraphState) -> GraphState:
    """Answers directly from the LLM's general knowledge, no retrieval needed."""
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(_prompts["system_prompt"] + "\n\nQuestion: {query}")
    chain = prompt | llm
    result = chain.invoke({"query": state["query"]})
    state["generation"] = result.content if hasattr(result, "content") else str(result)
    return state


def generate_node(state: GraphState) -> GraphState:
    """Generates the final answer from retrieved context (documents or web results)."""
    context_items = state.get("relevant_documents") or state.get("web_results") or []
    context = format_docs(context_items)

    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(_prompts["generate_prompt"])
    chain = prompt | llm
    result = chain.invoke({"context": context, "question": state["query"]})
    state["generation"] = result.content if hasattr(result, "content") else str(result)
    return state


_VERIFY_PROMPT = (
    "Given the context and a generated answer, determine whether the answer is "
    "grounded in and supported by the context.\n\n"
    "Context:\n{context}\n\n"
    "Answer:\n{answer}"
)


def verify_node(state: GraphState) -> GraphState:
    """
    Checks whether the generated answer is actually supported by the retrieved
    context. If not, and retries remain, the state is left so the graph can
    loop back through rewrite/retrieval; otherwise a disclaimer is appended.
    """
    context_items = state.get("relevant_documents") or state.get("web_results") or []
    if not context_items:
        # Nothing to verify against (shouldn't normally happen on this path).
        state["is_grounded"] = True
        return state

    context = format_docs(context_items)
    llm = get_llm().with_structured_output(VerificationResult)
    prompt = ChatPromptTemplate.from_template(_VERIFY_PROMPT)
    chain = prompt | llm

    result: VerificationResult = chain.invoke(
        {"context": context, "answer": state.get("generation", "")}
    )
    state["is_grounded"] = result.is_grounded

    if not result.is_grounded:
        logger.info("Answer failed grounding check: %s", result.reasoning)
        if state.get("retries", 0) >= MAX_RETRIES:
            state["generation"] = (
                state.get("generation", "")
                + "\n\n_Note: this answer could not be fully verified against the "
                "retrieved context. Please double-check it._"
            )

    return state
