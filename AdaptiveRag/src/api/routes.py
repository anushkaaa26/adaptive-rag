"""
RAG query and document upload API endpoints.
"""
from fastapi import APIRouter, File, Header, HTTPException, UploadFile

from src.memory.chat_history_mongo import MongoChatHistory
from src.models.query_request import QueryRequest
from src.rag.document_upload import process_and_upload
from src.rag.graph_builder import build_graph
from src.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/rag", tags=["rag"])

_chat_history = MongoChatHistory()

ALLOWED_EXTENSIONS = (".pdf", ".txt")


@router.post("/query")
async def query_endpoint(request: QueryRequest):
    """Processes a RAG query through the adaptive LangGraph workflow."""
    try:
        graph = build_graph()
        result_state = graph.invoke(
            {"query": request.query, "session_id": request.session_id, "retries": 0}
        )

        answer = result_state.get("generation", "I couldn't generate an answer.")

        await _chat_history.add_message(request.session_id, "human", request.query)
        await _chat_history.add_message(request.session_id, "ai", answer)

        return {"result": {"type": "ai", "content": answer}}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error processing query")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    x_description: str = Header(..., alias="X-Description"),
):
    """Uploads and indexes a PDF or TXT document into the vector store."""
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")
    if not x_description or not x_description.strip():
        raise HTTPException(status_code=400, detail="X-Description header is required.")

    try:
        file_bytes = await file.read()
        success = await process_and_upload(file_bytes, file.filename, x_description)
        return {"status": success}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error processing document upload")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Retrieves the full conversation history for a session."""
    history = await _chat_history.get_history(session_id)
    return {"session_id": session_id, "history": history}
