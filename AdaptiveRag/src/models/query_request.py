"""
Request schema for the /rag/query endpoint.
"""
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., description="User's question or query", min_length=1)
    session_id: str = Field(..., description="Unique session identifier for conversation tracking")
