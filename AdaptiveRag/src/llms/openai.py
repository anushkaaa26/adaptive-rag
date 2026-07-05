"""
OpenAI ChatGPT-4o (or configured model) LLM initialization.
"""
from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.config.settings import settings


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Returns a cached ChatOpenAI instance."""
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,
    )
