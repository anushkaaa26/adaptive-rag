"""
Qdrant vector store and retriever setup.

Embeddings run locally via a HuggingFace sentence-transformers model (free,
no API key, no network calls at inference time) -- Groq itself doesn't
provide an embeddings endpoint.
"""
from functools import lru_cache

from langchain_community.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src.config.settings import settings
from src.core.logger import get_logger

logger = get_logger(__name__)

# all-MiniLM-L6-v2 produces 384-dim vectors. If you change EMBEDDING_MODEL,
# update this to match the new model's output dimension.
EMBEDDING_DIM = 384


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    logger.info("Loading local embedding model: %s", settings.EMBEDDING_MODEL)
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)


def ensure_collection(collection_name: str) -> None:
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        logger.info("Creating Qdrant collection '%s'", collection_name)
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def get_vectorstore(collection_name: str | None = None) -> Qdrant:
    collection_name = collection_name or settings.QDRANT_DOCS_COLLECTION
    ensure_collection(collection_name)
    return Qdrant(
        client=get_qdrant_client(),
        collection_name=collection_name,
        embeddings=get_embeddings(),
    )


def get_retriever(collection_name: str | None = None, k: int = 4):
    return get_vectorstore(collection_name).as_retriever(search_kwargs={"k": k})
