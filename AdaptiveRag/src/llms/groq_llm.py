"""
Groq LLM initialization (free-tier, fast inference for open models like
Llama 3.3 / Llama 3.1). Groq is inference-only -- it does not provide an
embeddings endpoint, so embeddings are handled separately by a local
HuggingFace model (see src/rag/retriever_setup.py).
"""
from functools import lru_cache

from langchain_groq import ChatGroq

from src.config.settings import settings


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.0) -> ChatGroq:
    """Returns a cached ChatGroq instance."""
    return ChatGroq(
        model=settings.GROQ_MODEL,
        temperature=temperature,
        api_key=settings.GROQ_API_KEY,
    )
