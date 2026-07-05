"""
Document processing and upload pipeline: loads PDF/TXT files, chunks them,
and indexes them into the Qdrant vector store.
"""
import os
import tempfile
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from src.config.settings import settings
from src.rag.retriever_setup import get_vectorstore
from src.core.logger import get_logger

logger = get_logger(__name__)

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
)


def _load_documents(file_path: str, filename: str) -> List[Document]:
    if filename.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif filename.lower().endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {filename}")
    return loader.load()


async def process_and_upload(file_bytes: bytes, filename: str, description: str) -> bool:
    """
    Saves the uploaded file to a temp path, loads + chunks it, tags each chunk
    with the given description as metadata, and indexes it into Qdrant.
    """
    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        raw_docs = _load_documents(tmp_path, filename)
        chunks = _SPLITTER.split_documents(raw_docs)

        for chunk in chunks:
            chunk.metadata.update({"source": filename, "description": description})

        if not chunks:
            logger.warning("No content extracted from %s", filename)
            return False

        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)
        logger.info("Indexed %d chunks from %s", len(chunks), filename)
        return True
    finally:
        os.remove(tmp_path)
