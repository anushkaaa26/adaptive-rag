"""
Application settings loaded from environment variables (.env file).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenAI (optional -- only needed if you switch the LLM back to OpenAI)
    OPENAI_API_KEY: str = ""

    # Groq (free-tier LLM inference)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Local embeddings (free, no API key needed)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Tavily web search
    TAVILY_API_KEY: str = ""

    # Qdrant vector database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_CODE_COLLECTION: str = "code_documents"
    QDRANT_DOCS_COLLECTION: str = "documents"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "adaptive_rag"

    # Document processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150

    # LLM
    OPENAI_MODEL: str = "gpt-4o"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
