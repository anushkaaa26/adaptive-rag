"""
Structured output model for query classification / routing.
"""
from typing import Literal

from pydantic import BaseModel, Field


class RouteQuery(BaseModel):
    """Routes a user query to the most relevant processing pipeline."""

    route: Literal["index", "general", "search"] = Field(
        description="Given a user query, choose to route it to 'index', 'general', or 'search'."
    )
