"""
Structured output model for the document relevance grading step.
"""
from pydantic import BaseModel, Field


class Grade(BaseModel):
    """Binary relevance score for a retrieved document."""

    binary_score: str = Field(
        description="Whether the document is relevant to the question: 'yes' or 'no'."
    )
