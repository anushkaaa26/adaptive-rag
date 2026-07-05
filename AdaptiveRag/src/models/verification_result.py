"""
Structured output model for verifying a generated answer against source context.
"""
from pydantic import BaseModel, Field


class VerificationResult(BaseModel):
    """Result of checking whether a generated answer is grounded in context."""

    is_grounded: bool = Field(description="Whether the answer is supported by the given context.")
    reasoning: str = Field(description="Brief explanation for the grounding decision.")
