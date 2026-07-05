"""
FastAPI application entry point for the Adaptive RAG backend.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth_routes import router as auth_router
from src.api.routes import router as rag_router
from src.core.logger import get_logger
from src.db.mongo_client import ping

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Adaptive RAG backend...")
    if await ping():
        logger.info("MongoDB connection OK.")
    else:
        logger.warning("MongoDB unreachable at startup -- will use in-memory chat history fallback.")
    yield
    logger.info("Shutting down Adaptive RAG backend.")


app = FastAPI(
    title="Adaptive RAG - Agentic AI Chatbot",
    description="An intelligent RAG system with adaptive query routing.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(rag_router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "Adaptive RAG - Agentic AI Chatbot"}


@app.get("/health")
async def health():
    mongo_ok = await ping()
    return {"status": "ok", "mongodb": mongo_ok}
